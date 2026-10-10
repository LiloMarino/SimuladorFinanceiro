from datetime import datetime

from backend.core.dto.base import BaseDTO
from backend.core.enum import IndicatorSeries


class FetchLogDTO(BaseDTO):
    series: IndicatorSeries
    attempted_at: datetime
    succeeded_at: datetime | None
