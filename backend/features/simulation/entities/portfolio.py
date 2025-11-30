from dataclasses import dataclass

from backend.features.simulation.entities.fixed_income_asset import FixedIncomeAsset
from backend.features.simulation.entities.position import Position


@dataclass
class Portfolio:
    cash: float
    variable_income: list[Position]
    fixed_income: list[FixedIncomeAsset]
    patrimonial_history: list[float]
