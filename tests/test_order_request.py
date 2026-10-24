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
