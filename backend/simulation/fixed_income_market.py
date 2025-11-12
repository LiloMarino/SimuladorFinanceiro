from datetime import datetime

from backend import logger_utils
from backend.realtime import notify
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

    def get_asset(self, uuid: str) -> FixedIncomeAsset | None:
        return self._assets.get(uuid)

    def _generate_assets(self):
        if self._current_month is None:
            return

        year, month = self._current_month
        current_date = datetime(year, month, 1)

        self._assets = FixedIncomeFactory.generate_assets(
            current_date=current_date, n=10
        )
        notify(
            "fixed_assets_update",
            {"assets": [asset.to_dict() for asset in self.get_available_assets()]},
        )
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
