from datetime import date, datetime
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class SnapshotDTO(BaseDTO):
    user_id: int
    snapshot_date: date
    total_equity: Decimal
    total_fixed: Decimal
    total_cash: Decimal
    total_contribution: Decimal
    total_networth: Decimal
    created_at: datetime
