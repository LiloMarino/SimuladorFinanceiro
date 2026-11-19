# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.enum import NewsLevel, NewsType
from backend.features.funds.offers_panel import FundOffersBuilder
from backend.features.notifications.news import Headline
from backend.features.notifications.registry import news_levels
from tests.test_fund_book import (
    TICKER,
    TODAY,
    MemoryFunds,
    Setup,
    _setup,
    isolated,
    memory,
)
from tests.test_fund_issuance import (
    ANA,
    CARLA,
    LATE,
    LEFTOVER_START,
    NAV,
    ROBOT,
    _issuable,
)


def _offers(setup: Setup, viewer):
    """A página Ofertas públicas no dia que o motor marca."""
    return FundOffersBuilder(setup.book, setup.engine.current_date).build(viewer)


def test_the_opening_offer_is_open_to_everyone_with_session_and_deadline(
    memory: MemoryFunds,
):
    setup = _setup(memory, participants=lambda: [ANA])
    setup.book.open_offer(TICKER, Decimal(200))

    offers = _offers(setup, ANA)

    [offer] = offers.open
    assert (offer.kind, offer.ticker, offer.price) == ("initial", TICKER, NAV)
    assert (offer.quotas, offer.remaining) == (200, 200)
    # Aberta em 06/01: pregão 1 de 5, vai até 10/01 e restam 4 depois de hoje
    assert (offer.session, offer.ends_on, offer.sessions_left) == (
        1,
        date(2020, 1, 10),
        4,
    )
    assert offer.preference_ends_on is None
    assert offers.preference == [] and offers.closed == []


def test_a_sold_out_offer_stays_open_until_its_deadline_then_moves_to_history(
    memory: MemoryFunds,
):
    setup = _setup(memory, participants=lambda: [ANA])
    setup.book.open_offer(TICKER, Decimal(20))
    setup.buy(20)

    [offer] = _offers(setup, ANA).open
    assert offer.remaining == 0

    setup.tick(date(2020, 1, 13))
    after = _offers(setup, ANA)

    assert after.open == []
    [closed] = after.closed
    assert (closed.kind, closed.quotas, closed.sold) == ("initial", 20, 20)
    assert closed.closed_on == TODAY


def test_an_offer_that_ran_to_the_deadline_goes_to_history_with_what_was_sold(
    memory: MemoryFunds,
):
    setup = _setup(memory, participants=lambda: [ANA])
    setup.book.open_offer(TICKER, Decimal(200))
    setup.buy(50)
    for day in (7, 8, 9, 10):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))

    offers = _offers(setup, ANA)

    assert offers.open == []
    [closed] = offers.closed
    assert (closed.sold, closed.quotas) == (50, 200)
    assert closed.closed_on == date(2020, 1, 10)


def test_the_preference_lists_only_the_issuances_where_the_viewer_holds_quotas(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))

    ana = _offers(setup, ANA).preference
    carla = _offers(setup, CARLA).preference
    late = _offers(setup, LATE).preference
    robot = _offers(setup, ROBOT).preference

    [mine] = ana
    # Ana tem 10% das 1.120 cotas: floor(200 x 112 / 1120) = 20, e nada foi comprado ainda
    assert (mine.my_rights, mine.my_left, mine.holders_bought) == (20, 20, 0)
    assert (mine.price, mine.issuance_quotas) == (NAV, 200)
    assert (mine.preference_ends_on, mine.sessions_left) == (date(2020, 1, 17), 10)
    assert [item.my_rights for item in carla] == [10]
    assert late == [] and robot == []


def test_the_preference_shrinks_with_the_purchase_and_leaves_when_the_right_is_used(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))

    setup.book.subscribe_issuance(TICKER, ANA, Decimal(5))
    [partial] = _offers(setup, ANA).preference
    assert (partial.my_left, partial.holders_bought) == (15, 5)

    setup.book.subscribe_issuance(TICKER, ANA, Decimal(15))
    assert _offers(setup, ANA).preference == []
    [carla] = _offers(setup, CARLA).preference
    assert carla.holders_bought == 20


def test_the_leftover_opens_to_everyone_and_the_preference_closes(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(20))
    setup.engine.cash[setup.fund_client] += Decimal(20000)

    setup.tick(LEFTOVER_START)
    offers = _offers(setup, LATE)

    assert offers.preference == []
    [leftover] = offers.open
    assert (leftover.kind, leftover.session) == ("leftover", None)
    assert (leftover.quotas, leftover.remaining) == (200, 180)
    assert (leftover.preference_ends_on, leftover.preference_bought) == (
        date(2020, 1, 17),
        20,
    )
    # A sobra abre em 20/01 e vai até 24/01: o pregão 1 de 5 deixa 4 depois de hoje
    assert (leftover.ends_on, leftover.sessions_left) == (date(2020, 1, 24), 4)


def test_a_closed_issuance_goes_to_history_beside_the_price_of_today(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(20))
    setup.tick(LEFTOVER_START)
    setup.buy(30)
    for day in range(20, 25):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))

    offers = _offers(setup, ANA)

    assert offers.open == [] and offers.preference == []
    issuance = [item for item in offers.closed if item.kind == "issuance"]
    [closed] = issuance
    assert (closed.sold, closed.quotas, closed.price) == (50, 200, NAV)
    assert closed.closed_on == date(2020, 1, 24)
    assert closed.market_price == setup.book.price(setup.book.get(TICKER))


def test_the_opening_of_an_offer_is_the_only_headline_that_opens_a_window(
    memory: MemoryFunds,
):
    published: list[tuple[date, Headline]] = []
    setup = _setup(memory, publish=lambda day, h: published.append((day, h)))

    setup.book.open_offer(TICKER, Decimal(200))

    [(day, headline)] = published
    assert (day, headline.news_type, headline.tickers) == (
        TODAY,
        NewsType.FUND_OFFER_OPENED,
        (TICKER,),
    )
    assert headline.text == "Aura abre oferta de 200 cotas a R$ 100"
    assert headline.dek is not None and "preço fixo por 5 pregões, até 10/01" in (
        headline.dek
    )
    levels = news_levels({})
    assert levels[NewsType.FUND_OFFER_OPENED] is NewsLevel.WINDOW
    assert levels[NewsType.FUND_ISSUANCE_OPENED] is NewsLevel.JOURNAL
