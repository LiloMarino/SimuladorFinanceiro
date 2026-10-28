from fastapi import APIRouter, status

from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.government import (
    ContributionRequest,
    DonationRequest,
    ElectionPanelDTO,
    ExpelRequest,
    FoundPartyRequest,
    GovernmentPanelDTO,
    JoinPartyRequest,
    MeasurePreviewDTO,
    PartyFlagsRequest,
    ProposeMeasureRequest,
    TicketRequest,
    ViceAnswerRequest,
)

government_router = APIRouter(prefix="/api/government", tags=["Government"])


@government_router.get(
    "/election",
    response_model=ElectionPanelDTO,
    summary="Obter a eleição",
    description="Retorna as datas, os grupos de eleitores, os partidos com chapa, filiados, verba, bandeiras e perfil, as pesquisas com a margem de erro (no total e por grupo), o apoio e a rejeição do partido de quem vê em cada grupo, a simulação do 2º turno, as doações, o resultado dos turnos, o governo em vigor e o ranking de jogadores e de partidos. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_election(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_election(user)


@government_router.post(
    "/parties",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Fundar um partido",
    description="Funda um partido com nome, sigla de 2 a 8 letras, cor, 3 bandeiras diferentes (Mercado livre e Justiça social não andam juntas) e a contribuição mensal de quem funda, que pode ser zero. Só na campanha, um ano antes do 1º turno; um partido por jogador.",
)
def found_party(
    simulation: ActiveSimulation, user: CurrentUser, payload: FoundPartyRequest
):
    simulation.found_party(user, payload)


@government_router.put(
    "/parties/flags",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Escolher as bandeiras do partido",
    description="O fundador de um partido criado antes das bandeiras escolhe as 3; até lá, o perfil do partido é neutro. Depois de escolhidas, as bandeiras não mudam. Mercado livre e Justiça social não andam juntas.",
)
def set_party_flags(
    simulation: ActiveSimulation, user: CurrentUser, payload: PartyFlagsRequest
):
    simulation.set_party_flags(user, payload.flags)


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
    description="Só a fundadora escolhe o candidato entre os filiados e o vice entre os jogadores da sala (de outro partido ou sem partido), até o fim da inscrição (último dia do mês anterior ao 1º turno). Não vale quem já é vice ou candidato de outra chapa. O vice recebe o convite e aceita ou recusa; sem resposta, a chapa concorre sem vice.",
)
def set_ticket(simulation: ActiveSimulation, user: CurrentUser, payload: TicketRequest):
    simulation.set_ticket(user, payload.candidate, payload.vice)


@government_router.post(
    "/vice/answer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Responder ao convite de vice",
    description="Aceita ou recusa a vaga de vice. Recusar não muda o partido de quem responde: a vaga volta para a fundadora indicar outro jogador.",
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


@government_router.get(
    "",
    response_model=GovernmentPanelDTO,
    summary="Obter o governo",
    description="Retorna o governo em vigor, a aprovação com o histórico e os fatores, os impostos de hoje, as medidas por setor, a fila do Congresso (pública), o próximo voto e a carteira congelada do presidente. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_government(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_governance(user)


@government_router.post(
    "/measures",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Propor uma medida",
    description="Só o presidente propõe. A medida entra na fila do Congresso na hora, sem pausar a partida; no último dia útil do mês o Congresso vota a fila com chance igual à aprovação, e a aprovada vale 90 dias depois.",
)
def propose_measure(
    simulation: ActiveSimulation, user: CurrentUser, payload: ProposeMeasureRequest
):
    simulation.propose_measure(user, payload)


@government_router.post(
    "/measures/preview",
    response_model=MeasurePreviewDTO,
    summary="Simular uma medida",
    description="Mostra o que a medida faria sem propô-la: faixa na régua, marca do governo antes e depois, pontos na aprovação, chance no próximo voto, quando passaria a valer e, nas medidas de setor, quem tem os ativos atingidos.",
)
def preview_measure(
    simulation: ActiveSimulation, user: CurrentUser, payload: ProposeMeasureRequest
):
    return simulation.preview_measure(user, payload)


@government_router.delete(
    "/measures/{measure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Retirar uma medida da fila",
    description="Só o presidente retira, e só antes do voto do Congresso.",
)
def withdraw_measure(simulation: ActiveSimulation, user: CurrentUser, measure_id: int):
    simulation.withdraw_measure(user, measure_id)


@government_router.post(
    "/measures/{measure_id}/repropose",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Propor de novo uma medida rejeitada",
    description="A medida rejeitada deste governo volta à fila do Congresso para o próximo voto.",
)
def repropose_measure(simulation: ActiveSimulation, user: CurrentUser, measure_id: int):
    simulation.repropose_measure(user, measure_id)
