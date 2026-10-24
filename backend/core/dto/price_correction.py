from backend.core.dto.base import BaseDTO


class PriceCorrectionResultDTO(BaseDTO):
    """O que a correção de erros de dado trocou na base."""

    corrected_days: int
    stocks: int
