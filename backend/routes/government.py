from fastapi import APIRouter, status

from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.government import (
    ContributionRequest,
    DonationRequest,
    ElectionPanelDTO,
    ExpelRequest,
    FoundPartyRequest,
    JoinPartyRequest,
    TicketRequest,
    ViceAnswerRequest,
)

government_router = APIRouter(prefix="/api/government", tags=["Government"])


@government_router.get(
    "/election",
    response_model=ElectionPanelDTO,
    summary="Obter a eleição",
    description="Retorna as datas, os partidos com chapa, filiados, verba e promessa, as pesquisas, a simulação do 2º turno, as doações, o resultado dos turnos, o governo em vigor e o ranking de jogadores e de partidos. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_election(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_election(user)


@government_router.post(
    "/parties",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Fundar um partido",
    description="Funda um partido com nome, sigla de 2 a 5 letras, cor, promessa na régua de 1 a 5 e a contribuição mensal de quem funda, que pode ser zero. Só na campanha, um ano antes do 1º turno; um partido por jogador.",
)
def found_party(
    simulation: ActiveSimulation, user: CurrentUser, payload: FoundPartyRequest
):
    simulation.found_party(user, payload)


@government_router.post(
    "/parties/{party_id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Filiar-se a um partido",
    description="Entra no partido escolhendo quanto contribui por mês, que pode ser zero. Um partido por vez.",
)
def join_party(
    simulation: ActiveSimulation,
    user: CurrentUser,
    party_id: int,
    payload: JoinPartyRequest,
):
    simulation.join_party(user, party_id, payload.contribution)


@government_router.delete(
    "/membership",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair do partido",
    description="A contribuição para na hora e o que já saiu do caixa não volta. A fundadora que sai passa o partido ao filiado mais antigo; o último a sair desfaz o partido.",
)
def leave_party(simulation: ActiveSimulation, user: CurrentUser):
    simulation.leave_party(user)


@government_router.put(
    "/membership/contribution",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mudar a contribuição",
    description="Troca a contribuição mensal ao partido; vale a partir do próximo dia 1º. Pode ser zero.",
)
def set_contribution(
    simulation: ActiveSimulation, user: CurrentUser, payload: ContributionRequest
):
    simulation.set_contribution(user, payload.contribution)


@government_router.post(
    "/parties/expel",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Expulsar um filiado",
    description="Só a fundadora expulsa. A expulsão é pública; se o expulso era candidato ou vice, a vaga abre.",
)
def expel_member(
    simulation: ActiveSimulation, user: CurrentUser, payload: ExpelRequest
):
    simulation.expel_member(user, payload.nickname)


@government_router.put(
    "/parties/ticket",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Montar a chapa",
    description="Só a fundadora escolhe candidato e vice entre os filiados, até o fim da inscrição (último dia do mês anterior ao 1º turno). O vice recebe o convite e aceita ou recusa; sem resposta, a chapa concorre sem vice.",
)
def set_ticket(simulation: ActiveSimulation, user: CurrentUser, payload: TicketRequest):
    simulation.set_ticket(user, payload.candidate, payload.vice)


@government_router.post(
    "/vice/answer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Responder ao convite de vice",
    description="Aceita ou recusa a vaga de vice. Recusar não tira do partido: a vaga volta para a fundadora indicar outro filiado.",
)
def answer_vice(
    simulation: ActiveSimulation, user: CurrentUser, payload: ViceAnswerRequest
):
    simulation.answer_vice(user, payload.accept)


@government_router.post(
    "/donations",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Doar a um finalista",
    description="Entre os turnos, quem ficou de fora doa a um dos finalistas, até a véspera do 2º turno. A doação é pública, sai do caixa de uma vez e vira apoio do finalista.",
)
def donate(simulation: ActiveSimulation, user: CurrentUser, payload: DonationRequest):
    simulation.donate_to_party(user, payload.party_id, payload.amount)
