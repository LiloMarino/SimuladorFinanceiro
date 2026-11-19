from collections.abc import Callable
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING, Literal

from backend.core import repository
from backend.core.dto.fund import FundComanagerDTO, FundComanagerEventDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import FundComanagerStatus
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import next_month_turn
from backend.features.funds.fees import CENT

if TYPE_CHECKING:
    from backend.features.funds.fund_book import Fund

# Co-gestores por gestora, contando os convites pendentes
MAX_COMANAGERS = 3

# Dias de validade do convite: ele cai ao fechar o pregão do sétimo dia depois do envio
INVITE_DAYS = 7


def operators_of(fund: "Fund") -> list[int]:
    """Quem opera a carteira da gestora: o gestor principal e os co-gestores ativos."""
    return [
        fund.terms.manager_user_id,
        *(c.user_id for c in fund.comanagers if c.status is FundComanagerStatus.ACTIVE),
    ]


def manager_share(fund: "Fund") -> Decimal:
    """A parte das taxas do principal: o que sobra das partes em vigor dos co-gestores."""
    return Decimal(1) - sum((c.share for c in fund.comanagers), Decimal(0))


def split_fee(fund: "Fund", fee: Decimal) -> list[tuple[int, Decimal]]:
    """A taxa dividida entre o principal e os co-gestores, a soma fechando no centavo.

    Cada co-gestor recebe a parte dele arredondada para baixo ao centavo, como as demais taxas; o principal fica com o resto.
    """
    paid = [
        (c.user_id, (fee * c.share).quantize(CENT, ROUND_DOWN))
        for c in fund.comanagers
        if c.share > 0
    ]
    manager = fee - sum((amount for _, amount in paid), Decimal(0))
    return [(fund.terms.manager_user_id, manager), *paid]


def heir_of(fund: "Fund") -> FundComanagerDTO | None:
    """O co-gestor que assume quando o principal vira presidente: a maior parte, e o mais antigo no empate."""
    active = [c for c in fund.comanagers if c.status is FundComanagerStatus.ACTIVE]
    if not active:
        return None
    return min(active, key=lambda c: (-c.share, c.since or date.max, c.user_id))


def expires_on(comanager: FundComanagerDTO) -> date:
    """O último dia do convite pendente."""
    return comanager.invited_on + timedelta(days=INVITE_DAYS)


