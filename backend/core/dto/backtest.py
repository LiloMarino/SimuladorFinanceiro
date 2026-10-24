from datetime import date
from decimal import Decimal

from pydantic import Field, model_validator

from backend.core.dto.base import BaseDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import BacktestPriceImpact
from backend.core.player_colors import MAX_PLAYERS


class BacktestParticipantDTO(BaseDTO):
    """Uma estratégia no backtest: vira um jogador sem pessoa, com carteira própria."""

    nickname: str
    color: str
    strategy_key: str
    # Os parâmetros que faltarem ficam no padrão do catálogo
    params: dict[str, StrategyParamValue] = Field(default_factory=dict)


class BacktestConfigDTO(BaseDTO):
    """Tudo o que o host escolhe para um backtest: o período, o dinheiro e as estratégias."""

    name: str = Field(min_length=1)
    start_date: date
    end_date: date
    starting_cash: Decimal = Field(gt=0)
    monthly_contribution: Decimal = Field(ge=0)
    price_impact: BacktestPriceImpact
    participants: list[BacktestParticipantDTO] = Field(
        min_length=1, max_length=MAX_PLAYERS
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser antes da data de fim.")
        return self


class BacktestCoverageDTO(BaseDTO):
    """Até onde há mercado para o backtest, somando todas as séries."""

    # O dia em que todas as séries já existem
    first_date: date | None
    # Até aqui o mercado é real; depois dele, gerado
    real_end: date | None
    generated_end: date | None


class BacktestSetupDTO(BaseDTO):
    coverage: BacktestCoverageDTO
    # A configuração do último backtest (ou a do `?from=`); nula no primeiro uso
    config: BacktestConfigDTO | None
    # Nome livre para sugerir quando não há configuração anterior
    suggested_name: str


class BacktestPointDTO(BaseDTO):
    """O retrato de um dia no gráfico: o patrimônio de cada estratégia e as referências."""

    day: date
    # Na ordem dos participantes
    equity: list[Decimal]
    # Saldo inicial mais os aportes até o dia
    contributed: Decimal
    # O que o mesmo dinheiro, com os mesmos aportes, valeria no CDI e no Ibovespa
    cdi: Decimal
    ibov: Decimal | None


class BacktestFailureDTO(BaseDTO):
    """Estratégia que deu erro: para de operar e fica com a carteira que tinha."""

    nickname: str
    day: date
    message: str


class BacktestProgressDTO(BaseDTO):
    simulation_id: int
    name: str
    host_nickname: str
    start_date: date
    end_date: date
    total_days: int
    done_days: int
    current_date: date | None
    # Estimado pelo ritmo real: pregões feitos ÷ tempo decorrido
    seconds_left: float | None


class BacktestStatusDTO(BaseDTO):
    progress: BacktestProgressDTO | None
    participants: list[BacktestParticipantDTO]
    points: list[BacktestPointDTO]
    failures: list[BacktestFailureDTO]


class BacktestProgressEventDTO(BaseDTO):
    """O que mudou desde o último aviso: o andamento e os pontos e falhas novos."""

    progress: BacktestProgressDTO
    points: list[BacktestPointDTO]
    failures: list[BacktestFailureDTO]


class BacktestStoppedDTO(BaseDTO):
    """O backtest parado e salvo até onde chegou."""

    simulation_id: int


class BacktestEndedEventDTO(BaseDTO):
    reason: str
    simulation_id: int


class BacktestResultDTO(BaseDTO):
    """O backtest salvo: a configuração, onde parou e a série de referência para o relatório."""

    simulation_id: int
    config: BacktestConfigDTO
    # Último pregão simulado; igual ao fim quando concluiu
    stopped_on: date | None
    finished: bool
    total_days: int
    done_days: int
    references: list["BacktestReferencePointDTO"]
    failures: list[BacktestFailureDTO]


class BacktestReferencePointDTO(BaseDTO):
    day: date
    contributed: Decimal
    cdi: Decimal
    ibov: Decimal | None
