from backend.core.decorators.static_property import staticproperty
from backend.core.repository.economic import EconomicRepository
from backend.core.repository.stock import StockRepository


class RepositoryManager:
    @staticproperty
    def stock():
        return StockRepository()

    @staticproperty
    def economic():
        return EconomicRepository()
