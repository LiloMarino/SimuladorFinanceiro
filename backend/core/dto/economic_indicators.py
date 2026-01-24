from backend.core.dto.base import BaseDTO


class EconomicIndicatorsDTO(BaseDTO):
    ipca: float
    selic: float
    cdi: float
