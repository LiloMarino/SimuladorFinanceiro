from fastapi import APIRouter

from backend.core.dto.sovereign_fund import (
    SovereignContributionPreviewDTO,
    SovereignContributionRequest,
    SovereignFundPanelDTO,
)
from backend.routes.dependencies import ActiveSimulation, CurrentUser

sovereign_fund_router = APIRouter(
    prefix="/api/government/sovereign-fund", tags=["Government"]
)


@sovereign_fund_router.get(
    "",
    response_model=SovereignFundPanelDTO,
    summary="Obter o Fundo Soberano",
    description="Retorna o caixa do fundo, o que o Tesouro aportou e o que voltou a ele (vendas e dividendos), o teto de fatia por empresa e por gestora e a carteira com a fatia de cada ativo. A sala inteira lê; `is_president` diz a quem a conta do fundo se abre. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_sovereign_fund(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_sovereign_fund(user)


@sovereign_fund_router.post(
    "/contribution-preview",
    response_model=SovereignContributionPreviewDTO,
    summary="Simular um aporte no Fundo Soberano",
    description="Só o presidente simula. Retorna a medida de aportar (voto, vigência e efeito na dívida) e o caixa do fundo antes e depois. O aporte não move o PIB. Para propor, use a medida `CONTRIBUTE_SOVEREIGN_FUND` com o valor em reais.",
)
def preview_sovereign_contribution(
    simulation: ActiveSimulation,
    user: CurrentUser,
    payload: SovereignContributionRequest,
):
    return simulation.preview_sovereign_contribution(user, payload)
