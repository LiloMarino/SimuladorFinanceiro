from backend.core.dto.base import BaseDTO


class ImportSettingsDTO(BaseDTO):
    """Como a base é importada, escolha do host."""

    # A importação troca por interpolação o dia em que a fonte errou o preço
    correct_price_errors: bool = True
