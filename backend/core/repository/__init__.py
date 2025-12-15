from backend.core.repository.economic import EconomicRepository
from backend.core.repository.event import EventRepository
from backend.core.repository.snapshot import SnapshotRepository
from backend.core.repository.stock import StockRepository
from backend.core.repository.user import UserRepository

stock = StockRepository()
economic = EconomicRepository()
user = UserRepository()
event = EventRepository()
snapshot = SnapshotRepository()
