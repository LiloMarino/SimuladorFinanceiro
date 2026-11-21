from collections.abc import Callable
from decimal import Decimal

from backend.core.dto.fund import FundIssuanceEstimateDTO
from backend.core.fund_reference import (
    FundReference,
    maker_attractiveness,
    maker_leftover,
)
from backend.features.funds.fund_book import Fund, FundBook
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.strategy.fair_value_trading import OPINION_RANGE

# As cotas que os bots cotistas compram de `ticker` no último pregão da sobra: recebe a referência
# da cota, a opinião dos bots sobre ela (fração do valor) e as cotas em circulação
BotDemand = Callable[[str, FundReference, float, Decimal], Decimal]


class IssuanceEstimator:
    """A captação que a sobra de uma emissão deve trazer: o que cada bot cotista compra pela
    própria estratégia, e o Mercado a fração da sobra que o desempenho e o ágio pedem.

    A conta usa as mesmas funções da compra de verdade, com o dia da decisão (o último pregão
    da sobra) montado a partir do que cada bot tem hoje.
    """

    def __init__(
        self, book: FundBook, engine: SimulationEngine, bot_demand: BotDemand
    ) -> None:
        self._book = book
        self._engine = engine
        self._bot_demand = bot_demand

    def estimate(
        self,
        fund: Fund,
        leftover: Decimal,
        price: Decimal,
        book_price: Decimal | None,
    ) -> FundIssuanceEstimateDTO | None:
        """A faixa de captação de `leftover` cotas vendidas a `price`, com a foto `book_price`; nula sem sobra ou sem PL por cota."""
        reference = self._book.leftover_reference(fund, price, book_price)
        if reference is None or leftover <= 0:
            return None
        attractiveness = maker_attractiveness(reference)
        total = fund.account.quotas
        rows = [
            self._bound(fund, reference, attractiveness, leftover, price, total, bias)
            for bias in (-OPINION_RANGE, OPINION_RANGE)
        ]
        low, high = rows
        return FundIssuanceEstimateDTO(
            quotas_min=low[0],
            quotas_max=high[0],
            raised_min=low[1],
            raised_max=high[1],
            commission_min=low[2],
            commission_max=high[2],
            performance=reference.performance,
            premium=reference.premium,
        )

    def _bound(
        self,
        fund: Fund,
        reference: FundReference,
        attractiveness: float,
        leftover: Decimal,
        price: Decimal,
        total: Decimal,
        bias: float,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """As cotas, o dinheiro que entra no caixa da gestora e a comissão da sobra quando todo bot tem a opinião `bias`; os bots compram antes do Mercado."""
        bots = min(self._bot_demand(fund.ticker, reference, bias, total), leftover)
        maker = maker_leftover(leftover - bots, attractiveness)
        # Só a compra dos bots paga comissão: o Mercado subscreve com caixa sintético
        commission = self._engine.offer_commission_on(bots * price)
        return (bots + maker, (bots + maker) * price - commission, commission)
