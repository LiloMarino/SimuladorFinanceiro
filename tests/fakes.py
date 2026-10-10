from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date
from decimal import Decimal

from backend.core.utils import is_business_day, next_business_day
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.variable_income.entities.position import Position

USER_ID = 1


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


def client(name: str) -> uuid.UUID:
    """client_id estável a partir de um apelido legível."""
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


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

    def get_cash(self, client_id: uuid.UUID) -> Decimal:
        return self.cash[client_id]

    def add_cash(self, client_id: uuid.UUID, cash: Decimal) -> None:
        self.cash[client_id] += cash

    def get_current_price(self, position: Position) -> Decimal:
        return position.avg_price
