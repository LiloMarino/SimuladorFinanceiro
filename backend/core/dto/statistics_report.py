"""
Relatório de desempenho em abas, um DTO por aba. Toda fração vem como fração
(0.2 = 20%); métrica que a série ainda não permite medir vem None.
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from backend.core.dto.base import BaseDTO
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.sector import SectorAllocationDTO
from backend.core.enum import VictoryCriterion


class SeriesPointDTO(BaseDTO):
    date: date
    value: Decimal


class PlayerRefDTO(BaseDTO):
    player_nickname: str
    simulation_id: int
    simulation_name: str


# Geral

type ScoreAxis = Literal["return", "risk", "consistency", "efficiency"]
type ScoreMetric = Literal[
    "return_over_cdi",
    "return_over_ibov",
    "max_drawdown",
    "annual_volatility",
    "time_underwater",
    "worst_month",
    "months_above_cdi",
    "positive_months",
    "sharpe_ratio",
    "sortino_ratio",
]


class ScoreMetricDTO(BaseDTO):
    metric: ScoreMetric
    # Valor medido (fração, pregões ou número puro) e os pontos que ele vale
    value: Decimal | None
    points: Decimal | None


class ScoreAxisDTO(BaseDTO):
    axis: ScoreAxis
    # Média dos pontos das métricas medidas do eixo
    points: Decimal | None
    metrics: list[ScoreMetricDTO]


class ScoreDTO(BaseDTO):
    # Soma dos pontos dos eixos: chão 0, sem teto
    total: Decimal
    axes: list[ScoreAxisDTO]


class PlayerRankingDTO(PlayerRefDTO):
    position: int
    total_networth: Decimal
    # Retorno sobre o capital aportado (saldo inicial + aportes)
    return_value: Decimal
    return_percent: Decimal
    # Dias úteis com snapshot: o tamanho da amostra das métricas
    days: int
    # None até a amostra ter `min_score_days` retornos diários
    score: ScoreDTO | None
    sharpe_ratio: Decimal | None


class OverviewReportDTO(BaseDTO):
    # Ordenado pelo ranking: o primeiro é o melhor
    players: list[PlayerRankingDTO]
    average_return: Decimal | None
    min_score_days: int
    # O critério que ordenou o ranking: o da partida, ou a nota entre partidas diferentes
    criterion: VictoryCriterion


# Rentabilidade


class PlayerReturnsDTO(PlayerRefDTO):
    networth: list[SeriesPointDTO]
    # Retorno acumulado da cota, que só os rendimentos movem: o aporte não conta
    cumulative_return: list[SeriesPointDTO]
    capital_provided: Decimal
    annual_return: Decimal | None
    months_above_cdi: int
    positive_months: int
    months: int


type BenchmarkSeries = Literal["CDI", "IBOV"]


class BenchmarkDTO(BaseDTO):
    series: BenchmarkSeries
    simulation_id: int
    simulation_name: str
    cumulative_return: list[SeriesPointDTO]
    annual_return: Decimal | None


class ReturnsReportDTO(BaseDTO):
    players: list[PlayerReturnsDTO]
    # Uma linha de cada referência por simulação, no período dela
    benchmarks: list[BenchmarkDTO]


# Risco


class PlayerRiskDTO(PlayerRefDTO):
    drawdown: list[SeriesPointDTO]
    rolling_volatility: list[SeriesPointDTO]
    max_drawdown: Decimal | None
    annual_volatility: Decimal | None
    sharpe_ratio: Decimal | None
    sortino_ratio: Decimal | None
    # Maior sequência de pregões abaixo do pico anterior
    time_underwater: int | None
    worst_month: Decimal | None
    annual_return: Decimal | None
    # Retornos diários na amostra
    days: int


class RiskReportDTO(BaseDTO):
    players: list[PlayerRiskDTO]
    rolling_window: int


# Composição


class SectorProfitDTO(BaseDTO):
    # None agrupa as ações sem classificação ("Sem setor")
    sector: str | None
    profit: Decimal


class PlayerCompositionDTO(PlayerRefDTO):
    history: list[PatrimonialHistoryDTO]
    # Renda variável por setor no último dia da série
    sectors: list[SectorAllocationDTO]
    # 1 ÷ soma dos quadrados das frações dos setores
    effective_sectors: Decimal | None
    # Vendas - compras + valor da posição no último dia, antes do IR
    sector_profit: list[SectorProfitDTO]


class CompositionReportDTO(BaseDTO):
    players: list[PlayerCompositionDTO]


# Operações


class MonthlyVolumeDTO(BaseDTO):
    month: date
    bought: Decimal
    sold: Decimal


class PlayerOperationsDTO(PlayerRefDTO):
    buy_trades: int
    sell_trades: int
    traded_volume: Decimal
    # Volume negociado ÷ patrimônio médio do período
    turnover: Decimal | None
    income_tax_paid: Decimal
    # Executado - histórico, somado com o sinal de quem paga: compra cara e venda
    # barata são custo; None com o impacto de preço desligado
    impact_cost: Decimal | None
    monthly_volume: list[MonthlyVolumeDTO]


class OperationsReportDTO(BaseDTO):
    players: list[PlayerOperationsDTO]
