from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from backend.core.enum import OrderAction, OrderOwner
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    FUND_MAKER_CLIENT_ID,
    MARKET_CLIENT_ID,
    LimitOrder,
)
from backend.features.variable_income.order_book import OrderBook

T0 = datetime(2020, 1, 6, tzinfo=UTC)


def _limit(
    price: float,
    action: OrderAction,
    *,
    ticker: str = "ABCD",
    seconds: int = 0,
) -> LimitOrder:
    return LimitOrder(
        placed_on=date(2020, 1, 2),
        client_id=uuid.uuid4(),
        ticker=ticker,
        price=price,
        size=Decimal(1),
        action=action,
        created_at=T0 + timedelta(seconds=seconds),
    )


def test_best_buy_is_highest_price():
    """Melhor compra é a de maior preço."""
    book = OrderBook()
    best = _limit(11, OrderAction.BUY)
    book.add(_limit(10, OrderAction.BUY))
    book.add(best)
    book.add(_limit(9, OrderAction.BUY))

    assert book.best_buy("ABCD") is best


def test_best_sell_is_lowest_price():
    """Melhor venda é a de menor preço."""
    book = OrderBook()
    best = _limit(9, OrderAction.SELL)
    book.add(_limit(10, OrderAction.SELL))
    book.add(best)

    assert book.best_sell("ABCD") is best


def test_same_price_older_order_wins():
    """No mesmo preço, a ordem mais antiga tem prioridade."""
    book = OrderBook()
    newer = _limit(10, OrderAction.SELL, seconds=5)
    older = _limit(10, OrderAction.SELL, seconds=1)
    book.add(newer)
    book.add(older)

    assert book.best_sell("ABCD") is older


def test_removed_order_is_skipped_as_best():
    """Ordem removida some do topo, da busca e da listagem."""
    book = OrderBook()
    top = _limit(9, OrderAction.SELL)
    next_best = _limit(10, OrderAction.SELL)
    book.add(top)
    book.add(next_best)

    book.remove(top)

    assert book.best_sell("ABCD") is next_best
    assert book.find(top.id) is None
    assert book.get_orders("ABCD") == [next_best]


def test_empty_side_has_no_best():
    """Lado sem ordens não tem melhor oferta."""
    book = OrderBook()
    book.add(_limit(10, OrderAction.SELL))

    assert book.best_buy("ABCD") is None
    assert book.best_sell("WXYZ") is None


def test_get_orders_lists_both_sides_of_one_ticker():
    """Listagem traz compras e vendas do ticker pedido, e só dele."""
    book = OrderBook()
    buy = _limit(9, OrderAction.BUY)
    sell = _limit(11, OrderAction.SELL)
    book.add(buy)
    book.add(sell)
    book.add(_limit(5, OrderAction.BUY, ticker="WXYZ"))

    assert book.get_orders("ABCD") == [buy, sell]
    assert book.find(buy.id) is buy


def test_order_dto_carries_the_game_day_of_creation():
    """O "quando" da ordem é o dia da partida, não o relógio real."""
    order = LimitOrder(
        placed_on=date(2023, 5, 17),
        client_id=MARKET_CLIENT_ID,
        ticker="ABCD",
        price=10,
        size=Decimal(1),
        action=OrderAction.BUY,
    )

    assert order.to_dto().placed_on == date(2023, 5, 17)


def test_get_orders_follows_matching_priority():
    """Compras do maior para o menor preço, vendas do menor para o maior, e a mais antiga primeiro no empate."""
    book = OrderBook()
    buy_low = _limit(9, OrderAction.BUY, seconds=0)
    buy_high_late = _limit(11, OrderAction.BUY, seconds=5)
    buy_high_early = _limit(11, OrderAction.BUY, seconds=1)
    sell_high = _limit(14, OrderAction.SELL, seconds=0)
    sell_low = _limit(12, OrderAction.SELL, seconds=3)
    for order in (buy_low, buy_high_late, sell_high, buy_high_early, sell_low):
        book.add(order)

    assert book.get_orders("ABCD") == [
        buy_high_early,
        buy_high_late,
        buy_low,
        sell_low,
        sell_high,
    ]


def test_get_orders_skips_removed_orders_in_priority_order():
    """Ordem removida não aparece, e as demais seguem a prioridade."""
    book = OrderBook()
    top = _limit(11, OrderAction.BUY)
    next_best = _limit(10, OrderAction.BUY)
    book.add(next_best)
    book.add(top)

    book.remove(top)

    assert book.get_orders("ABCD") == [next_best]


def test_synthetic_owners_are_named_and_have_no_color():
    """Mercado, formador e oferta pública são donos sintéticos: sem cor e com o tipo de cada um."""
    for client_id, nickname, owner in (
        (MARKET_CLIENT_ID, "Mercado", OrderOwner.MARKET),
        (FUND_MAKER_CLIENT_ID, "Formador de mercado", OrderOwner.FUND_MAKER),
        (FUND_ISSUER_CLIENT_ID, "Oferta pública", OrderOwner.FUND_ISSUER),
    ):
        order = _limit(10, OrderAction.BUY)
        order.client_id = client_id

        dto = order.to_dto()

        assert (dto.player_nickname, dto.owner, dto.player_color) == (
            nickname,
            owner,
            None,
        )


def test_bot_order_dto_flags_the_robot(monkeypatch):
    """A ordem de um jogador sem pessoa por trás sai marcada como de robô."""
    bot = SimpleNamespace(id=7, nickname="Surfista", is_bot=True)
    monkeypatch.setattr(
        UserManager, "get_user", classmethod(lambda cls, _client_id: bot)
    )
    monkeypatch.setattr(
        UserManager, "get_color", classmethod(lambda cls, _user_id: "teal")
    )

    dto = _limit(10, OrderAction.BUY).to_dto()

    assert (dto.player_nickname, dto.owner, dto.player_color) == (
        "Surfista",
        OrderOwner.BOT,
        "teal",
    )


def test_player_order_dto_carries_the_player_color(monkeypatch):
    """O jogador aparece com o apelido e a cor da paleta dele."""
    player = SimpleNamespace(id=3, nickname="Ana", is_bot=False)
    monkeypatch.setattr(
        UserManager, "get_user", classmethod(lambda cls, _client_id: player)
    )
    monkeypatch.setattr(
        UserManager, "get_color", classmethod(lambda cls, _user_id: "chart-2")
    )

    dto = _limit(10, OrderAction.BUY).to_dto()

    assert (dto.player_nickname, dto.owner, dto.player_color) == (
        "Ana",
        OrderOwner.PLAYER,
        "chart-2",
    )


def test_fund_account_order_dto_names_the_fund(monkeypatch):
    """A ordem da conta de uma gestora sai com o nome dela, sem cor de jogador."""
    order = _limit(10, OrderAction.BUY)
    monkeypatch.setattr(
        SimulationManager,
        "_fund_names",
        {order.client_id: "Aurora Gestão"},
    )

    dto = order.to_dto()

    assert (dto.player_nickname, dto.owner, dto.player_color) == (
        "Aurora Gestão",
        OrderOwner.FUND,
        None,
    )
