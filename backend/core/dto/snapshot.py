from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, NamedTuple

from pydantic import field_serializer

from backend.core.dto.base import BaseDTO
from backend.core.enum import AssetClass

if TYPE_CHECKING:
    from backend.core.models.models import Snapshots

SCALE = Decimal("0.000001")


class DayBalanceDTO(NamedTuple):
    """O que o motor sabe do dia do jogador; o caixa e o aporte saem dos eventos."""

    total_equity: Decimal
    total_fixed: Decimal
    total_debt: Decimal
    equity_by_class: dict[AssetClass, Decimal]


class SnapshotDTO(BaseDTO):
    user_id: int
    snapshot_date: date
    total_equity: Decimal
    total_fixed: Decimal
    total_cash: Decimal
    total_contribution: Decimal
    total_debt: Decimal
    total_networth: Decimal
    equity_by_class: dict[AssetClass, Decimal]
    created_at: datetime

    @field_serializer("equity_by_class")
    def _serialize_equity_by_class(
        self, value: dict[AssetClass, Decimal]
    ) -> dict[str, str]:
        """Sai pronto para a coluna JSONB, na escala das colunas `Numeric(20, 6)` do snapshot."""
        return {
            asset_class.value: str(total.quantize(SCALE))
            for asset_class, total in value.items()
        }

    @staticmethod
    def from_model(m: Snapshots) -> SnapshotDTO:
        return SnapshotDTO(
            user_id=m.user_id,
            snapshot_date=m.snapshot_date,
            total_equity=m.total_equity,
            total_fixed=m.total_fixed,
            total_cash=m.total_cash,
            total_contribution=m.total_contribution,
            total_debt=m.total_debt,
            total_networth=m.total_networth,
            equity_by_class=m.equity_by_class,
            created_at=m.created_at,
        )
