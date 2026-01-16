from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.core.dependencies import ActiveSimulation, ClientID
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


@operation_router.get("/variable-income")
def get_variable_income(simulation: ActiveSimulation):
    """Return list of stocks."""
    stocks = simulation.get_stocks()
    return JSONResponse(content={"data": [s.to_json() for s in stocks]})


@operation_router.get("/variable-income/{asset}")
def get_variable_income_details(simulation: ActiveSimulation, asset: str):
    """Return details of a specific stock."""
    stock = simulation.get_stock_details(asset)
    if not stock:
        raise NotFoundError("Asset not found.")
    return JSONResponse(content={"data": stock.to_json()})


@operation_router.post("/variable-income/{asset}/orders")
def submit_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: SubmitOrderRequest,
):
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
    return JSONResponse(
        content={"data": {"order_id": order.id, "status": order.status.name}}
    )


@operation_router.delete("/variable-income/{asset}/orders")
def cancel_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: CancelOrderRequest,
):
    order_id = payload.order_id

    canceled = simulation.cancel_order(order_id=order_id, client_id=client_id)
    if not canceled:
        raise NotFoundError("Ordem não encontrada")
    return JSONResponse(content={"data": None})


@operation_router.get("/variable-income/{asset}/orders")
def list_order_book(simulation: ActiveSimulation, asset: str):
    """Lista todas as ordens (BUY + SELL) no book para o ativo"""
    orders = simulation.get_orders(asset)
    return JSONResponse(content={"data": [o.to_json() for o in orders]})


@operation_router.get("/fixed-income")
def get_fixed_income(simulation: ActiveSimulation):
    """Return list of fixed-income assets."""
    fixed = simulation.get_fixed_assets()
    fixed_json = [asset.to_json() for asset in fixed]
    return JSONResponse(content={"data": fixed_json})


@operation_router.get("/fixed-income/{asset_uuid}")
def get_fixed_income_details(simulation: ActiveSimulation, asset_uuid: str):
    """Return details of a fixed-income asset."""
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Asset not found.")
    return JSONResponse(content={"data": fixed.to_json()})


@operation_router.post("/fixed-income/{asset_uuid}/buy")
def buy_fixed_income(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
    payload: BuyFixedIncomeRequest,
):
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")

    quantity = payload.quantity

    simulation._engine.fixed_broker.buy(client_id, fixed, quantity)

    return JSONResponse(content={"data": None})
