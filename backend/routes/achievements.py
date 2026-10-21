from fastapi import APIRouter

from backend.core.dependencies import CurrentUser
from backend.core.dto.achievements import AchievementDTO
from backend.features.achievements import service

achievements_router = APIRouter(prefix="/api", tags=["Achievements"])


@achievements_router.get(
    "/achievements",
    response_model=list[AchievementDTO],
    summary="Conquistas do jogador",
    description="O catálogo inteiro com o que o jogador já desbloqueou e o progresso das que têm meta. Conquista secreta bloqueada não traz nome nem descrição.",
)
def list_achievements(user: CurrentUser):
    return service.list_achievements(user.id)


@achievements_router.post(
    "/achievements/seen",
    status_code=204,
    summary="Marcar conquistas como vistas",
    description="Chamado ao abrir a tela de conquistas: tira o selo de nova das desbloqueadas até aqui.",
)
def mark_achievements_seen(user: CurrentUser):
    service.mark_seen(user.id)
