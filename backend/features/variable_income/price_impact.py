import math
from collections import defaultdict
from datetime import date
from typing import TypeVar

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.daily_equity_flow import DailyEquityFlowDTO
from backend.core.dto.stock_price_history import StockPriceHistoryDTO
from backend.core.utils import business_days_between, subtract_business_days

# Pregões usados na média de volume que serve de régua para o tamanho da ordem
AVERAGE_VOLUME_WINDOW = 20

# O preço nunca chega a zero, por maior que seja a venda acumulada
MIN_FACTOR = 0.01

CandleRow = TypeVar("CandleRow", bound=CandleDTO)
PriceRow = TypeVar("PriceRow", bound=CandleDTO | StockPriceHistoryDTO)


def impact(quantity: int, average_volume: float, k: float) -> float:
    """
    Deslocamento relativo do preço, com o sinal da quantidade: k * √(|quantidade| ÷ volume médio).
    Ex.: k = 0,02 e quantidade = 10% do volume médio → +0,63%.
    """
    if quantity == 0 or average_volume <= 0:
        return 0.0
    return math.copysign(k * math.sqrt(abs(quantity) / average_volume), quantity)


def decay(age: int, decay_days: int) -> float:
    """
    Fração do impacto que resta `age` pregões depois do primeiro dia afetado: (1 - age/T)².
    Vale 1 no primeiro dia, cai rápido no começo e zera em T.
    """
    if not 0 <= age < decay_days:
        return 0.0
    return (1 - age / decay_days) ** 2


class PriceImpact:
    """
    Deslocamento do preço histórico causado pelas ordens dos jogadores.

    O fator de um ativo num dia é 1 + a soma dos impactos ainda ativos. Cada impacto vem
    da quantidade líquida (compras - vendas) de um dia inteiro, então fatiar uma ordem em
    várias execuções não muda nada e compra e venda iguais entre jogadores se anulam. Uma
    ordem afeta só os pregões seguintes ao dela, e o efeito volta ao histórico em T pregões.

    Os eventos de renda variável são a fonte da verdade: o impacto é sempre recalculado
    a partir deles, então retomar uma simulação reconstrói os mesmos preços.
    """

    def __init__(self, simulation_id: int, enabled: bool, k: float, decay_days: int):
        self.simulation_id = simulation_id
        self.enabled = enabled
        self.k = k
        self.decay_days = decay_days
        self._factors: dict[str, float] = {}
        self._average_volumes: dict[tuple[str, date], float] = {}

    def refresh(self, today: date) -> None:
        """Recalcula o fator de cada ativo em `today` a partir dos eventos persistidos."""
        if not self.enabled:
            return

        since = subtract_business_days(today, self.decay_days)
        flows_by_ticker: dict[str, list[DailyEquityFlowDTO]] = defaultdict(list)
        for flow in repository.event.get_daily_equity_flow(self.simulation_id, since):
            flows_by_ticker[flow.ticker].append(flow)

        self._factors = {
            ticker: self._factor_on(flows, today)
            for ticker, flows in flows_by_ticker.items()
        }

    def apply(self, candle: CandleRow) -> CandleRow:
        """Candle do dia corrente com o fator calculado no último `refresh`."""
        return _scale(candle, self._factors.get(candle.ticker, 1.0))

    def apply_history(
        self, ticker: str, history: list[StockPriceHistoryDTO]
    ) -> list[StockPriceHistoryDTO]:
        """Histórico com o fator de cada dia, igual ao que foi negociado naquele dia."""
        factors = self.factors_on(ticker, [row.price_date for row in history])
        return [_scale(row, factors[row.price_date]) for row in history]

    def factors_on(self, ticker: str, days: list[date]) -> dict[date, float]:
        """Fator do ativo em cada um dos `days`, reconstruído dos eventos persistidos."""
        flows = (
            repository.event.get_daily_equity_flow(self.simulation_id, ticker=ticker)
            if self.enabled
            else []
        )
        return {day: self._factor_on(flows, day) if flows else 1.0 for day in days}

    def _factor_on(self, flows: list[DailyEquityFlowDTO], on: date) -> float:
        total = 0.0
        for flow in flows:
            # O primeiro pregão depois da ordem tem idade 0
            remaining = decay(
                business_days_between(flow.flow_date, on) - 1, self.decay_days
            )
            if remaining > 0:
                average_volume = self._average_volume(flow.ticker, flow.flow_date)
                total += impact(flow.quantity, average_volume, self.k) * remaining
        return max(1 + total, MIN_FACTOR)

    def _average_volume(self, ticker: str, day: date) -> float:
        key = (ticker, day)
        if key not in self._average_volumes:
            self._average_volumes[key] = repository.stock.get_average_volume(
                ticker, day, AVERAGE_VOLUME_WINDOW
            )
        return self._average_volumes[key]


def _scale(row: PriceRow, factor: float) -> PriceRow:
    """Multiplica OHLC pelo fator, no centavo; volume é o histórico."""
    if factor == 1.0:
        return row

    update: dict[str, float] = {
        field: round(getattr(row, field) * factor, 2)
        for field in ("open", "high", "low", "close")
    }
    if isinstance(row, CandleDTO):
        # change_pct é uma razão entre preços do mesmo dia: o fator se cancela
        update["change"] = round(update["close"] - update["open"], 2)
    return row.model_copy(update=update)
