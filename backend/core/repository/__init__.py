from backend.core.decorators.cached_classproperty import cached_classproperty
from backend.core.repository.economic import EconomicRepository
from backend.core.repository.stock import StockRepository


class RepositoryManager:
    @cached_classproperty
    def stock(self):
        return StockRepository()

    @cached_classproperty
    def economic(self):
        return EconomicRepository()
