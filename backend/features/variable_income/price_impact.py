import math
from bisect import bisect_left
from collections import defaultdict
from datetime import date
from decimal import Decimal
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
# O menor preço que a ação escalada mostra: um centavo
MIN_PRICE = 0.01

CandleRow = TypeVar("CandleRow", bound=CandleDTO)
PriceRow = TypeVar("PriceRow", bound=CandleDTO | StockPriceHistoryDTO)


def impact(quantity: Decimal, average_volume: float, k: float) -> float:
    """
    Deslocamento relativo do preço, com o sinal da quantidade: k * √(|quantidade| ÷ volume médio).
    Ex.: k = 0,02 e quantidade = 10% do volume médio → +0,63%.
    """
    if quantity == 0 or average_volume <= 0:
        return 0.0
    return math.copysign(
        k * math.sqrt(float(abs(quantity)) / average_volume), float(quantity)
    )


def decay(age: int, decay_days: int) -> float:
    """
    Fração do impacto que resta `age` pregões depois do primeiro dia afetado: (1 - age/T)².
    Vale 1 no primeiro dia, cai rápido no começo e zera em T.
    """
    if not 0 <= age < decay_days:
        return 0.0
    return (1 - age / decay_days) ** 2


# Fração do volume médio diário usada no exemplo da prévia
PREVIEW_VOLUME_SHARE = 0.10
# O volume médio do exemplo da prévia, em ações
PREVIEW_AVERAGE_VOLUME = 1_000_000


def preview_curve(k: float, decay_days: int) -> list[float]:
    """
    O impacto de uma compra de `PREVIEW_VOLUME_SHARE` do volume médio em cada pregão
    afetado: o primeiro dia e o efeito até sumir, em `decay_days + 1` pontos.
    """
    first_day = impact(
        Decimal(round(PREVIEW_VOLUME_SHARE * PREVIEW_AVERAGE_VOLUME)),
        PREVIEW_AVERAGE_VOLUME,
        k,
    )
    return [first_day * decay(age, decay_days) for age in range(decay_days + 1)]


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
        # O fator de um dia só depende das ordens dos dias anteriores, que o flush grava
        # antes do refresh: calculado uma vez, ele vale pelo resto da partida
        self._factors_by_day: dict[date, dict[str, float]] = {}
        self._earlier_days: dict[str, dict[date, float]] = {}
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
        self._factors_by_day[today] = self._factors

    def apply(self, candle: CandleRow) -> CandleRow:
        """Candle do dia corrente com o fator calculado no último `refresh` e o efeito do governo na bolsa."""
        factor = self._factors.get(candle.ticker, 1.0) * self._market(
            candle.ticker, candle.price_date
        )
        return _scale(candle, factor)

    def apply_history(
        self, ticker: str, history: list[StockPriceHistoryDTO]
    ) -> list[StockPriceHistoryDTO]:
        """Histórico com o fator de cada dia, igual ao que foi negociado naquele dia."""
        factors = self.factors_on(ticker, [row.price_date for row in history])
        return [_scale(row, factors[row.price_date]) for row in history]

    def factors_on(self, ticker: str, days: list[date]) -> dict[date, float]:
        """Fator do ativo em cada um dos `days`, reconstruído dos eventos persistidos."""
        orders = self._orders_factors(ticker, days)
        return {day: orders[day] * self._market(ticker, day) for day in days}

    def _orders_factors(self, ticker: str, days: list[date]) -> dict[date, float]:
        """Só o efeito das ordens: os dias sem refresh saem dos eventos, uma vez cada."""
        if not self.enabled:
            return dict.fromkeys(days, 1.0)

        earlier = self._earlier_days.setdefault(ticker, {})
        missing = [
            day
            for day in days
            if day not in self._factors_by_day and day not in earlier
        ]
        if missing:
            flows = repository.event.get_daily_equity_flow(
                self.simulation_id, ticker=ticker
            )
            self._load_average_volumes(flows)
            for day in missing:
                earlier[day] = self._factor_on(flows, day) if flows else 1.0
        return {
            day: self._factors_by_day[day].get(ticker, 1.0)
            if day in self._factors_by_day
            else earlier[day]
            for day in days
        }

    def _market(self, ticker: str, day: date) -> float:
        """O efeito das medidas do governo na bolsa vale com o impacto das ordens ligado ou não."""
        return repository.economic.stock_factor(self.simulation_id, ticker, day)

    def _factor_on(self, flows: list[DailyEquityFlowDTO], on: date) -> float:
        # Os fluxos vêm em ordem de data: os ativos em `on` são os T pregões logo antes
        # dele, e somá-los na mesma ordem dá o mesmo fator que percorrer todos
        end = bisect_left(flows, on, key=lambda flow: flow.flow_date)
        start = end
        while (
            start > 0
            and business_days_between(flows[start - 1].flow_date, on) <= self.decay_days
        ):
            start -= 1

        active = flows[start:end]
        self._load_average_volumes(active)
        total = 0.0
        for flow in active:
            # O primeiro pregão depois da ordem tem idade 0
            remaining = decay(
                business_days_between(flow.flow_date, on) - 1, self.decay_days
            )
            if remaining > 0:
                average_volume = self._average_volumes[(flow.ticker, flow.flow_date)]
                total += impact(flow.quantity, average_volume, self.k) * remaining
        return max(1 + total, MIN_FACTOR)

    def _load_average_volumes(self, flows: list[DailyEquityFlowDTO]) -> None:
        """O volume médio do dia de cada fluxo ainda sem ele, uma consulta por ativo."""
        missing: dict[str, list[date]] = defaultdict(list)
        for flow in flows:
            if (flow.ticker, flow.flow_date) not in self._average_volumes:
                missing[flow.ticker].append(flow.flow_date)
        for ticker, days in missing.items():
            averages = repository.stock.get_average_volumes(
                ticker, days, AVERAGE_VOLUME_WINDOW, simulation_id=self.simulation_id
            )
            self._average_volumes.update(
                ((ticker, day), average) for day, average in averages.items()
            )


def _scale(row: PriceRow, factor: float) -> PriceRow:
    """Multiplica OHLC pelo fator, no centavo e com piso de um centavo; volume é o histórico."""
    if factor == 1.0:
        return row

    update: dict[str, float] = {
        field: _scaled_price(getattr(row, field), factor)
        for field in ("open", "high", "low", "close")
    }
    if isinstance(row, CandleDTO):
        # change_pct é uma razão entre preços do mesmo dia: o fator se cancela
        update["change"] = round(update["close"] - update["open"], 2)
    return row.model_copy(update=update)


def _scaled_price(price: float, factor: float) -> float:
    """O preço escalado no centavo; um preço positivo não arredonda a zero."""
    scaled = round(price * factor, 2)
    return max(scaled, MIN_PRICE) if price > 0 else scaled
