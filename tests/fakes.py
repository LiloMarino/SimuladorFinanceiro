from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date
from decimal import Decimal

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping, VictoryCriterion
from backend.core.utils import is_business_day, next_business_day
from backend.features.fixed_income.fixed_broker import CoverSale
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.variable_income.entities.position import Position

USER_ID = 1
# A carteira que o resolvedor devolve para todo cliente dos testes sem banco
PORTFOLIO_ID = 1


def no_pay(*_) -> Decimal:
    """A conversão de salários em reais de uma partida sem salário: nada vale reais."""
    return Decimal(0)


def daily_series(start: date, end: date, value: str) -> dict[date, Decimal]:
    """Série diária constante (CDI/SELIC): um valor por dia útil de `start` a `end`."""
    day = start if is_business_day(start) else next_business_day(start)
    values = {}
    while day <= end:
        values[day] = Decimal(value)
        day = next_business_day(day)
    return values


def monthly_series(start: date, months: int, value: str) -> dict[date, Decimal]:
    """Série mensal constante (IPCA): `months` meses a partir do mês de `start`."""
    values = {}
    year, month = start.year, start.month
    for _ in range(months):
        values[date(year, month, 1)] = Decimal(value)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return values


def simulation_settings(
    grouping: PlayerGrouping = PlayerGrouping.INDIVIDUAL,
) -> SimulationSettingsDTO:
    """Regras de uma partida de teste, individual ou em equipes."""
    return SimulationSettingsDTO(
        name="Partida",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 12, 31),
        starting_cash=Decimal(10000),
        monthly_contribution=Decimal(0),
        price_impact_enabled=False,
        price_impact_k=0.02,
        price_impact_decay_days=20,
        victory_criterion=VictoryCriterion.SCORE,
        game_type=GameType.CLASSIC,
        goal_net_worth=Decimal(100000),
        monthly_salary=Decimal(8000),
        monthly_expense=Decimal(5000),
        unexpected_per_year=3,
        withdrawal_rate=Decimal("0.04"),
        inflation_adjusted=False,
        player_grouping=grouping,
    )


def client(name: str) -> uuid.UUID:
    """client_id estável a partir de um apelido legível."""
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


class NoFixedIncome:
    """Corretora de renda fixa sem posições: a cobertura automática não tem o que vender."""

    def sell_for_cash(
        self, client_id: uuid.UUID, shortfall: Decimal, include_marked: bool
    ) -> list[CoverSale]:
        return []


class FakeSimulationEngine(SimulationEngine):
    """
    Motor em memória para Broker e FixedBroker: só caixa, data e preço.

    O `__init__` do motor real fica de fora, porque ele monta os brokers e o caixa
    carregado do banco; aqui o caixa começa no dict informado.
    """

    def __init__(
        self,
        *,
        cash: dict[uuid.UUID, Decimal] | None = None,
        current_date: date = date(2020, 1, 6),
    ):
        self.simulation_id = 1
        self.current_date = current_date
        self.cash: defaultdict[uuid.UUID, Decimal] = defaultdict(Decimal, cash or {})
        self.stocks = {}
        self.fixed_broker = NoFixedIncome()
        self.dividends: list[tuple[uuid.UUID, str, Decimal]] = []

    def get_cash(self, client_id: uuid.UUID) -> Decimal:
        return self.cash[client_id]

    def add_cash(self, client_id: uuid.UUID, cash: Decimal) -> None:
        self.cash[client_id] += cash

    def transfer_cash(
        self, source: uuid.UUID, target: uuid.UUID, amount: Decimal
    ) -> None:
        self.cash[source] -= amount
        self.cash[target] += amount

    def credit_fund_offer(self, client_id: uuid.UUID, amount: Decimal) -> None:
        self.cash[client_id] += amount

    def credit_fund_subscription(self, client_id: uuid.UUID, amount: Decimal) -> None:
        self.cash[client_id] += amount

    def charge_fund_fee(
        self, client_id: uuid.UUID, amount: Decimal, performance: bool
    ) -> None:
        self.cash[client_id] -= amount

    def receive_fund_fee(
        self, client_id: uuid.UUID, amount: Decimal, performance: bool
    ) -> None:
        self.cash[client_id] += amount

    def pay_dividend(self, client_id: uuid.UUID, ticker: str, amount: Decimal) -> None:
        self.cash[client_id] += amount
        self.dividends.append((client_id, ticker, amount))

    def get_current_price(self, position: Position) -> Decimal:
        return position.avg_price
