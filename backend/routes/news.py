from fastapi import APIRouter

from backend.core import repository
from backend.core.dependencies import ActiveSimulation
from backend.core.dto.news import NewsDTO

news_router = APIRouter(prefix="/api/news", tags=["News"])


@news_router.get(
    "",
    response_model=list[NewsDTO],
    summary="Jornal da partida",
    description="Todas as manchetes da partida em andamento, da mais nova para a mais antiga.",
)
def get_news(simulation: ActiveSimulation):
    return repository.news.of_simulation(simulation.settings.id)
