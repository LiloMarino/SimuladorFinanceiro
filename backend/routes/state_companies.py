from fastapi import APIRouter, status

from backend.core.dto.state_company import (
    FoundStateCompanyRequest,
    StateCompaniesPanelDTO,
    StateFoundingPreviewDTO,
    StateOrderPreviewDTO,
    StateOrderRequest,
    StateReservationRequest,
)
from backend.routes.dependencies import ActiveSimulation, CurrentUser

state_companies_router = APIRouter(
    prefix="/api/government/state-companies", tags=["Government"]
)


@state_companies_router.get(
    "",
    response_model=StateCompaniesPanelDTO,
    summary="Obter as estatais",
    description="Retorna o resumo (o que o governo tem nas estatais, o que elas renderam ao Tesouro em 12 meses, a inflação represada e o teto de pontos de IPCA), uma linha por estatal com a ordem dada e a em vigor, os movimentos recentes e as ofertas de privatização abertas com o pedido de quem vê. A sala inteira lê; `is_president` diz quem comanda. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_state_companies(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_state_companies(user)


@state_companies_router.post(
    "/found-preview",
    response_model=StateFoundingPreviewDTO,
    summary="Simular a fundação de uma estatal",
    description="Só o presidente simula. Retorna a medida de fundar (voto, vigência e efeito na dívida) e os efeitos da empresa: o capital posto, o gasto da fundação por mês, o empurrão permanente no crescimento e o dividendo esperado ao Tesouro por ano.",
)
def preview_state_founding(
    simulation: ActiveSimulation, user: CurrentUser, payload: FoundStateCompanyRequest
):
    return simulation.preview_state_founding(user, payload)


@state_companies_router.get(
    "/{ticker}/order-preview",
    response_model=StateOrderPreviewDTO,
    summary="Simular as ordens de uma estatal",
    description="Mostra o efeito de cada degrau do controle de preço (pontos de IPCA, corte de lucro, fator de preço e de dividendo, dividendo esperado ao Tesouro por mês e o motivo de estar bloqueado pelo teto) e de cada política de dividendos, mais o teto que sobra à estatal. A sala inteira lê.",
)
def preview_state_order(simulation: ActiveSimulation, user: CurrentUser, ticker: str):
    return simulation.preview_state_order(user, ticker)


@state_companies_router.put(
    "/{ticker}/order",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dar a ordem a uma estatal",
    description="Só o presidente dá, e só à estatal ativa e sem privatização na fila. A ordem (degrau do controle de preço e política de dividendos) vale do mês seguinte; o degrau que levaria a soma de todas as estatais acima do teto de pontos de IPCA é recusado.",
)
def set_state_order(
    simulation: ActiveSimulation,
    user: CurrentUser,
    ticker: str,
    payload: StateOrderRequest,
):
    simulation.set_state_order(user, ticker, payload)


@state_companies_router.post(
    "/offer/reservation",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reservar ações na oferta de privatização",
    description="Pede a quantidade de ações na oferta aberta, sem reservar caixa: cada pedido substitui o anterior e o caixa só paga no fechamento. Recusa com 409 fora da janela da oferta.",
)
def reserve_state_offer(
    simulation: ActiveSimulation, user: CurrentUser, payload: StateReservationRequest
):
    simulation.reserve_state_offer(user, payload)
