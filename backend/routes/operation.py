import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field, model_validator

from backend.core import repository
from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.candle import MarketQuoteDTO
from backend.core.dto.candle_challenge import AnswerChallengeRequest, CandleChallengeDTO
from backend.core.dto.candle_patterns import CandlePatternsDTO
from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import (
    FixedIncomeQuoteDTO,
    FixedIncomeRedemptionQuoteDTO,
)
from backend.core.dto.order import OrderDTO
from backend.core.dto.order_preview import OrderPreviewDTO, TradeDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.dto.technical_indicators import (
    IndicatorsRequestDTO,
    TechnicalIndicatorsDTO,
)
from backend.core.enum import OrderAction, OrderType
from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.user_manager import UserManager
from backend.features.candle_challenge import service as candle_challenge
from backend.features.technical_analysis.assistance import ensure_chart_hints
from backend.features.technical_analysis.patterns import build_candle_patterns
from backend.features.technical_analysis.summary import (
    build_technical_indicators,
    price_frame,
)
from backend.features.variable_income.broker import to_money
from backend.features.variable_income.entities.order import LimitOrder, MarketOrder

logger = logging.getLogger(__name__)

operation_router = APIRouter(prefix="/api", tags=["Operations"])


class SubmitOrderRequest(BaseModel):
    # Uma das duas: a quantidade, ou o valor que a compra a mercado pode gastar
    quantity: Decimal | None = Field(default=None, gt=0, decimal_places=8)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    type: str
    action: str
    limit_price: float | None = None

    @model_validator(mode="after")
    def exactly_one_size(self):
        if (self.quantity is None) == (self.amount is None):
            raise ValueError("Informe a quantidade ou o valor da ordem")
        return self


class CancelOrderRequest(BaseModel):
    order_id: str


class RedeemFixedIncomeRequest(BaseModel):
    # Quanto o jogador quer receber no caixa, líquido de IOF e IR
    amount: Decimal = Field(..., gt=0)


class BuyFixedIncomeRequest(BaseModel):
    quantity: Decimal = Field(..., gt=0)


class SubmitOrderResponse(BaseModel):
    order_id: str
    status: str
    # O que a ordem executou; na compra a mercado que parou no caixa ou no valor, menos que o pedido
    quantity: Decimal
    # O que a execução movimentou em reais (quantidade x preço de cada fatia)
    total: Decimal


@operation_router.get(
    "/variable-income",
    response_model=list[MarketQuoteDTO],
    summary="Listar ativos de renda variável",
    description="Retorna os ativos de renda variável com a cotação do dia, os últimos 30 fechamentos e o setor.",
)
def get_variable_income(simulation: ActiveSimulation):
    """
    Lista todos os ativos de renda variável.
    """
    return simulation.get_market()


@operation_router.get(
    "/variable-income/{asset}",
    response_model=StockDetailsDTO | None,
    summary="Obter detalhes de um ativo",
    description="Retorna as informações detalhadas de um ativo de renda variável específico.",
)
def get_variable_income_details(simulation: ActiveSimulation, asset: str):
    """
    Retorna os detalhes de um ativo de renda variável.
    """
    stock = simulation.get_stock_details(asset)
    if not stock:
        raise NotFoundError("Ativo não encontrado.")
    return stock


@operation_router.post(
    "/variable-income/{asset}/indicators",
    response_model=TechnicalIndicatorsDTO,
    summary="Indicadores técnicos de um ativo",
    description=(
        "Calcula os indicadores técnicos sobre o mesmo histórico do gráfico do ativo, "
        "que termina na data da simulação, com os parâmetros enviados. Devolve as "
        "séries pedidas em `series` e o Resumo técnico do dia, que conta todos os "
        "indicadores."
    ),
)
def get_variable_income_indicators(
    simulation: ActiveSimulation, asset: str, payload: IndicatorsRequestDTO
):
    stock = simulation.get_stock_details(asset)
    if not stock:
        raise NotFoundError("Ativo não encontrado.")
    return build_technical_indicators(price_frame(stock.history), payload)


@operation_router.get(
    "/variable-income/{asset}/patterns",
    response_model=CandlePatternsDTO,
    summary="Padrões de vela de um ativo",
    description=(
        "Os padrões de vela do histórico do ativo até a data da simulação, cada um com a "
        "variação do preço 5 pregões depois e se foi para o lado que o padrão sugere, e "
        "quantas vezes cada padrão acertou. Recusa quando as dicas de análise técnica "
        "estão desligadas na partida."
    ),
)
def get_variable_income_patterns(simulation: ActiveSimulation, asset: str):
    ensure_chart_hints(simulation.settings)
    stock = simulation.get_stock_details(asset)
    if not stock:
        raise NotFoundError("Ativo não encontrado.")
    return build_candle_patterns(price_frame(stock.history))


