from datetime import date, timedelta
from decimal import ROUND_FLOOR, Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dto.fund import FundDirectedIssuanceDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import FundComanagerStatus, FundDirectedIssuanceStatus
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.funds.fees import CENT
from backend.features.funds.fund_comanagers import INVITE_DAYS

if TYPE_CHECKING:
    from backend.features.funds.fund_book import Fund


def directed_price(nav: Decimal, ranking: Decimal) -> Decimal:
    """O preço da cota na emissão dirigida: o maior entre o PL por cota e o preço de ranking, ao centavo.

    Quem compra não entra abaixo do que o mercado paga pela cota.
    """
    return max(nav, ranking).quantize(CENT)


def cap_room(held: Decimal, total: Decimal, cap: Decimal) -> Decimal:
    """As cotas novas que quem tem `held` das `total` ainda compra sem passar de `cap` do total.

    A compra de `n` cotas novas leva a parte a `(held + n) / (total + n)`; o maior `n` que
    fica em `cap` é `(cap x total - held) / (1 - cap)`, para baixo. Passado do teto, zero; com
    teto de 100% a compra não tem limite.
    """
    if cap >= 1:
        return Decimal("Infinity")
    room = ((cap * total - held) / (1 - cap)).to_integral_value(rounding=ROUND_FLOOR)
    return max(room, Decimal(0))


def expires_on(offer: FundDirectedIssuanceDTO) -> date:
    """O último dia da oferta pendente."""
    return offer.offered_on + timedelta(days=INVITE_DAYS)


class FundDirectedIssuances:
    """A oferta de cotas novas do principal a um co-gestor: oferecer, aceitar ou recusar, cancelar e vencer.

    A oferta guarda só a quantidade; o preço e os limites nascem na aceitação, com o estado
    da gestora de então. A gestora tem no máximo uma oferta pendente.
    """

    def load(self, fund_id: int) -> FundDirectedIssuanceDTO | None:
        return repository.fund_directed_issuance.pending_of_fund(fund_id)

    def offer(
        self, fund: "Fund", buyer_user_id: int, quotas: Decimal, today: date
    ) -> FundDirectedIssuanceDTO:
        """O principal oferece `quotas` cotas novas a um co-gestor ativo; a oferta vale por sete dias."""
        if fund.directed is not None:
            raise ConflictError(
                "A gestora já tem uma oferta de cotas esperando resposta"
            )
        buyer = next((c for c in fund.comanagers if c.user_id == buyer_user_id), None)
        if buyer is None or buyer.status is not FundComanagerStatus.ACTIVE:
            raise UnprocessableEntityError("O comprador precisa ser co-gestor ativo")
        fund.directed = repository.fund_directed_issuance.create(
            fund.terms.id,
            buyer_user_id,
            quotas,
            today,
            FundDirectedIssuanceStatus.OFFERED,
        )
        return fund.directed

    def record_settled(
        self,
        fund: "Fund",
        buyer_user_id: int,
        quotas: Decimal,
        price: Decimal,
        today: date,
    ) -> FundDirectedIssuanceDTO:
        """A emissão que o principal faz para si nasce já liquidada."""
        return repository.fund_directed_issuance.create(
            fund.terms.id,
            buyer_user_id,
            quotas,
            today,
            FundDirectedIssuanceStatus.ACCEPTED,
            price,
            today,
        )

    def pending_for(self, fund: "Fund", user: UserDTO) -> FundDirectedIssuanceDTO:
        """A oferta que espera a resposta de `user`."""
        offer = fund.directed
        if offer is None or offer.buyer_user_id != user.id:
            raise NotFoundError("Não há oferta de cotas esperando a sua resposta")
        return offer

    def decline(self, fund: "Fund", user: UserDTO) -> FundDirectedIssuanceDTO:
        """O co-gestor recusa: a oferta se encerra sem liquidar."""
        offer = self.pending_for(fund, user)
        self._close(fund, FundDirectedIssuanceStatus.DECLINED)
        return offer

    def settle(self, fund: "Fund", price: Decimal, today: date) -> None:
        """A oferta aceita fica liquidada ao preço e no dia da liquidação."""
        self._close(fund, FundDirectedIssuanceStatus.ACCEPTED, price, today)

    def cancel(self, fund: "Fund") -> FundDirectedIssuanceDTO | None:
        """A oferta pendente cai: o principal a cancelou ou o comprador deixou de ser co-gestor."""
        return self._close(fund, FundDirectedIssuanceStatus.CANCELLED)

    def cancel_of(self, fund: "Fund", user_id: int) -> FundDirectedIssuanceDTO | None:
        """Cancela a oferta pendente destinada a `user_id`, se houver."""
        if fund.directed is None or fund.directed.buyer_user_id != user_id:
            return None
        return self.cancel(fund)

    def expire(self, fund: "Fund", today: date) -> FundDirectedIssuanceDTO | None:
        """A oferta sem resposta cai ao fim do último dia dela."""
        if fund.directed is None or today < expires_on(fund.directed):
            return None
        return self._close(fund, FundDirectedIssuanceStatus.EXPIRED)

    def _close(
        self,
        fund: "Fund",
        status: FundDirectedIssuanceStatus,
        price: Decimal | None = None,
        settled_on: date | None = None,
    ) -> FundDirectedIssuanceDTO | None:
        offer = fund.directed
        if offer is None:
            return None
        repository.fund_directed_issuance.close(offer.id, status, price, settled_on)
        fund.directed = None
        return offer
