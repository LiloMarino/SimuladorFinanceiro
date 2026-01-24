from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.order import OrderDTO
from backend.core.dto.stock_details import StockDetailsDTO
from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
    OrderType,
)

operation_router = APIRouter(prefix="/api", tags=["Operations"])


class SubmitOrderRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    type: str
    action: str
    limit_price: float | None = None


class CancelOrderRequest(BaseModel):
    order_id: str


class BuyFixedIncomeRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class SubmitOrderResponse(BaseModel):
    order_id: str
    status: str


@operation_router.get(
    "/variable-income",
    response_model=list[CandleDTO],
    summary="Listar ativos de renda variável",
    description="Retorna a lista de todos os ativos de renda variável (ações) disponíveis na simulação.",
)
def get_variable_income(simulation: ActiveSimulation):
    """
    Lista todos os ativos de renda variável.
    """
    stocks = simulation.get_stocks()
    return stocks


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
        raise NotFoundError("Asset not found.")
    return stock


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
    size = payload.quantity
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

    if order_type_enum == OrderType.MARKET:
        order = MarketOrder(
            client_id=client_id, ticker=asset, size=size, action=action_enum
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

    simulation.create_order(order)
    return SubmitOrderResponse(order_id=order.id, status=order.status.name)


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

    canceled = simulation.cancel_order(order_id=order_id, client_id=client_id)
    if not canceled:
        raise NotFoundError("Ordem não encontrada")


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
    response_model=list[FixedIncomeAssetDTO],
    summary="Listar ativos de renda fixa",
    description="Retorna a lista de todos os ativos de renda fixa disponíveis na simulação.",
)
def get_fixed_income(simulation: ActiveSimulation):
    """
    Lista todos os ativos de renda fixa.
    """
    fixed = simulation.get_fixed_assets()
    return fixed


@operation_router.get(
    "/fixed-income/{asset_uuid}",
    response_model=FixedIncomeAssetDTO | None,
    summary="Obter detalhes de renda fixa",
    description="Retorna as informações detalhadas de um ativo de renda fixa específico.",
)
def get_fixed_income_details(simulation: ActiveSimulation, asset_uuid: str):
    """
    Retorna os detalhes de um ativo de renda fixa.
    """
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Asset not found.")
    return fixed


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

    simulation._engine.fixed_broker.buy(client_id, fixed, quantity)