@operation_router.get(
    "/variable-income/{asset}/challenge",
    response_model=CandleChallengeDTO,
    summary="Desafio da vela de um ativo",
    description=(
        "A pergunta de hoje (um padrão de vela que fechou no último pregão e ainda não "
        "foi respondido), a última resposta do jogador nesse ativo e o placar dele na "
        "partida. Recusa quando as dicas de análise técnica estão desligadas."
    ),
)
def get_candle_challenge(simulation: ActiveSimulation, client_id: ClientID, asset: str):
    ensure_chart_hints(simulation.settings)
    user_id = UserManager.get_user_id(client_id)
    # A resposta vale até o próximo pregão: ler e gravar acontecem no mesmo dia
    with simulation.lock:
        stock = simulation.get_stock_details(asset)
        if not stock:
            raise NotFoundError("Ativo não encontrado.")
        return candle_challenge.current(
            simulation.settings.id, user_id, asset, price_frame(stock.history)
        )


@operation_router.post(
    "/variable-income/{asset}/challenge",
    response_model=CandleChallengeDTO,
    summary="Responder ao desafio da vela",
    description=(
        "Grava a resposta (sobe ou desce) ao padrão de hoje. Só vale enquanto o último "
        "pregão for o do padrão, uma vez por padrão; a conferência vem no fechamento do "
        "5º pregão depois dele."
    ),
)
def answer_candle_challenge(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: AnswerChallengeRequest,
):
    ensure_chart_hints(simulation.settings)
    user_id = UserManager.get_user_id(client_id)
    with simulation.lock:
        stock = simulation.get_stock_details(asset)
        if not stock:
            raise NotFoundError("Ativo não encontrado.")
        return candle_challenge.answer(
            simulation.settings.id,
            user_id,
            asset,
            payload.direction,
            price_frame(stock.history),
        )


@operation_router.post(
    "/variable-income/{asset}/orders",
    response_model=SubmitOrderResponse,
    summary="Submeter ordem de compra/venda",
    description="Cria e submete uma nova ordem (MARKET ou LIMIT) para o ativo especificado.",
)
def submit_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: SubmitOrderRequest,
):
    """
    Submete uma nova ordem para o ativo.
    """
    order_type: str = payload.type.lower()
    action: str = payload.action.lower()

    # Valida os parâmetros
    try:
        action_enum = OrderAction(action.lower())
    except ValueError as e:
        raise UnprocessableEntityError("Ação inválida") from e
    try:
        order_type_enum = OrderType(order_type.lower())
    except ValueError as e:
        raise UnprocessableEntityError("Tipo de ordem inválido") from e

    if payload.amount is not None and not (
        order_type_enum == OrderType.MARKET and action_enum == OrderAction.BUY
    ):
        raise UnprocessableEntityError("O valor só vale na compra a mercado")

    # Na compra por valor a quantidade nasce no create_order, com o book de agora
    size = payload.quantity if payload.quantity is not None else Decimal(0)
    if order_type_enum == OrderType.MARKET:
        order = MarketOrder(
            client_id=client_id,
            ticker=asset,
            size=size,
            action=action_enum,
            budget=payload.amount,
        )
    else:
        price = payload.limit_price
        if price is None:
            raise UnprocessableEntityError(
                "limit_price é obrigatório para ordem limitada"
            )
        order = LimitOrder(
            client_id=client_id,
            ticker=asset,
            size=size,
            action=action_enum,
            price=price,
        )

    logger.debug(
        "Ordem recebida: %s %s %sx %s (cliente %s)",
        order_type_enum.value,
        action_enum.value,
        size,
        asset,
        client_id,
    )
    simulation.create_order(order)
    return SubmitOrderResponse(
        order_id=order.id,
        status=order.status.name,
        quantity=order.size,
        total=to_money(order.notional).quantize(Decimal("0.01")),
    )


@operation_router.delete(
    "/variable-income/{asset}/orders",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar ordem",
    description="Remove uma ordem ativa do livro de ordens para o ativo informado.",
)
def cancel_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: CancelOrderRequest,
):
    """
    Cancela uma ordem existente.
    """
    order_id = payload.order_id
    logger.debug("Cancelamento recebido: ordem %s de %s", order_id, asset)

    canceled = simulation.cancel_order(order_id=order_id, client_id=client_id)
    if not canceled:
        raise NotFoundError("Ordem não encontrada")


class OrderPreviewRequest(BaseModel):
    action: OrderAction
    # Uma das duas: a quantidade, ou o valor da compra a mercado
    quantity: Decimal | None = Field(default=None, ge=0, decimal_places=8)
    amount: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    limit_price: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def exactly_one_size(self):
        if (self.quantity is None) == (self.amount is None):
            raise ValueError("Informe a quantidade ou o valor da ordem")
        if self.amount is not None and (
            self.action != OrderAction.BUY or self.limit_price is not None
        ):
            raise ValueError("O valor só vale na compra a mercado")
        return self


