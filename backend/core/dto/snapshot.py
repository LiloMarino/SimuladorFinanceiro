from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core.dto.base import BaseDTO

if TYPE_CHECKING:
    from backend.core.models.models import Snapshots


class SnapshotDTO(BaseDTO):
    user_id: int
    snapshot_date: date
    total_equity: Decimal
    total_fixed: Decimal
    total_cash: Decimal
    total_contribution: Decimal
    total_networth: Decimal
    created_at: datetime

    @staticmethod
    def from_model(m: Snapshots) -> SnapshotDTO:
        return SnapshotDTO(
            user_id=m.user_id,
            snapshot_date=m.snapshot_date,
            total_equity=m.total_equity,
            total_fixed=m.total_fixed,
            total_cash=m.total_cash,
            total_contribution=m.total_contribution,
            total_networth=m.total_networth,
            created_at=m.created_at,
        )
