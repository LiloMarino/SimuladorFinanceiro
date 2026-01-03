from backend.core.repository.economic import EconomicRepository
from backend.core.repository.event import EventRepository
from backend.core.repository.fixed_income import FixedIncomeRepository
from backend.core.repository.portfolio import PortfolioRepository
from backend.core.repository.settings import SettingsRepository
from backend.core.repository.snapshot import SnapshotRepository
from backend.core.repository.statistics import StatisticsRepository
from backend.core.repository.stock import StockRepository
from backend.core.repository.user import UserRepository

stock = StockRepository()
economic = EconomicRepository()
user = UserRepository()
event = EventRepository()
snapshot = SnapshotRepository()
portfolio = PortfolioRepository()
fixed_income = FixedIncomeRepository()
statistics = StatisticsRepository()
settings = SettingsRepository()
