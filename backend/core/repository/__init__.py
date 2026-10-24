from backend.core.repository.achievements import AchievementsRepository
from backend.core.repository.credit import CreditRepository
from backend.core.repository.economic import EconomicRepository
from backend.core.repository.event import EventRepository
from backend.core.repository.fixed_income import FixedIncomeRepository
from backend.core.repository.generated_future import GeneratedFutureRepository
from backend.core.repository.import_settings import ImportSettingsRepository
from backend.core.repository.last_simulation_settings import (
    LastSimulationSettingsRepository,
)
from backend.core.repository.portfolio import PortfolioRepository
from backend.core.repository.preset import PresetRepository
from backend.core.repository.settings import SettingsRepository
from backend.core.repository.simulation import SimulationRepository
from backend.core.repository.simulation_player import SimulationPlayerRepository
from backend.core.repository.snapshot import SnapshotRepository
from backend.core.repository.statistics import StatisticsRepository
from backend.core.repository.stock import StockRepository
from backend.core.repository.strategy import StrategyRepository
from backend.core.repository.user import UserRepository

stock = StockRepository()
economic = EconomicRepository()
user = UserRepository()
event = EventRepository()
snapshot = SnapshotRepository()
portfolio = PortfolioRepository()
fixed_income = FixedIncomeRepository()
credit = CreditRepository()
statistics = StatisticsRepository()
settings = SettingsRepository()
simulation = SimulationRepository()
simulation_player = SimulationPlayerRepository()
generated_future = GeneratedFutureRepository()
import_settings = ImportSettingsRepository()
last_simulation_settings = LastSimulationSettingsRepository()
preset = PresetRepository()
achievements = AchievementsRepository()
strategy = StrategyRepository()
