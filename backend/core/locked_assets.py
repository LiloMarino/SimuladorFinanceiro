"""A regra de saída de cada tipo de patrimônio travado da profissão: o texto da linha da carteira e quanto do saldo vira caixa na troca de profissão."""

from dataclasses import dataclass
from decimal import Decimal

from backend.core.entrepreneur import SALE_PROCEEDS_RATE
from backend.core.enum import LockedAssetKind


@dataclass(frozen=True)
class LockedExit:
    """Como um tipo de patrimônio travado vira caixa."""

    # O texto da regra, mostrado na linha do patrimônio
    rule: str
    # A fração do saldo que cai no caixa quando o jogador troca de profissão
    switch_rate: Decimal


LOCKED_EXITS: dict[LockedAssetKind, LockedExit] = {
    LockedAssetKind.FGTS: LockedExit(
        rule="Sai só na demissão sem justa causa, com a multa de 40% sobre o saldo.",
        switch_rate=Decimal(1),
    ),
    LockedAssetKind.COMPANY_CAPITAL: LockedExit(
        rule="Só vira caixa vendendo uma parte, com desconto de 20%.",
        switch_rate=SALE_PROCEEDS_RATE,
    ),
}
