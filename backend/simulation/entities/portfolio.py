from dataclasses import dataclass
from typing import List

from backend.simulation.entities.fixed_income_asset import FixedIncomeAsset
from backend.simulation.entities.position import Position


@dataclass
class Portfolio:
    cash: float
    variable_income: List[Position]
    fixed_income: List[FixedIncomeAsset]
    patrimonial_history: List[float]
