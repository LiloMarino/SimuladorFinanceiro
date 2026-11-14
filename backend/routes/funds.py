from fastapi import APIRouter, status

from backend.core.dto.fund import (
    FundAccountDTO,
    FundContributionRequest,
    FundContributionResponse,
    FundDetailsDTO,
    FundFeesRequest,
    FundFoundRequest,
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
    description="Os termos, o PL por cota de agora e a série dos fechamentos dos pregões.",
)
def get_fund(simulation: ActiveSimulation, fund_id: int):
    return simulation.get_fund(fund_id)


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
