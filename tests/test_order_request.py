from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.enum import OrderAction
from backend.routes.operation import OrderPreviewRequest, SubmitOrderRequest


def test_submit_accepts_quantity_or_amount_but_not_both_or_none():
    assert SubmitOrderRequest(quantity=Decimal(5), type="market", action="buy")
    assert SubmitOrderRequest(amount=Decimal("100.50"), type="market", action="buy")
    with pytest.raises(ValidationError):
        SubmitOrderRequest(type="market", action="buy")
    with pytest.raises(ValidationError):
        SubmitOrderRequest(
            quantity=Decimal(5), amount=Decimal(100), type="market", action="buy"
        )


def test_preview_by_amount_is_only_a_market_buy():
    assert OrderPreviewRequest(action=OrderAction.BUY, amount=Decimal(100))
    with pytest.raises(ValidationError):
        OrderPreviewRequest(action=OrderAction.SELL, amount=Decimal(100))
    with pytest.raises(ValidationError):
        OrderPreviewRequest(action=OrderAction.BUY, amount=Decimal(100), limit_price=9)
    with pytest.raises(ValidationError):
        OrderPreviewRequest(action=OrderAction.BUY)


def test_submit_accepts_the_max_only_as_the_single_size():
    assert SubmitOrderRequest(max_size=True, type="limit", action="sell")
    with pytest.raises(ValidationError, match="exatamente um tamanho"):
        SubmitOrderRequest(
            max_size=True, type="market", action="buy", quantity=Decimal(5)
        )
    with pytest.raises(ValidationError, match="exatamente um tamanho"):
        SubmitOrderRequest(
            max_size=True, type="market", action="buy", amount=Decimal(100)
        )
    with pytest.raises(ValidationError, match="exatamente um tamanho"):
        SubmitOrderRequest(type="market", action="buy")


def test_preview_accepts_the_max_only_as_the_single_size():
    assert OrderPreviewRequest(action=OrderAction.SELL, max_size=True)
    assert OrderPreviewRequest(action=OrderAction.BUY, max_size=True, limit_price=9)
    with pytest.raises(ValidationError, match="exatamente um tamanho"):
        OrderPreviewRequest(action=OrderAction.BUY, max_size=True, quantity=Decimal(1))
    with pytest.raises(ValidationError):
        OrderPreviewRequest(action=OrderAction.BUY, max_size=True, amount=Decimal(100))
