from datetime import date

from fastapi import APIRouter, status

from backend.core.dependencies import ActiveSimulation, CurrentUser
from backend.core.dto.budget import BudgetDTO, InitialAccountDTO
from backend.core.dto.campaign import (
    CampaignActionRequest,
    CampaignHistoryDTO,
    CampaignPanelDTO,
    CampaignRollDTO,
)
from backend.core.dto.government import (
    AnswerDealRequest,
    CongressBaseDTO,
    ContributionRequest,
    DealPreviewDTO,
    DonationRequest,
    ElectionPanelDTO,
    EndorsementRequest,
    ExpelRequest,
    FoundPartyRequest,
    GovernmentPanelDTO,
    GuidanceRequest,
    GuidanceRuleRequest,
    JoinPartyRequest,
    MeasurePreviewDTO,
    PartyFlagsRequest,
    PromisesPanelDTO,
    ProposeDealRequest,
    ProposeMeasureRequest,
    RunoffContributionRequest,
    TicketRequest,
    ViceAnswerRequest,
)
from backend.core.dto.promises import BalanceDTO, PromisesPreviewDTO, PromisesRequest
from backend.features.government.budget_panel import build_initial_account

government_router = APIRouter(prefix="/api/government", tags=["Government"])


@government_router.get(
    "/election",
    response_model=ElectionPanelDTO,
    summary="Obter a eleição",
    description="Retorna as datas, os grupos de eleitores, os partidos com chapa, filiados, verba, bandeiras e perfil, as pesquisas com a margem de erro (no total e por grupo), o apoio e a rejeição do partido de quem vê em cada grupo, a disputa do 2º turno (pesquisa semanal, para onde foram os votos de quem saiu, declarações e contribuições), as doações, o resultado dos turnos, o governo em vigor e o ranking de jogadores e de partidos. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
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
    simulation.join_party(user, party_id, payload.contribution, payload.congress)


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
    simulation.set_contribution(user, payload.contribution, payload.congress)


@government_router.put(
    "/congress/guidance",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Orientar a bancada numa votação",
    description="O líder do partido (o fundador; se ele sai, o filiado mais antigo) orienta a bancada com Sim ou Não numa medida da fila, ou no pedido de impeachment aberto quando `measure_id` vem nulo. Vale até a véspera da votação; sem orientação, a bancada segue a orientação padrão do partido. Com acordo de apoio em vigor, orientar Não numa medida rompe o acordo e exige `break_deal` verdadeiro. Recusa com 403 para quem não é líder e com 409 quando o partido não tem bancada, a votação já fechou ou falta a confirmação da quebra.",
)
def guide_bloc(
    simulation: ActiveSimulation, user: CurrentUser, payload: GuidanceRequest
):
    simulation.guide_bloc(user, payload.measure_id, payload.yes, payload.break_deal)


@government_router.get(
    "/base",
    response_model=CongressBaseDTO,
    summary="Obter a base do governo no Congresso",
    description="Retorna o partido do governo, as bancadas da casa com a situação de cada uma (na base, esperando resposta, o que impede propor), os acordos de apoio por emenda em vigor ou esperando resposta (preço, prazo, medidas orientadas Sim, cadeiras da base se acabar), o total das emendas e a última votação com a desobediência da base. Pública: a sala inteira vê. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_base(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_base(user)


@government_router.get(
    "/deals/preview",
    response_model=DealPreviewDTO,
    summary="Ver a prévia de uma proposta de acordo",
    description="Para a bancada `bloc_key`, retorna a emenda (fração do PIB por ano e reais por mês), o prazo, as cadeiras da base antes e depois, a dívida no fim do mandato sem e com o acordo, os grupos do aliado e, no partido do computador, se ele deve aceitar e quantas bandeiras divide com o governo. Recusa com 404 quando a bancada não tem cadeira.",
)
def preview_deal(simulation: ActiveSimulation, user: CurrentUser, bloc_key: int):
    return simulation.preview_deal(bloc_key)


@government_router.post(
    "/deals",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Propor um acordo de apoio",
    description="O presidente propõe à bancada entrar na base por 6 meses (no máximo até a véspera da posse do novo Congresso): a emenda é 0,005% do PIB por ano por cadeira (o centrão, 1,5 vez) e a bancada orienta Sim em tudo o que o governo propuser. O partido de jogador tem 15 dias para responder; o do computador responde no pregão seguinte. Recusa com 403 para quem não preside e com 409 quando o partido já é da base com mais de 31 dias de prazo, tem proposta esperando, recusou há menos de 30 dias ou o impeachment está em votação.",
)
def propose_deal(
    simulation: ActiveSimulation, user: CurrentUser, payload: ProposeDealRequest
):
    simulation.propose_deal(user, payload.bloc_key)


@government_router.put(
    "/deals/answer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Responder a proposta de acordo",
    description="O líder do partido aceita ou recusa a proposta que espera resposta; o acordo vale a partir de hoje. Recusar não custa nada. Recusa com 404 sem proposta e com 409 depois do prazo.",
)
def answer_deal(
    simulation: ActiveSimulation, user: CurrentUser, payload: AnswerDealRequest
):
    simulation.answer_deal(user, payload.accept)


@government_router.post(
    "/deals/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair da base do governo",
    description="O líder do partido aliado rompe o acordo: a emenda para e os grupos do governo somam rejeição ao partido dele. Recusa com 403 para quem não lidera o partido e com 409 quando o partido não está na base.",
)
def leave_base(simulation: ActiveSimulation, user: CurrentUser):
    simulation.leave_base(user)


@government_router.delete(
    "/deals/{deal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar a proposta de acordo",
    description="O presidente cancela a proposta antes da resposta. Recusa com 403 para quem não preside e com 409 quando a proposta já foi respondida.",
)
def withdraw_deal(simulation: ActiveSimulation, user: CurrentUser, deal_id: int):
    simulation.withdraw_deal(user, deal_id)


@government_router.post(
    "/deals/{deal_id}/break",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Romper o acordo de apoio",
    description="O presidente para de pagar a emenda: o acordo acaba na hora e os grupos do aliado somam rejeição ao partido do governo. Recusa com 403 para quem não preside e com 409 quando o acordo não está em vigor.",
)
def break_deal(simulation: ActiveSimulation, user: CurrentUser, deal_id: int):
    simulation.break_deal(user, deal_id)


@government_router.put(
    "/parties/guidance",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mudar a orientação padrão do partido",
    description="O líder troca a orientação padrão da bancada para um valor: Sim ou Não nas medidas que mais puxam esse valor. Vale quando o líder não orienta a votação.",
)
def set_guidance_rule(
    simulation: ActiveSimulation, user: CurrentUser, payload: GuidanceRuleRequest
):
    simulation.set_guidance_rule(user, payload.value, payload.yes)


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


@government_router.post(
    "/runoff/endorsement",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Declarar apoio no 2º turno",
    description="A fundadora do partido que ficou de fora declara apoio a um dos finalistas, ou neutralidade (sem partido no pedido). A declaração é uma só e não se desfaz: os indecisos que vieram do partido seguem o apoio na medida da confiança de cada grupo nele. Vale até a véspera do 2º turno; o partido do computador declara sozinho.",
)
def endorse(
    simulation: ActiveSimulation, user: CurrentUser, payload: EndorsementRequest
):
    simulation.endorse(user, payload.party_id)


@government_router.post(
    "/runoff/contribution",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Contribuir na campanha do 2º turno",
    description="Cada filiado de finalista faz uma contribuição única, paga na hora da própria carteira. O valor rende pela raiz do total do partido, igual em todos os grupos, e sai primeiro dos indecisos de cada grupo. Vale até a véspera do 2º turno.",
)
def contribute_runoff(
    simulation: ActiveSimulation,
    user: CurrentUser,
    payload: RunoffContributionRequest,
):
    simulation.contribute_runoff(user, payload.amount)


@government_router.get(
    "/campaign",
    response_model=CampaignPanelDTO,
    summary="Obter as ações de campanha do meu partido",
    description="Retorna, para o partido de quem vê, o preço de cada ação (TV, evento, comício e ataque), o que o dado rola em cada grupo e quanto a ação rende hoje pelo retorno decrescente, o apoio e a rejeição do partido, os rivais, as últimas ações, a verba de base e quanto do apoio de hoje ainda vale no 1º turno. Só os filiados veem; recusa com 409 a quem não tem partido.",
)
def get_campaign(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_campaign(user)


@government_router.get(
    "/campaign/history",
    response_model=CampaignHistoryDTO,
    summary="Obter o histórico de campanha do meu partido",
    description="Cada ação dos filiados com o dado e o efeito no dia, a verba de base e os ataques recebidos (sem o dado do rival), com quanto cada um vale hoje depois da queda pela metade a cada 3 meses. Só os filiados do partido veem.",
)
def get_campaign_history(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_campaign_history(user)


@government_router.post(
    "/campaign/actions",
    response_model=CampaignRollDTO,
    summary="Disparar uma ação de campanha",
    description="Qualquer filiado dispara TV, evento com um grupo, comício ou ataque a um rival e paga na hora, da própria carteira. O dado sai da semente da partida e a resposta traz o número tirado, a faixa e o efeito. Vale da abertura da campanha até a véspera do 1º turno; a ação que falha antes do dado não cobra nada.",
)
def campaign_action(
    simulation: ActiveSimulation, user: CurrentUser, payload: CampaignActionRequest
):
    return simulation.campaign_action(user, payload)


@government_router.get(
    "/promises",
    response_model=PromisesPanelDTO,
    summary="Obter as promessas da minha chapa",
    description="Retorna, para a fundadora do partido, as promessas anunciadas, as medidas gerais que se prometem com o que valem hoje e o passo de referência, os setores e até quando a lista aceita mudança (o último dia de inscrição das chapas). Recusa com 403 a quem não funda o partido.",
)
def get_promises(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_promises(user)


@government_router.post(
    "/promises/preview",
    response_model=PromisesPreviewDTO,
    summary="Simular as promessas da chapa",
    description="Mostra a lista de promessas como ficaria, sem anunciá-la: em cada grupo de eleitores, o apoio que cada promessa rende hoje (já descontado pela rejeição do partido), a afinidade e a reparação de rejeição se for cumprida e a rejeição que soma se for descumprida, mais a rejeição que voltar atrás nas já anunciadas custaria.",
)
def preview_promises(
    simulation: ActiveSimulation, user: CurrentUser, payload: PromisesRequest
):
    return simulation.preview_promises(user, payload)


@government_router.put(
    "/promises",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Anunciar as promessas da chapa",
    description="Só a fundadora define a lista (até 3 medidas), da abertura da campanha até o fim da inscrição das chapas. Medida com valor leva um alvo; medida de setor é sim ou não. A promessa rende apoio desde o anúncio; retirar, trocar ou baixar o alvo depois dele soma rejeição nos grupos que queriam a medida. A lista substitui a anterior.",
)
def set_promises(
    simulation: ActiveSimulation, user: CurrentUser, payload: PromisesRequest
):
    simulation.set_promises(user, payload)


@government_router.get(
    "/balances",
    response_model=list[BalanceDTO],
    summary="Obter os balanços de promessas",
    description="O balanço das promessas de cada governo que acabou, do mais recente ao mais antigo: o estado de cada promessa (cumprida, em andamento, descumprida ou na direção contrária) e a fração do caminho andada. Os números por grupo (afinidade somada e rejeição somada ou reparada) só chegam aos filiados do partido da chapa.",
)
def get_balances(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_balances(user)


@government_router.get(
    "",
    response_model=GovernmentPanelDTO,
    summary="Obter o governo",
    description="Retorna o governo em vigor, a aprovação com o histórico e os fatores, os impostos de hoje, as medidas por setor, a fila do Congresso (pública) com o efeito de cada medida no orçamento e o da fila inteira, o próximo voto e a carteira congelada do presidente. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_government(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_governance(user)


@government_router.get(
    "/budget",
    response_model=BudgetDTO,
    summary="Obter o orçamento",
    description="Retorna a conta do governo no último fechamento de mês (receita, gasto, juros, resultado e dívida, em % do PIB por ano e em reais), a receita de cada imposto do jogo contra a política padrão, os fechamentos já feitos, a projeção da dívida até o fim do mandato e a curva do prêmio de risco. Pública: a sala inteira vê. Recusa com 409 quando a partida não usa a expansão Governo & Política.",
)
def get_budget(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_budget()


@government_router.get(
    "/initial-account",
    response_model=InitialAccountDTO,
    summary="Obter a conta inicial do governo",
    description="Para uma data de início, mostra o que a partida herda nas duas contas iniciais: a dívida do fim do ano anterior em % do PIB, o resultado primário (zero na jogável, o real do ano de início na realista) e o prêmio de risco que a dívida já cobra. Antes de a sala existir, o lobby usa para explicar a escolha.",
)
def get_initial_account(user: CurrentUser, start: date):
    return build_initial_account(start)


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
    description="Mostra o que a medida faria sem propô-la: faixa na régua, marca do governo antes e depois, pontos na aprovação, chance no próximo voto, quando passaria a valer, o efeito estimado no orçamento (imposto atingido, receita, resultado e dívida no fim do mandato) e, nas medidas de setor, quem tem os ativos atingidos.",
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
