"""A regra de saída de cada tipo de patrimônio travado da profissão: o texto da linha da carteira e quanto do saldo vira caixa na troca de profissão."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.clt import cents
from backend.core.entrepreneur import SALE_PROCEEDS_RATE
from backend.core.enum import LockedAssetKind
from backend.core.pension import months_in_plan, redeem_net

# O que o saldo `value` deixa no caixa em `day`, dado desde quando está travado (`since`, nulo quando o tipo não conta tempo)
Payout = Callable[[Decimal, date | None, date], Decimal]


def fixed_share(rate: Decimal) -> Payout:
    """A saída que entrega a fração `rate` do saldo, em qualquer dia."""
    return lambda value, since, day: cents(value * rate)


def pension_payout(value: Decimal, since: date | None, day: date) -> Decimal:
    """O resgate do saldo inteiro da previdência: o IR regressivo da faixa do tempo no plano."""
    months = 0 if since is None else months_in_plan(since, day)
    return redeem_net(value, months)


@dataclass(frozen=True)
class LockedExit:
    """Como um tipo de patrimônio travado vira caixa."""

    # O texto da regra, mostrado na linha do patrimônio
    rule: str
    # O que o saldo deixa no caixa quando o jogador troca de profissão
    payout: Payout


LOCKED_EXITS: dict[LockedAssetKind, LockedExit] = {
    LockedAssetKind.FGTS: LockedExit(
        rule="Sai só na demissão sem justa causa, com a multa de 40% sobre o saldo.",
        payout=fixed_share(Decimal(1)),
    ),
    LockedAssetKind.COMPANY_CAPITAL: LockedExit(
        rule="Só vira caixa vendendo uma parte, com desconto de 20%.",
        payout=fixed_share(SALE_PROCEEDS_RATE),
    ),
    LockedAssetKind.PENSION: LockedExit(
        rule="Resgatar paga o IR regressivo pelo tempo no plano (35% a 10%).",
        payout=pension_payout,
    ),
}
