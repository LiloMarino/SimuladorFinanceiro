from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.exceptions.http_exceptions import ForbiddenError


def ensure_chart_hints(settings: SimulationSettingsDTO) -> None:
    """Os padrões de vela só existem na partida com as dicas de análise técnica ligadas."""
    if not settings.show_chart_hints:
        raise ForbiddenError(
            "As dicas de análise técnica estão desligadas nesta partida."
        )
