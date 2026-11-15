"""A ordem do presidente numa estatal: o controle de preço e a política de dividendos."""

from collections.abc import Mapping
from dataclasses import dataclass

from backend.core.enum import DividendPolicy, StateControl


@dataclass(frozen=True)
class StateOrder:
    """O que o presidente manda numa estatal; sem ordem dada, vale o padrão."""

    control: StateControl = StateControl.NONE
    dividend_policy: DividendPolicy = DividendPolicy.NORMAL

    @property
    def is_default(self) -> bool:
        return self == StateOrder()


@dataclass(frozen=True)
class OrderChange:
    """O que mudou na ordem de uma estatal entre duas vigências."""

    ticker: str
    before: StateOrder
    after: StateOrder

    @property
    def control_changed(self) -> bool:
        return self.before.control is not self.after.control

    @property
    def policy_changed(self) -> bool:
        return self.before.dividend_policy is not self.after.dividend_policy


def order_changes(
    before: Mapping[str, StateOrder], now: Mapping[str, StateOrder]
) -> list[OrderChange]:
    """As estatais cuja ordem mudou da vigência `before` para `now`, por código; sem ordem vale o padrão."""
    changes: list[OrderChange] = []
    for ticker in sorted({*before, *now}):
        old = before.get(ticker, StateOrder())
        new = now.get(ticker, StateOrder())
        if old != new:
            changes.append(OrderChange(ticker, old, new))
    return changes
