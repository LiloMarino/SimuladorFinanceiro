"""
Indicadores técnicos de uma ação: as séries que o gráfico desenha e o Resumo
técnico do dia, todos calculados com os parâmetros escolhidos pelo jogador.
"""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from backend.core.dto.base import BaseDTO

type MovingAverageKind = Literal["sma", "ema"]

# Cada item que o seletor liga e desliga
type IndicatorKey = Literal[
    "averages", "bollinger", "volume", "rsi", "macd", "stochastic", "atr", "obv"
]

# Os indicadores que entram no Resumo técnico, na ordem dele
type ReadingKey = Literal[
    "sma", "ema", "bollinger", "rsi", "macd", "stochastic", "atr", "obv"
]

type ReadingGroup = Literal["price", "oscillator"]

# "none" é o indicador sem lado (o ATR mede o tamanho do movimento, não a direção)
type ReadingSignal = Literal["buy", "neutral", "sell", "none"]

type SummaryVerdict = Literal["strong_buy", "buy", "neutral", "sell", "strong_sell"]


class MovingAverageDTO(BaseDTO):
    kind: MovingAverageKind
    period: int = Field(ge=2, le=200)


class IndicatorParamsDTO(BaseDTO):
    """Os parâmetros de todos os indicadores; os padrões são os de mercado."""

    averages: list[MovingAverageDTO] = Field(
        default=[
            MovingAverageDTO(kind="sma", period=20),
            MovingAverageDTO(kind="ema", period=50),
        ],
        max_length=4,
    )
    bollinger_period: int = Field(default=20, ge=2, le=100)
    bollinger_deviations: float = Field(default=2, ge=0.5, le=5)
    rsi_period: int = Field(default=14, ge=2, le=50)
    rsi_overbought: int = Field(default=70, ge=50, le=95)
    rsi_oversold: int = Field(default=30, ge=5, le=50)
    macd_fast: int = Field(default=12, ge=2, le=50)
    macd_slow: int = Field(default=26, ge=3, le=100)
    macd_signal: int = Field(default=9, ge=2, le=50)
    stochastic_k: int = Field(default=14, ge=2, le=50)
    stochastic_d: int = Field(default=3, ge=1, le=20)
    atr_period: int = Field(default=14, ge=2, le=50)

    @model_validator(mode="after")
    def _ordered(self) -> "IndicatorParamsDTO":
        if self.rsi_oversold >= self.rsi_overbought:
            raise ValueError(
                "O IFR sobrevendido precisa ficar abaixo do sobrecomprado."
            )
        if self.macd_fast >= self.macd_slow:
            raise ValueError("A média curta do MACD precisa ser menor que a longa.")
        return self


class IndicatorSettingsDTO(BaseDTO):
    """O que o jogador deixou ligado no gráfico e com quais parâmetros; vale para todas as ações."""

    visible: list[IndicatorKey] = Field(default=[])
    params: IndicatorParamsDTO = IndicatorParamsDTO()


class IndicatorsRequestDTO(BaseDTO):
    params: IndicatorParamsDTO = IndicatorParamsDTO()
    # Os indicadores cujas séries voltam; o resumo sempre conta todos
    series: list[IndicatorKey] = Field(default=[])


class IndicatorPointDTO(BaseDTO):
    date: date
    value: float


class AverageSeriesDTO(BaseDTO):
    kind: MovingAverageKind
    period: int
    points: list[IndicatorPointDTO]


class BandsSeriesDTO(BaseDTO):
    upper: list[IndicatorPointDTO]
    middle: list[IndicatorPointDTO]
    lower: list[IndicatorPointDTO]


class MacdSeriesDTO(BaseDTO):
    line: list[IndicatorPointDTO]
    signal: list[IndicatorPointDTO]
    histogram: list[IndicatorPointDTO]


class StochasticSeriesDTO(BaseDTO):
    k: list[IndicatorPointDTO]
    d: list[IndicatorPointDTO]


class IndicatorSeriesDTO(BaseDTO):
    """Só os pedidos vêm preenchidos; cada série começa no primeiro pregão com valor."""

    averages: list[AverageSeriesDTO] | None = None
    bollinger: BandsSeriesDTO | None = None
    rsi: list[IndicatorPointDTO] | None = None
    macd: MacdSeriesDTO | None = None
    stochastic: StochasticSeriesDTO | None = None
    atr: list[IndicatorPointDTO] | None = None
    obv: list[IndicatorPointDTO] | None = None


class TechnicalReadingDTO(BaseDTO):
    key: ReadingKey
    group: ReadingGroup
    # Nome curto com os parâmetros ("MMS 20", "MACD 12, 26, 9")
    label: str
    # O valor do dia; na Bollinger é a média, com a faixa em `lower`/`upper`
    value: float | None
    lower: float | None = None
    upper: float | None = None
    signal: ReadingSignal
    # O porquê da leitura em uma frase curta ("preço acima da média")
    reason: str
    # Pregões que o indicador precisa para existir e quantos ainda faltam (0 quando já tem valor)
    needed_sessions: int
    missing_sessions: int


class TechnicalSummaryDTO(BaseDTO):
    date: date | None
    readings: list[TechnicalReadingDTO]
    buys: int
    sells: int
    # Indicadores com lado e com valor: a base da nota
    counted: int
    # Os indicadores com lado (todos menos o ATR), com ou sem valor
    sided: int
    # (compras - vendas) ÷ contados, de -1 a 1; None quando a maioria ainda não tem valor
    score: float | None
    verdict: SummaryVerdict | None


class TechnicalIndicatorsDTO(BaseDTO):
    series: IndicatorSeriesDTO
    summary: TechnicalSummaryDTO
