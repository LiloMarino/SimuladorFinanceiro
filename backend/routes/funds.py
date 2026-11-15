from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query, status

from backend.core.dto.fund import (
    FundAccountDTO,
    FundAssemblyConveneRequest,
    FundAssemblyVoteRequest,
    FundBuybackDTO,
    FundBuybackPreviewDTO,
    FundBuybackRequest,
    FundComanagerInviteRequest,
    FundComanagerShareRequest,
    FundContributionRequest,
    FundContributionResponse,
    FundDetailsDTO,
    FundDistributionRequest,
    FundFeesRequest,
    FundFoundRequest,
    FundIssuanceDTO,
    FundIssuancePreviewDTO,
    FundIssuanceRequest,
    FundIssuanceSubscriptionPreviewDTO,
    FundIssuanceSubscriptionRequest,
    FundOfferRequest,
    FundSummaryDTO,
    FundTickerCheckDTO,
)
from backend.routes.dependencies import ActiveSimulation, CurrentUser

funds_router = APIRouter(prefix="/api/funds", tags=["Funds"])


@funds_router.get(
    "",
    response_model=list[FundSummaryDTO],
    summary="Listar as gestoras da partida",
    description="Cada gestora com os termos, o PL por cota de agora e o preço de ranking.",
)
def get_funds(simulation: ActiveSimulation):
    return simulation.get_funds()


@funds_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FundSummaryDTO,
    summary="Fundar uma gestora",
    description="O ticker tem quatro letras e o sufixo 11 e fica reservado ao fundador. A gestora nasce sem cotas: o gestor integraliza antes de abrir a oferta.",
)
def found_fund(
    simulation: ActiveSimulation, user: CurrentUser, payload: FundFoundRequest
):
    return simulation.found_fund(user, payload)


@funds_router.get(
    "/accounts",
    response_model=list[FundAccountDTO],
    summary="Listar as contas com que o jogador opera",
    description="A conta pessoal primeiro e depois cada gestora que o jogador gere, com o caixa de cada uma e o último dia do congelamento, quando o gestor governa o país.",
)
def get_fund_accounts(simulation: ActiveSimulation, user: CurrentUser):
    return simulation.get_fund_accounts(user)


@funds_router.get(
    "/ticker-check",
    response_model=FundTickerCheckDTO,
    summary="Conferir a sigla de uma gestora",
    description="Diz se a sigla está livre, fora do formato (quatro letras e 11), é de um ativo ou já é de uma gestora (com o nome do dono). Não altera nada.",
)
def check_fund_ticker(simulation: ActiveSimulation, user: CurrentUser, ticker: str):
    return simulation.check_fund_ticker(user, ticker)


@funds_router.get(
    "/{fund_id}",
    response_model=FundDetailsDTO,
    summary="Detalhar uma gestora",
    description="Quem tem as cotas, a composição, o desempenho de 12 meses contra o CDI, a série de preço e PL, o último relatório mensal, as taxas, os movimentos, a oferta em andamento e as cotas de quem consulta. A carteira posição a posição e o quanto o gestor vende sem perder o controle só vêm para o gestor.",
)
def get_fund(simulation: ActiveSimulation, user: CurrentUser, fund_id: int):
    return simulation.get_fund(user, fund_id)


@funds_router.post(
    "/{fund_id}/contributions",
    response_model=FundContributionResponse,
    summary="Integralizar a gestora",
    description="O gestor passa caixa e ações da própria carteira à gestora e recebe cotas ao patrimônio líquido do dia (100 por cota na primeira integralização). Só vale antes da oferta pública.",
)
def contribute_to_fund(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundContributionRequest,
):
    return simulation.contribute_to_fund(user, fund_id, payload)


@funds_router.post(
    "/{fund_id}/offer",
    response_model=FundSummaryDTO,
    summary="Abrir a oferta pública",
    description="Põe à venda, ao patrimônio líquido do dia, a quantidade de cotas informada. A oferta abre uma vez só, lista a cota no mercado e dura cinco pregões, contando o da abertura.",
)
def open_fund_offer(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundOfferRequest,
):
    return simulation.open_fund_offer(user, fund_id, payload.quotas)


@funds_router.delete(
    "/{fund_id}/offer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Encerrar a oferta pública",
    description="Retira do mercado as cotas da oferta que ainda não foram vendidas. A oferta também fecha sozinha ao fim do quinto pregão.",
)
def close_fund_offer(simulation: ActiveSimulation, user: CurrentUser, fund_id: int):
    simulation.close_fund_offer(user, fund_id)


