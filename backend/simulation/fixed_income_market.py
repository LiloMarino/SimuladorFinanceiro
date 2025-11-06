from datetime import datetime

from backend import logger_utils
from backend.simulation.entities.fixed_income_asset import FixedIncomeAsset
from backend.simulation.fixed_income_factory import FixedIncomeFactory

logger = logger_utils.setup_logger(__name__)


class FixedIncomeMarket:
    """Gera e mantém o hall de ativos de renda fixa disponíveis."""

    def __init__(self):
        self._current_month: tuple[int, int] | None = None
        self._assets: dict[str, FixedIncomeAsset] = {}

    def refresh_assets(self, current_date: datetime):
        current_month = (current_date.year, current_date.month)
        if self._current_month == current_month:
            return

        self._current_month = current_month
        self._generate_assets()

    def get_available_assets(self) -> list[FixedIncomeAsset]:
        return list(self._assets.values())

    def _generate_assets(self):
        self._assets = FixedIncomeFactory.generate_assets(10)
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
