from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import RateIndexType, StrategyGroup
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.strategy.context import StrategyContext

CENT = Decimal("0.01")
# Abaixo disto o caixa parado não vale uma aplicação
MIN_INVESTMENT = Decimal(1)


class CdiReference(BaseStrategy):
    """
    Referência de renda fixa: todo o caixa parado vai para a oferta atrelada ao CDI
    que paga mais depois do imposto no vencimento.
    """

    key = "cdi_100"
    name = "100% no CDI"
    bot_names = ("Rentista", "Dona Selic", "Conservador")
    summary = "Todo o dinheiro na renda fixa que paga o CDI."
    description = (
        "Aplica o caixa parado, a cada dia, na oferta de renda fixa atrelada ao CDI "
        "que paga mais depois do imposto. É a régua para comparar as outras estratégias."
    )
    group = StrategyGroup.REFERENCE
    term_hint = (
        "CDI é a taxa de juros que os bancos cobram entre si, a régua da renda fixa. "
        "Um título que paga 100% do CDI rende o mesmo que ela; 110% rende 10% a mais."
    )
    params = ()

    def next(self, ctx: StrategyContext, params: dict[str, StrategyParamValue]) -> None:
        value = ctx.cash.quantize(CENT, ROUND_DOWN)
        if value < MIN_INVESTMENT:
            return

        # Oferta com teto por jogador não comporta o caixa inteiro
        offers = [
            o
            for o in ctx.fixed_offers
            if o.rate_index is RateIndexType.CDI and o.player_cap is None
        ]
        if not offers:
            return

        best = min(offers, key=lambda o: (-_net_rate(o), str(o.asset_uuid)))
        ctx.invest(
            best.asset_uuid,
            value,
            f"Aplicou o caixa parado em {best.name}, que paga {_percent(best)}% do CDI",
        )


def _net_rate(offer: FixedIncomeOfferDTO) -> Decimal:
    """Percentual do CDI que sobra depois do IR no vencimento."""
    return offer.interest_rate * (1 - offer.income_tax_rate_at_maturity)


def _percent(offer: FixedIncomeOfferDTO) -> str:
    return f"{offer.interest_rate * 100:.0f}".replace(".", ",")