@funds_router.post(
    "/{fund_id}/issuance",
    status_code=status.HTTP_201_CREATED,
    response_model=FundIssuanceDTO,
    summary="Anunciar a emissão de cotas",
    description="Emite cotas novas ao patrimônio líquido por cota do dia, com o preço fixo até o fim. Os cotistas jogadores têm dez pregões de preferência, na proporção que tinham no anúncio; depois a sobra abre a todos por cinco pregões e o que não vender não nasce. O dinheiro entra no caixa da gestora.",
)
def announce_fund_issuance(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundIssuanceRequest,
):
    return simulation.announce_fund_issuance(user, fund_id, payload)


@funds_router.post(
    "/{fund_id}/issuance/subscriptions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Comprar na preferência da emissão",
    description="O cotista compra cotas novas ao preço fixo da emissão, até o direito que a proporção dele no anúncio deu. Vale só nos pregões da preferência.",
)
def subscribe_fund_issuance(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundIssuanceSubscriptionRequest,
):
    simulation.subscribe_fund_issuance(user, fund_id, payload)


@funds_router.get(
    "/{fund_id}/issuance/preview",
    response_model=FundIssuancePreviewDTO,
    summary="Prever uma emissão",
    description="Ao PL por cota de hoje: o caixa que a emissão traz, o direito de preferência do gestor e o controle dele se comprar ou não. Só o gestor consulta; não altera nada.",
)
def preview_fund_issuance(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    quotas: Annotated[int, Query(gt=0)],
):
    return simulation.preview_fund_issuance(user, fund_id, quotas)


@funds_router.get(
    "/{fund_id}/issuance/subscription-preview",
    response_model=FundIssuanceSubscriptionPreviewDTO,
    summary="Prever a compra na preferência",
    description="O custo, o caixa pessoal e a parte do jogador depois de comprar a quantidade de cotas informada. Não altera nada.",
)
def preview_fund_subscription(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    quotas: Annotated[int, Query(gt=0)],
):
    return simulation.preview_fund_subscription(user, fund_id, quotas)


@funds_router.post(
    "/{fund_id}/buyback",
    status_code=status.HTTP_201_CREATED,
    response_model=FundBuybackDTO,
    summary="Abrir a recompra de cotas",
    description="Põe no livro uma ordem de compra da gestora pela quantidade e até o preço máximo informados, paga com o caixa dela. As cotas compradas deixam de existir. Uma recompra por vez, e a ordem não casa com cotas do próprio gestor.",
)
def open_fund_buyback(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundBuybackRequest,
):
    return simulation.open_fund_buyback(user, fund_id, payload)


@funds_router.delete(
    "/{fund_id}/buyback",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar o resto da recompra",
    description="Tira do livro o que a recompra ainda não comprou e devolve o caixa reservado. O que já foi comprado fica queimado.",
)
def cancel_fund_buyback(simulation: ActiveSimulation, user: CurrentUser, fund_id: int):
    simulation.cancel_fund_buyback(user, fund_id)


@funds_router.post(
    "/{fund_id}/assembly",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Convocar a assembleia de troca de gestor",
    description="Quem tem 10% ou mais das cotas convoca, indicando a si mesmo ou um aliado jogador para a gestão. Indicado o próprio convocador, a votação abre já por 5 pregões; um aliado tem 5 pregões para aceitar. Uma assembleia a cada 3 meses por gestora; durante ela a gestora não emite cotas.",
)
def convene_fund_assembly(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundAssemblyConveneRequest,
):
    simulation.convene_fund_assembly(user, fund_id, payload)


@funds_router.delete(
    "/{fund_id}/assembly",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar o convite da assembleia",
    description="Quem convocou cancela o convite que o aliado ainda não respondeu. O cancelamento não conta no intervalo entre assembleias.",
)
def cancel_fund_assembly(simulation: ActiveSimulation, user: CurrentUser, fund_id: int):
    simulation.cancel_fund_assembly(user, fund_id)


@funds_router.post(
    "/{fund_id}/assembly/acceptance",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Aceitar o convite da assembleia",
    description="O aliado indicado aceita e a votação abre, com quem convocou a favor.",
)
def accept_fund_assembly_invite(
    simulation: ActiveSimulation, user: CurrentUser, fund_id: int
):
    simulation.answer_fund_assembly_invite(user, fund_id, True)


@funds_router.post(
    "/{fund_id}/assembly/refusal",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Recusar o convite da assembleia",
    description="O aliado indicado recusa e a assembleia se encerra, sem contar no intervalo entre assembleias.",
)
def refuse_fund_assembly_invite(
    simulation: ActiveSimulation, user: CurrentUser, fund_id: int
):
    simulation.answer_fund_assembly_invite(user, fund_id, False)


