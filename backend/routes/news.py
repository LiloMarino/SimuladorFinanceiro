from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from backend.core import repository
from backend.core.dependencies import ActiveSimulation
from backend.core.dto.news import NewsDTO

news_router = APIRouter(prefix="/api/news", tags=["News"])


@news_router.get(
    "",
    response_model=list[NewsDTO],
    summary="Jornal da partida",
    description="As manchetes de um mês da partida em andamento, da mais nova para a mais antiga.",
)
def get_news(
    simulation: ActiveSimulation,
    month: Annotated[
        str,
        Query(
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            description="O mês das manchetes, no formato AAAA-MM.",
        ),
    ],
):
    return repository.news.of_month(
        simulation.settings.id, date.fromisoformat(f"{month}-01")
    )
