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
from backend.core.enum import TeamNaming, VictoryCriterion


class SeriesPointDTO(BaseDTO):
    date: date
    value: Decimal


class PlayerRefDTO(BaseDTO):
    player_nickname: str
    # Chave da paleta: a cor do jogador nesta simulação
    color: str
    simulation_id: int
    simulation_name: str
    # Índice da equipe (1 a 10); nulo fora do modo em equipes
    team: int | None


class TeamReportDTO(BaseDTO):
    """Base dos relatórios: como chamar as equipes, escolha do host nas regras."""

    team_naming: TeamNaming


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
    # Meses fechados na partida: o total dos "7 de 12" da nota
    months: int
    # None até a amostra ter `min_score_days` retornos diários
    score: ScoreDTO | None
    sharpe_ratio: Decimal | None
    # Valor no critério da partida e quanto falta para o primeiro (0 para o líder)
    criterion_value: Decimal | None
    leader_gap: Decimal | None
    # Eixo da nota com menos pontos: onde o jogador mais pode subir
    weakest_axis: ScoreAxis | None
    # Quanto o valor dele no critério passa (ou fica abaixo) da média da equipe; None fora de equipes
    team_contribution: Decimal | None


class TeamPullerDTO(BaseDTO):
    """Quem mais puxou a média da equipe para cima."""

    player_nickname: str
    color: str
    contribution: Decimal
    # Eixo da nota em que mais puxou e quanto; None quando o critério não é a nota geral
    axis: ScoreAxis | None
    axis_gap: Decimal | None


class TeamRankingDTO(BaseDTO):
    """Equipe no ranking: o valor dela em cada critério é a média dos membros."""

    team: int
    simulation_id: int
    position: int
    members: int
    # Membros com valor no critério: só eles entram na média ("2 de 3")
    measured_members: int
    total_networth: Decimal
    return_value: Decimal
    return_percent: Decimal
    # Eixos da nota na média dos membros; None até algum membro ter a nota
    score: ScoreDTO | None
    sharpe_ratio: Decimal | None
    criterion_value: Decimal | None
    leader_gap: Decimal | None
    weakest_axis: ScoreAxis | None
    top_puller: TeamPullerDTO | None


class OverviewReportDTO(TeamReportDTO):
    # Ordenado pelo ranking: o primeiro é o melhor
    players: list[PlayerRankingDTO]
    # Uma entrada por equipe, ordenada pelo ranking; vazio fora do modo em equipes
    teams: list[TeamRankingDTO]
    average_return: Decimal | None
    min_score_days: int
    # O critério que ordenou o ranking: o da partida, ou a nota entre partidas diferentes
    criterion: VictoryCriterion


# Rentabilidade


class MonthlyReturnDTO(BaseDTO):
    month: date
    value: Decimal
    # CDI composto no mesmo mês, para comparar
    cdi: Decimal


class PlayerReturnsDTO(PlayerRefDTO):
    networth: list[SeriesPointDTO]
    # Retorno acumulado da cota, que só os rendimentos movem: o aporte não conta
    cumulative_return: list[SeriesPointDTO]
    capital_provided: Decimal
    annual_return: Decimal | None
    months_above_cdi: int
    positive_months: int
    months: int
    monthly_returns: list[MonthlyReturnDTO]


type BenchmarkSeries = Literal["CDI", "IBOV"]


class BenchmarkDTO(BaseDTO):
    series: BenchmarkSeries
    simulation_id: int
    simulation_name: str
    cumulative_return: list[SeriesPointDTO]
    annual_return: Decimal | None


class TeamReturnsDTO(BaseDTO):
    """Curvas e contagens da equipe: a média dos membros em cada dia."""

    team: int
    simulation_id: int
    members: int
    networth: list[SeriesPointDTO]
    cumulative_return: list[SeriesPointDTO]
    capital_provided: Decimal
    annual_return: Decimal | None
    # Média de meses entre os membros: exata, quem mostra arredonda
    months_above_cdi: Decimal
    positive_months: Decimal
    months: int


class ReturnsReportDTO(TeamReportDTO):
    players: list[PlayerReturnsDTO]
    teams: list[TeamReturnsDTO]
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


class TeamRiskDTO(BaseDTO):
    """Métricas de risco da equipe: média simples dos membros em cada uma."""

    team: int
    simulation_id: int
    members: int
    max_drawdown: Decimal | None
    annual_volatility: Decimal | None
    sharpe_ratio: Decimal | None
    sortino_ratio: Decimal | None
    time_underwater: Decimal | None
    worst_month: Decimal | None
    annual_return: Decimal | None


class RiskReportDTO(TeamReportDTO):
    players: list[PlayerRiskDTO]
    teams: list[TeamRiskDTO]
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


class TeamCompositionDTO(BaseDTO):
    """Como a equipe dividiu o dinheiro no último dia: média das frações dos membros."""

    team: int
    simulation_id: int
    members: int
    cash_share: Decimal | None
    equity_share: Decimal | None
    fixed_share: Decimal | None


class CompositionReportDTO(TeamReportDTO):
    players: list[PlayerCompositionDTO]
    teams: list[TeamCompositionDTO]


# Operações


class MonthlyVolumeDTO(BaseDTO):
    month: date
    bought: Decimal
    sold: Decimal
    buy_count: int
    sell_count: int


type TurnoverStyle = Literal["Segura", "Moderado", "Ativo", "Muito ativo"]


class PlayerOperationsDTO(PlayerRefDTO):
    buy_trades: int
    sell_trades: int
    traded_volume: Decimal
    # Volume negociado ÷ patrimônio médio do período
    turnover: Decimal | None
    turnover_style: TurnoverStyle | None
    income_tax_paid: Decimal
    # Executado - histórico, somado com o sinal de quem paga: compra cara e venda
    # barata são custo; None com o impacto de preço desligado
    impact_cost: Decimal | None
    monthly_volume: list[MonthlyVolumeDTO]


class TeamOperationsDTO(BaseDTO):
    """Operações da equipe: volume, IR e negócios são somas (totais, não desempenho)."""

    team: int
    simulation_id: int
    members: int
    buy_trades: int
    sell_trades: int
    traded_volume: Decimal
    income_tax_paid: Decimal
    # Média dos membros que têm o giro
    turnover: Decimal | None
    impact_cost: Decimal | None
    monthly_volume: list[MonthlyVolumeDTO]


class OperationsReportDTO(TeamReportDTO):
    players: list[PlayerOperationsDTO]
    teams: list[TeamOperationsDTO]


# Fechamento da partida


class PlayerHighlightDTO(BaseDTO):
    player_nickname: str
    color: str
    value: Decimal


class BestMonthDTO(BaseDTO):
    month: date
    value: Decimal


class HighlightsDTO(BaseDTO):
    biggest_return: PlayerHighlightDTO | None
    # A queda máxima mais rasa da sala
    smallest_drawdown: PlayerHighlightDTO | None
    most_trades: PlayerHighlightDTO | None
    most_tax: PlayerHighlightDTO | None
    # O melhor mês de quem está vendo; None se ele não jogou
    your_best_month: BestMonthDTO | None