@funds_router.put(
    "/{fund_id}/assembly/vote",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Votar na assembleia",
    description="O cotista vota a favor ou contra a troca, e muda o voto até o fim da votação. O peso é o das cotas dele no fechamento do último pregão. O gestor não vota: as cotas dele contam contra.",
)
def vote_fund_assembly(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundAssemblyVoteRequest,
):
    simulation.vote_fund_assembly(user, fund_id, payload)


@funds_router.post(
    "/{fund_id}/comanagers",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Convidar um co-gestor",
    description="O gestor principal convida um jogador (bot não) a operar a carteira e dividir as taxas. O convite reserva a parte, vale por 7 dias e a gestora aceita até 3 co-gestores, contando os convites. O co-gestor só opera a carteira.",
)
def invite_fund_comanager(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundComanagerInviteRequest,
):
    simulation.invite_fund_comanager(user, fund_id, payload)


@funds_router.post(
    "/{fund_id}/comanagers/acceptance",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Aceitar o convite de co-gestão",
    description="O convidado passa a operar a carteira da gestora na hora; a parte dele vale nas taxas do mês seguinte.",
)
def accept_fund_comanager_invite(
    simulation: ActiveSimulation, user: CurrentUser, fund_id: int
):
    simulation.answer_fund_comanager_invite(user, fund_id, True)


@funds_router.post(
    "/{fund_id}/comanagers/refusal",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Recusar o convite de co-gestão",
    description="O convite some e a parte reservada volta ao gestor principal.",
)
def refuse_fund_comanager_invite(
    simulation: ActiveSimulation, user: CurrentUser, fund_id: int
):
    simulation.answer_fund_comanager_invite(user, fund_id, False)


@funds_router.delete(
    "/{fund_id}/comanagers/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair da co-gestão",
    description="O co-gestor deixa a gestão e o acesso à carteira cai no mesmo pregão. A parte dele volta ao gestor principal na próxima divisão de taxa.",
)
def leave_fund_comanagement(
    simulation: ActiveSimulation, user: CurrentUser, fund_id: int
):
    simulation.leave_fund_comanagement(user, fund_id)


@funds_router.put(
    "/{fund_id}/comanagers/{comanager_user_id}/share",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mudar a parte de um co-gestor",
    description="A parte nova vale nas taxas do mês seguinte; as partes dos co-gestores precisam deixar parte para o gestor principal. Pedir a parte de hoje desfaz a mudança agendada.",
)
def change_fund_comanager_share(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    comanager_user_id: int,
    payload: FundComanagerShareRequest,
):
    simulation.change_fund_comanager_share(user, fund_id, comanager_user_id, payload)


@funds_router.delete(
    "/{fund_id}/comanagers/{comanager_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover um co-gestor ou retirar o convite",
    description="O gestor principal tira o co-gestor e o acesso cai no mesmo pregão; a parte volta a ele na próxima divisão de taxa. Num convite pendente, só o retira.",
)
def remove_fund_comanager(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    comanager_user_id: int,
):
    simulation.remove_fund_comanager(user, fund_id, comanager_user_id)


@funds_router.get(
    "/{fund_id}/buyback/preview",
    response_model=FundBuybackPreviewDTO,
    summary="Prever uma recompra",
    description="O custo ao preço máximo, quanto dele é ágio sobre o PL por cota, o caixa que sobra, o PL por cota de quem fica e o controle do gestor. Só o gestor consulta; não altera nada.",
)
def preview_fund_buyback(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    quantity: Annotated[int, Query(gt=0)],
    max_price: Annotated[Decimal, Query(gt=0, decimal_places=2)],
):
    return simulation.preview_fund_buyback(user, fund_id, quantity, max_price)


@funds_router.put(
    "/{fund_id}/distribution",
    response_model=FundSummaryDTO,
    summary="Mudar a parte do lucro que a gestora distribui",
    description="A parte do lucro realizado do mês que vira rendimento aos cotistas, de 0% a 100%. A nova parte fica pendente e vale a partir do primeiro dia útil do mês seguinte, junto das taxas.",
)
def set_fund_distribution(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundDistributionRequest,
):
    return simulation.set_fund_distribution(user, fund_id, payload)


@funds_router.put(
    "/{fund_id}/fees",
    response_model=FundSummaryDTO,
    summary="Mudar as taxas da gestora",
    description="As taxas novas ficam pendentes e valem a partir do primeiro dia útil do mês seguinte, dentro dos tetos da partida.",
)
def set_fund_fees(
    simulation: ActiveSimulation,
    user: CurrentUser,
    fund_id: int,
    payload: FundFeesRequest,
):
    return simulation.set_fund_fees(user, fund_id, payload)
