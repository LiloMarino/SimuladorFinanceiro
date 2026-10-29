from fastapi import APIRouter

from backend.core import repository
from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.summaries import SummaryDTO

summaries_router = APIRouter(prefix="/api/summaries", tags=["Summaries"])


@summaries_router.get(
    "",
    response_model=list[SummaryDTO],
    summary="Resumos do jogador",
    description="Os resumos do mês e as retrospectivas do ano do jogador na partida em andamento, do mais novo para o mais antigo.",
)
def get_summaries(simulation: ActiveSimulation, user: CurrentUser):
    return repository.summaries.of_player(simulation.settings.id, user.id)
