from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


@dataclass(frozen=True, slots=True, kw_only=True)
class PatrimonialHistoryDTO(BaseDTO):
    snapshot_date: date
    total_networth: Decimal
    total_equity: Decimal
    total_fixed: Decimal
    total_cash: Decimal
    total_contribution: Decimal
