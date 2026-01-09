from fastapi import APIRouter, status
from pydantic import BaseModel

from backend.core.exceptions.http_exceptions import (
    NotFoundError,
    UnprocessableEntityError,
)
from backend.fastapi_deps import ActiveSimulation, ClientID
from backend.fastapi_helpers import make_response
from backend.features.variable_income.entities.order import (
    LimitOrder,
    MarketOrder,
    OrderAction,
    OrderType,
)

operation_router = APIRouter(prefix="/api", tags=["operations"])


# Request models
class SubmitOrderRequest(BaseModel):
    quantity: int
    type: str
    action: str
    limit_price: float | None = None


class CancelOrderRequest(BaseModel):
    order_id: str


class BuyFixedIncomeRequest(BaseModel):
    quantity: int


@operation_router.get("/variable-income")
def get_variable_income(simulation: ActiveSimulation):
    """Return list of stocks."""
    stocks = simulation.get_stocks()
    return make_response(
        True, "Stocks loaded successfully.", data=[s.to_json() for s in stocks]
    )


@operation_router.get("/variable-income/{asset}")
def get_variable_income_details(simulation: ActiveSimulation, asset: str):
    """Return details of a specific stock."""
    stock = simulation.get_stock_details(asset)
    if not stock:
        return make_response(
            False, "Asset not found.", status_code=status.HTTP_404_NOT_FOUND
        )
    return make_response(True, "Asset details loaded.", data=stock.to_json())


@operation_router.post("/variable-income/{asset}/orders")
def submit_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: SubmitOrderRequest,
):
    # Valida os parâmetros
    if not payload.quantity:
        raise UnprocessableEntityError("Quantidade é obrigatória")
    try:
        action_enum = OrderAction(payload.action.lower())
    except ValueError as e:
        raise UnprocessableEntityError("Ação inválida") from e
    try:
        order_type_enum = OrderType(payload.type.lower())
    except ValueError as e:
        raise UnprocessableEntityError("Tipo de ordem inválido") from e

    if order_type_enum == OrderType.MARKET:
        order = MarketOrder(
            client_id=client_id, ticker=asset, size=payload.quantity, action=action_enum
        )
    else:
        if payload.limit_price is None:
            raise UnprocessableEntityError(
                "limit_price é obrigatório para ordem limitada"
            )
        order = LimitOrder(
            client_id=client_id,
            ticker=asset,
            size=payload.quantity,
            action=action_enum,
            price=payload.limit_price,
        )

    simulation.create_order(order)
    return make_response(
        True,
        "Order submitted successfully.",
        data={"order_id": order.id, "status": order.status.name},
    )


@operation_router.delete("/variable-income/{asset}/orders")
def cancel_order(
    simulation: ActiveSimulation,
    client_id: ClientID,
    asset: str,
    payload: CancelOrderRequest,
):
    if not payload.order_id:
        raise UnprocessableEntityError("order_id é obrigatório")

    canceled = simulation.cancel_order(order_id=payload.order_id, client_id=client_id)
    if not canceled:
        raise NotFoundError("Ordem não encontrada")
    return make_response(True, "Order canceled successfully.")


@operation_router.get("/variable-income/{asset}/orders")
def list_order_book(simulation: ActiveSimulation, asset: str):
    """Lista todas as ordens (BUY + SELL) no book para o ativo"""
    orders = simulation.get_orders(asset)
    return make_response(
        True,
        "Order book loaded.",
        data=[o.to_json() for o in orders],
    )


@operation_router.get("/fixed-income")
def get_fixed_income(simulation: ActiveSimulation):
    """Return list of fixed-income assets."""
    fixed = simulation.get_fixed_assets()
    fixed_json = [asset.to_json() for asset in fixed]
    return make_response(True, "Fixed income assets loaded.", data=fixed_json)


@operation_router.get("/fixed-income/{asset_uuid}")
def get_fixed_income_details(simulation: ActiveSimulation, asset_uuid: str):
    """Return details of a fixed-income asset."""
    fixed = simulation.get_fixed_asset(asset_uuid)
    if not fixed:
        return make_response(
            False, "Asset not found.", status_code=status.HTTP_404_NOT_FOUND
        )
    return make_response(True, "Asset details loaded.", data=fixed.to_json())


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

    if not payload.quantity:
        raise UnprocessableEntityError("Quantidade é obrigatória")

    simulation._engine.fixed_broker.buy(client_id, fixed, payload.quantity)

    return make_response(True, "Investment queued successfully.")