class FundComanagers:
    """Os co-gestores da gestora: convite, aceite, saída, partes das taxas e divisão delas.

    A parte do principal não é guardada: é 1 menos a soma das partes dos co-gestores. A soma
    das partes que vão valer (a agendada, se houver, senão a de hoje) fica abaixo de 100%, e por
    isso o convite pendente já reserva a dele.
    """

    def __init__(self, participants: Callable[[], list[UserDTO]]) -> None:
        self._participants = participants

    def load(self, fund_id: int) -> list[FundComanagerDTO]:
        return repository.fund_comanager.of_fund(fund_id)

    def _find(self, fund: "Fund", user_id: int) -> FundComanagerDTO | None:
        return next((c for c in fund.comanagers if c.user_id == user_id), None)

    def _get(self, fund: "Fund", user_id: int) -> FundComanagerDTO:
        comanager = self._find(fund, user_id)
        if comanager is None:
            raise NotFoundError("Esse jogador não é co-gestor da gestora")
        return comanager

    def _check_sum(self, fund: "Fund", user_id: int, share: Decimal) -> None:
        others = sum(
            (c.future_share for c in fund.comanagers if c.user_id != user_id),
            Decimal(0),
        )
        if others + share >= 1:
            raise UnprocessableEntityError(
                "As partes dos co-gestores precisam deixar parte para o gestor principal"
            )

    def _put(self, fund: "Fund", comanager: FundComanagerDTO) -> None:
        if self._find(fund, comanager.user_id) is None:
            fund.comanagers.append(comanager)
        else:
            fund.comanagers = [
                comanager if c.user_id == comanager.user_id else c
                for c in fund.comanagers
            ]
        repository.fund_comanager.save(fund.terms.id, comanager)

    def drop(self, fund: "Fund", user_id: int) -> None:
        """Tira a linha do co-gestor, sem registrar saída."""
        fund.comanagers = [c for c in fund.comanagers if c.user_id != user_id]
        repository.fund_comanager.delete(fund.terms.id, user_id)

    def _record(
        self,
        fund: "Fund",
        user_id: int,
        kind: Literal["joined", "left"],
        day: date,
        share: Decimal | None = None,
    ) -> None:
        repository.fund_comanager.record_event(
            fund.terms.id,
            FundComanagerEventDTO(user_id=user_id, kind=kind, day=day, share=share),
        )

    def invite(
        self, fund: "Fund", nickname: str, share: Decimal, today: date
    ) -> FundComanagerDTO:
        """O principal convida um jogador; o convite já reserva a parte e vale por sete dias."""
        guest = next(
            (
                u
                for u in self._participants()
                if u.nickname == nickname and not u.is_bot
            ),
            None,
        )
        if guest is None:
            raise UnprocessableEntityError("O convidado precisa ser um jogador da sala")
        if guest.id == fund.terms.manager_user_id:
            raise UnprocessableEntityError("O convidado já é o gestor")
        if self._find(fund, guest.id) is not None:
            raise ConflictError("Esse jogador já é co-gestor ou tem convite pendente")
        if len(fund.comanagers) >= MAX_COMANAGERS:
            raise ConflictError(
                f"A gestora aceita até {MAX_COMANAGERS} co-gestores, contando os convites"
            )
        self._check_sum(fund, guest.id, share)
        comanager = FundComanagerDTO(
            user_id=guest.id,
            status=FundComanagerStatus.INVITED,
            share=Decimal(0),
            pending_share=share,
            pending_from=None,
            invited_on=today,
            since=None,
        )
        self._put(fund, comanager)
        return comanager

    def answer(
        self, fund: "Fund", user: UserDTO, accept: bool, today: date
    ) -> FundComanagerDTO:
        """O convidado aceita (a parte vale nas taxas do mês seguinte) ou recusa o convite."""
        comanager = self._get(fund, user.id)
        if comanager.status is not FundComanagerStatus.INVITED:
            raise ConflictError("Não há convite esperando resposta")
        if not accept:
            self.drop(fund, user.id)
            return comanager
        accepted = comanager.model_copy(
            update={
                "status": FundComanagerStatus.ACTIVE,
                "since": today,
                "pending_from": next_month_turn(today),
            }
        )
        self._put(fund, accepted)
        self._record(fund, user.id, "joined", today, accepted.future_share)
        return accepted

    def change_share(
        self, fund: "Fund", user_id: int, share: Decimal, today: date
    ) -> FundComanagerDTO:
        """A parte nova vale nas taxas do mês seguinte; pedir a parte de hoje desfaz o pedido."""
        comanager = self._get(fund, user_id)
        self._check_sum(fund, user_id, share)
        if comanager.status is FundComanagerStatus.INVITED:
            changed = comanager.model_copy(update={"pending_share": share})
        elif share == comanager.share:
            changed = comanager.model_copy(
                update={"pending_share": None, "pending_from": None}
            )
        else:
            changed = comanager.model_copy(
                update={"pending_share": share, "pending_from": next_month_turn(today)}
            )
        self._put(fund, changed)
        return changed

    def remove(self, fund: "Fund", user_id: int, today: date) -> FundComanagerDTO:
        """O principal tira o co-gestor ou retira o convite; o acesso acaba na hora."""
        comanager = self._get(fund, user_id)
        self.drop(fund, user_id)
        if comanager.status is FundComanagerStatus.ACTIVE:
            self._record(fund, user_id, "left", today)
        return comanager

    def leave(self, fund: "Fund", user: UserDTO, today: date) -> None:
        """O co-gestor deixa a gestão; o acesso acaba na hora."""
        comanager = self._get(fund, user.id)
        if comanager.status is not FundComanagerStatus.ACTIVE:
            raise ConflictError("Só o co-gestor ativo sai da gestão")
        self.remove(fund, user.id, today)

    def expire_invites(self, fund: "Fund", today: date) -> list[FundComanagerDTO]:
        """O convite sem resposta cai ao fim do último dia e devolve a parte reservada."""
        expired = [
            c
            for c in fund.comanagers
            if c.status is FundComanagerStatus.INVITED and today >= expires_on(c)
        ]
        for comanager in expired:
            self.drop(fund, comanager.user_id)
        return expired

    def apply_pending(self, fund: "Fund", today: date) -> None:
        """As partes agendadas que chegaram ao dia passam a valer nas taxas."""
        for comanager in fund.comanagers:
            if (
                comanager.status is not FundComanagerStatus.ACTIVE
                or comanager.pending_share is None
                or comanager.pending_from is None
                or comanager.pending_from > today
            ):
                continue
            self._put(
                fund,
                comanager.model_copy(
                    update={
                        "share": comanager.pending_share,
                        "pending_share": None,
                        "pending_from": None,
                    }
                ),
            )

    def succeed(self, fund: "Fund", heir: FundComanagerDTO, today: date) -> None:
        """O herdeiro vira o principal e o gestor que sai deixa a gestão.

        A linha do herdeiro some e a parte dele se soma à do principal, porque a parte do
        principal é o que sobra das partes dos co-gestores. Os demais mantêm as partes.
        """
        self._record(fund, fund.terms.manager_user_id, "left", today)
        self.drop(fund, heir.user_id)

    def restore(self, fund: "Fund", user_id: int, share: Decimal, today: date) -> bool:
        """O herdeiro que deixa de ser principal volta a co-gestor com a parte de antes da posse.

        Volta só se a lista tem vaga e a soma das partes ainda deixa parte ao principal; devolve
        se voltou.
        """
        others = sum((c.future_share for c in fund.comanagers), Decimal(0))
        if len(fund.comanagers) >= MAX_COMANAGERS or others + share >= 1:
            return False
        self._put(
            fund,
            FundComanagerDTO(
                user_id=user_id,
                status=FundComanagerStatus.ACTIVE,
                share=share,
                pending_share=None,
                pending_from=None,
                invited_on=today,
                since=today,
            ),
        )
        self._record(fund, user_id, "joined", today, share)
        return True
