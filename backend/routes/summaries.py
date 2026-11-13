from fastapi import APIRouter

from backend.core import repository
from backend.core.dto.summaries import SummaryDTO
from backend.routes.dependencies import ActiveSimulation, CurrentUser

summaries_router = APIRouter(prefix="/api/summaries", tags=["Summaries"])


@summaries_router.get(
    "",
    response_model=list[SummaryDTO],
    summary="Resumos do jogador",
    description="As retrospectivas do ano do jogador na partida em andamento, do mais novo para o mais antigo.",
)
def get_summaries(simulation: ActiveSimulation, user: CurrentUser):
    return repository.summaries.of_player(simulation.settings.id, user.id)
