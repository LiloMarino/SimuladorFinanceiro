from decimal import ROUND_FLOOR, Decimal

from backend.core.dto.fund import (
    FundBuybackPreviewDTO,
    FundDirectedIssuancePreviewDTO,
    FundIssuancePreviewDTO,
    FundIssuanceSubscriptionPreviewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.funds.fund_book import ISSUANCE_LIMIT, Fund, FundBook
from backend.features.funds.fund_details import control_quotas
from backend.features.simulation.simulation_engine import SimulationEngine


def _share(quotas: Decimal, total: Decimal) -> Decimal:
    return quotas / total if total > 0 else Decimal(0)


def _keeps_control(quotas: Decimal, total: Decimal) -> bool:
    """Mais da metade das cotas em circulação governa a gestora."""
    return quotas >= control_quotas(total)


class FundPreviewBuilder:
    """As contas dos diálogos de emissão e de recompra, feitas no backend com o estado vivo da
    gestora: o front só mostra os números."""

    def __init__(
        self, book: FundBook, engine: SimulationEngine, manager: UserDTO
    ) -> None:
        self._book = book
        self._engine = engine
        self._manager = manager

    def issuance(self, fund: Fund, quotas: Decimal) -> FundIssuancePreviewDTO:
        """Uma emissão de `quotas` cotas ao PL por cota de hoje: o caixa que entra e o controle do gestor."""
        nav = self._book.nav_of(fund)
        if nav is None:
            raise ConflictError("A gestora ainda não tem PL por cota")
        total = fund.account.quotas
        mine = self._book.quotas_of(fund, self._manager)
        total_after = total + quotas
        rights = (quotas * mine / total).to_integral_value(rounding=ROUND_FLOOR)
        raised = nav * quotas
        return FundIssuancePreviewDTO(
            quotas=quotas,
            price=nav,
            raised=raised,
            commission=self._engine.offer_commission_on(raised),
            total_after=total_after,
            limit=total * ISSUANCE_LIMIT,
            share_now=_share(mine, total),
            share_if_skip=_share(mine, total_after),
            keeps_control_if_skip=_keeps_control(mine, total_after),
            share_if_buy=_share(mine + rights, total_after),
            keeps_control_if_buy=_keeps_control(mine + rights, total_after),
            manager_rights=rights,
            manager_cost=nav * rights,
        )

    def directed(self, fund: Fund, quotas: Decimal) -> FundDirectedIssuancePreviewDTO:
        """Uma emissão dirigida de `quotas` cotas comprada por quem consulta: preço, custo, destino do dinheiro e participações."""
        nav, ranking, price = self._book.directed_terms(fund)
        total = fund.account.quotas
        total_after = total + quotas
        cost = price * quotas
        cash = self._engine.get_cash(self._manager.client_id)
        fund_cash = max(self._engine.get_cash(fund.account.client_id), Decimal(0))
        payable = fund.terms.fee_payable
        to_payable = min(payable, fund_cash + cost) - min(payable, fund_cash)
        room = self._book.directed_room(fund)
        mine = self._book.quotas_of(fund, self._manager)
        operators = self._book.operators_quotas(fund)
        # Se quem consulta é operador, as cotas novas entram na soma dele; senão só nas dele
        operators_after = operators + (
            quotas if self._manager.id in self._book.operators(fund) else Decimal(0)
        )
        return FundDirectedIssuancePreviewDTO(
            quotas=quotas,
            nav=nav,
            ranking_price=ranking,
            price=price,
            cost=cost,
            buyer_cash=cash,
            cash_enough=cash >= cost,
            to_payable=to_payable,
            to_cash=cost - to_payable,
            room=room if room.is_finite() else None,
            manager_cap=self._book.manager_cap,
            total_after=total_after,
            nav_after=(nav * total + cost) / total_after,
            my_quotas_after=mine + quotas,
            my_share_now=_share(mine, total),
            my_share_after=_share(mine + quotas, total_after),
            operators_share_now=_share(operators, total),
            operators_share_after=_share(operators_after, total_after),
        )

    def subscription(
        self, fund: Fund, viewer: UserDTO, quotas: Decimal
    ) -> FundIssuanceSubscriptionPreviewDTO:
        """Comprar `quotas` da preferência: o custo, o caixa e a parte do jogador depois da compra."""
        issuance = fund.issuance
        if issuance is None:
            raise ConflictError("A gestora não tem emissão aberta")
        right = fund.issuance_rights.get(viewer.id)
        left = right.rights - right.bought if right else Decimal(0)
        cost = issuance.price * quotas
        mine = self._book.quotas_of(fund, viewer)
        return FundIssuanceSubscriptionPreviewDTO(
            quotas=quotas,
            price=issuance.price,
            cost=cost,
            cash_enough=self._engine.get_cash(viewer.client_id) >= cost,
            my_quotas_after=mine + quotas,
            my_share_after=_share(mine + quotas, fund.account.quotas + quotas),
            rights_left_after=max(Decimal(0), left - quotas),
        )

    def buyback(
        self, fund: Fund, quantity: Decimal, max_price: Decimal
    ) -> FundBuybackPreviewDTO:
        """Uma recompra de `quantity` cotas a até `max_price`: o custo do ágio, o caixa e o PL por cota que fica."""
        nav = self._book.nav_of(fund)
        if nav is None:
            raise ConflictError("A gestora ainda não tem PL por cota")
        total = fund.account.quotas
        cost = max_price * quantity
        cash = self._engine.get_cash(fund.account.client_id)
        total_after = total - quantity
        mine = self._book.quotas_of(fund, self._manager)
        return FundBuybackPreviewDTO(
            quantity=quantity,
            max_price=max_price,
            nav=nav,
            premium=max_price / nav - 1,
            cost=cost,
            premium_cost=max(Decimal(0), quantity * (max_price - nav)),
            cash_after=cash - cost,
            cash_enough=cash >= cost,
            nav_after=(nav * total - cost) / total_after
            if total_after > 0
            else Decimal(0),
            total_after=total_after,
            share_now=_share(mine, total),
            share_after=_share(mine, total_after),
            keeps_control_after=_keeps_control(mine, total_after),
        )
