from datetime import date, datetime

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.dto.series_coverage import SeriesCoverageDTO
from backend.core.enum import MarketRegime


class FutureParamsDTO(BaseDTO):
    """Os controles de uma geração: os mesmos valores geram o mesmo futuro."""

    until: date
    seed: int = Field(ge=0, le=2**63 - 1)
    temperature: float = Field(ge=0, le=3)
    # Nulo começa no bioma do mercado de hoje
    start_regime: MarketRegime | None = None
    inflation_shock: float = Field(ge=-5, le=20)


class GeneratedFutureDTO(FutureParamsDTO):
    generated_at: datetime
    # Até onde o real ocupou o lugar do gerado depois da gravação; gerar de novo
    # emenda o futuro a partir dele
    real_advanced_until: date | None
    saved_simulations_on_future: int


class FuturePreviewRequest(FutureParamsDTO):
    # Ativo mostrado além do Ibovespa; nulo mostra só o Ibovespa
    ticker: str | None = None


class PreviewPointDTO(BaseDTO):
    date: date
    value: float


class PreviewSeriesDTO(BaseDTO):
    """Uma série da prévia: a cauda real e o gerado que continua dela."""

    key: str
    real: list[PreviewPointDTO]
    generated: list[PreviewPointDTO]


class LevelChangeDTO(BaseDTO):
    # Fração: 0.31 é +31%
    change: float
    start: float
    end: float
    on: date


class DrawdownDTO(BaseDTO):
    # Fração negativa: -0.24 é a queda de 24% do pico ao fundo
    value: float
    peak: date
    trough: date


class PeakDTO(BaseDTO):
    # Em % ao ano
    value: float
    on: date
    today: float


class SeriesStartDTO(BaseDTO):
    """Primeiro dia gerado de uma série: o dia útil seguinte ao último real dela."""

    key: str
    start: date


class FuturePreviewDTO(BaseDTO):
    current_regime: MarketRegime
    ibov_start: SeriesStartDTO
    # A série que começa a ser gerada mais cedo, quando não é o Ibovespa
    laggard_start: SeriesStartDTO | None
    trading_days: int
    assets: int
    indicators: int
    ibov: PreviewSeriesDTO
    asset: PreviewSeriesDTO | None
    # SELIC em % ao ano e IPCA de 12 meses em %
    selic: PreviewSeriesDTO
    ipca_12m: PreviewSeriesDTO
    ibov_change: LevelChangeDTO
    max_drawdown: DrawdownDTO | None
    selic_peak: PeakDTO | None
    ipca_peak: PeakDTO | None


class ReplacedGeneratedDTO(BaseDTO):
    """Os dias em que o real chegou e ocupou o lugar do gerado."""

    days: int
    start: date
    end: date


class ImportResultDTO(BaseDTO):
    coverage: SeriesCoverageDTO
    replaced: ReplacedGeneratedDTO | None
