"""
Variable and fixed income operation routes for FastAPI.
Migrated from Flask Blueprint to FastAPI APIRouter.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.dependencies import ActiveSimulation, ClientID
from backend.core.exceptions.fastapi_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
    OrderType,
)
from backend.routes.fastapi_helpers import make_response_data

router = APIRouter(prefix="/api", tags=["operations"])


# Request models
class SubmitOrderRequest(BaseModel):
    quantity: int
    type: str  # "market" or "limit"
    action: str  # "buy" or "sell"
    limit_price: float | None = None


class CancelOrderRequest(BaseModel):
    order_id: str


class BuyFixedIncomeRequest(BaseModel):
    quantity: int


# Variable Income Routes
@router.get("/variable-income")
async def get_variable_income(simulation: ActiveSimulation):
    """Return list of stocks."""
    stocks = simulation.get_stocks()
    return make_response_data(
        True, "Stocks loaded successfully.", data=[s.to_json() for s in stocks]
    )


@router.get("/variable-income/{asset}")
async def get_variable_income_details(simulation: ActiveSimulation, asset: str):
    """Return details of a specific stock."""
    stock = simulation.get_stock_details(asset)
    if not stock:
        raise NotFoundError("Asset not found.")
    return make_response_data(True, "Asset details loaded.", data=stock.to_json())


@router.post("/variable-income/{asset}/orders")
async def submit_order(
    request: SubmitOrderRequest,
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
):
    """Submit a new order (market or limit)."""
    size = request.quantity
    order_type = request.type.lower()
    action = request.action.lower()

    # Valida os parâmetros
    if not size:
        raise UnprocessableEntityError("Quantidade é obrigatória")
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
        price = request.limit_price
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
    return make_response_data(
        True,
        "Order submitted successfully.",
        data={"order_id": order.id, "status": order.status.name},
    )


@router.delete("/variable-income/{asset}/orders")
async def cancel_order(
    request: CancelOrderRequest,
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
):
    """Cancel an existing order."""
    order_id = request.order_id
    if not order_id:
        raise UnprocessableEntityError("order_id é obrigatório")

    canceled = simulation.cancel_order(order_id=order_id, client_id=client_id)
    if not canceled:
        raise NotFoundError("Ordem não encontrada")
    return make_response_data(True, "Order canceled successfully.")


@router.get("/variable-income/{asset}/orders")
async def list_order_book(simulation: ActiveSimulation, asset: str):
    """Lista todas as ordens (BUY + SELL) no book para o ativo."""
    orders = simulation.get_orders(asset)
    return make_response_data(
        True,
        "Order book loaded.",
        data=[o.to_json() for o in orders],
    )


# Fixed Income Routes
@router.get("/fixed-income")
async def get_fixed_income(simulation: ActiveSimulation):
    """Return list of fixed-income assets."""
    fixed = simulation.get_fixed_assets()
    fixed_json = [asset.to_json() for asset in fixed]
    return make_response_data(True, "Fixed income assets loaded.", data=fixed_json)


@router.get("/fixed-income/{asset_uuid}")
async def get_fixed_income_details(simulation: ActiveSimulation, asset_uuid: str):
    """Return details of a fixed-income asset."""
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Asset not found.")
    return make_response_data(True, "Asset details loaded.", data=fixed.to_json())


@router.post("/fixed-income/{asset_uuid}/buy")
async def buy_fixed_income(
    request: BuyFixedIncomeRequest,
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset_uuid: str,
):
    """Buy fixed-income assets."""
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        raise NotFoundError("Ativo de renda fixa não encontrado")

    quantity = request.quantity
    if not quantity:
        raise UnprocessableEntityError("Quantidade é obrigatória")

    simulation._engine.fixed_broker.buy(client_id, fixed, quantity)

    return make_response_data(True, "Investment queued successfully.")