@operation_router.post(
    "/variable-income/{asset}/order-preview",
    response_model=OrderPreviewDTO,
    summary="Prévia de uma ordem",
    description="Preço estimado, total, caixa antes e depois, quantidade máxima e, na venda, o lucro e o IR que a ordem acrescenta ao mês.",
)
def preview_order(
    client_id: ClientID,
    simulation: ActiveSimulation,
    asset: str,
    payload: OrderPreviewRequest,
):
    return simulation.preview_order(
        client_id,
        asset,
        payload.action,
        payload.quantity,
        payload.limit_price,
        payload.amount,
    )


# Execuções mostradas na aba Histórico do livro de ofertas
TRADES_LIMIT = 50


@operation_router.get(
    "/variable-income/{asset}/trades",
    response_model=list[TradeDTO],
    summary="Execuções da sala no ativo",
    description="As últimas compras e vendas executadas por todos os jogadores da partida no ativo, mais recentes primeiro.",
)
def list_trades(_: ActiveSimulation, asset: str):
    return repository.portfolio.get_trades(asset, TRADES_LIMIT)


@operation_router.get(
    "/variable-income/{asset}/orders",
    response_model=list[OrderDTO],
    summary="Listar ordens do livro",
    description="Lista todas as ordens ativas (BUY + SELL) no livro de ordens para o ativo especificado.",
)
def list_order_book(simulation: ActiveSimulation, asset: str):
    """
    Lista todas as ordens no livro de ordens do ativo.
    """
    orders = simulation.get_orders(asset)
    return orders


@operation_router.get(
    "/fixed-income",
    response_model=list[FixedIncomeOfferDTO],
    summary="Listar ativos de renda fixa",
    description="Retorna os títulos de renda fixa disponíveis com a taxa equivalente do dia, a isenção e a alíquota de IR no vencimento.",
)
def get_fixed_income(simulation: ActiveSimulation):
    """
    Lista todos os ativos de renda fixa.
    """
    return simulation.get_fixed_offers()


@operation_router.get(
    "/fixed-income/{asset_uuid}",
    response_model=FixedIncomeOfferDTO,
    summary="Obter detalhes de renda fixa",
    description="Retorna o título com a taxa equivalente do dia, a isenção e a alíquota de IR no vencimento.",
)
def get_fixed_income_details(simulation: ActiveSimulation, asset_uuid: str):
    """
    Retorna os detalhes de um ativo de renda fixa.
    """
    fixed = simulation.get_fixed_offer(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo não encontrado.")
    return fixed


@operation_router.get(
    "/fixed-income/{asset_uuid}/projection",
    response_model=FixedIncomeQuoteDTO,
    summary="Projetar investimento em renda fixa",
    description="Projeta o valor aplicado hoje até o vencimento: bruto, IR e líquido. Pós-fixados usam o último valor conhecido do indexador.",
)
def get_fixed_income_projection(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
    amount: Annotated[Decimal, Query(ge=0)] = Decimal(0),
):
    """
    Projeta um investimento no ativo de renda fixa.
    """
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")
    return simulation.quote_fixed_income(client_id, fixed, amount)


@operation_router.post(
    "/fixed-income/{asset_uuid}/buy",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Comprar ativo de renda fixa",
    description="Realiza a compra de um ativo de renda fixa com a quantidade especificada.",
)
def buy_fixed_income(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
    payload: BuyFixedIncomeRequest,
):
    """
    Compra um ativo de renda fixa.
    """
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")

    quantity = payload.quantity

    simulation.buy_fixed_income(client_id, fixed, quantity)


@operation_router.get(
    "/fixed-income/{asset_uuid}/redemption",
    response_model=FixedIncomeRedemptionQuoteDTO,
    summary="Cotar resgate de renda fixa",
    description="Cota o resgate hoje de um título de liquidez diária: o bruto que sai do título, o IOF, o IR e o líquido que chega ao caixa.",
)
def get_fixed_income_redemption(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
    amount: Annotated[Decimal, Query(ge=0)] = Decimal(0),
):
    """
    Cota o resgate de uma posição de liquidez diária.
    """
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")
    return simulation.quote_fixed_redemption(client_id, fixed, amount)


@operation_router.post(
    "/fixed-income/{asset_uuid}/redeem",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resgatar ativo de renda fixa",
    description="Resgata de um título de liquidez diária o valor líquido que o jogador quer receber no caixa.",
)
def redeem_fixed_income(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
    payload: RedeemFixedIncomeRequest,
):
    """
    Resgata um ativo de renda fixa de liquidez diária.
    """
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")

    simulation.redeem_fixed_income(client_id, fixed, payload.amount)
