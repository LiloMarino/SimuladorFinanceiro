# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.user import UserDTO
from backend.core.enum import NewsType, OrderAction
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.features.funds.fund_book import FundBook, issuance_windows
from backend.features.notifications.news import Headline
from backend.features.variable_income.entities.order import (
    FUND_ISSUER_CLIENT_ID,
    LimitOrder,
)
from tests.fakes import USER_ID, client
from tests.test_fund_book import (
    BUYER,
    MANAGER,
    TICKER,
    TODAY,
    MemoryFunds,
    Setup,
    _setup,
    isolated,
    memory,
)

ANA = UserDTO(id=USER_ID, client_id=BUYER, nickname="Ana")
CARLA = UserDTO(id=2, client_id=client("carla"), nickname="Carla")
LATE = UserDTO(id=3, client_id=client("tardio"), nickname="Tardio")
ROBOT = UserDTO(id=4, client_id=client("robo"), nickname="Robô", is_bot=True)

# Cotas em circulação depois da oferta de 200: 1000 + 120 do formador
QUOTAS = Decimal(1120)
NAV = Decimal(100)
LEFTOVER_START = date(2020, 1, 20)
ENDS_ON = date(2020, 1, 24)


def _give(setup: Setup, user: UserDTO, quotas: int) -> None:
    """Põe `quotas` cotas na carteira do jogador, pagas ao PL da gestora."""
    setup.engine.cash[user.client_id] += NAV * quotas
    setup.engine.broker.buy_from_fund(user.client_id, TICKER, Decimal(quotas), NAV)


def _issuable(memory: MemoryFunds, published: list[Headline] | None = None) -> Setup:
    """Gestora com a oferta encerrada, Ana com 10% das cotas e Carla com 5%."""
    log = published if published is not None else []
    setup = _setup(
        memory,
        publish=lambda day, headline: log.append(headline),
        participants=lambda: [ANA, CARLA, LATE, ROBOT],
    )
    setup.book.open_offer(TICKER, Decimal(200))
    setup.book.close_offer(TICKER)
    _give(setup, ANA, 112)
    _give(setup, CARLA, 56)
    _give(setup, ROBOT, 56)
    for user in (ANA, CARLA, LATE):
        setup.engine.cash[user.client_id] += Decimal(100000)
    return setup


def _news(published: list[Headline]) -> list[NewsType]:
    """As manchetes da emissão, na ordem em que saíram."""
    return [
        h.news_type
        for h in published
        if h.news_type in (NewsType.FUND_ISSUANCE_OPENED, NewsType.FUND_ISSUANCE_CLOSED)
    ]


def _cash(setup: Setup, user: UserDTO) -> Decimal:
    return setup.engine.cash[user.client_id]


def _fund_cash(setup: Setup) -> Decimal:
    return setup.engine.cash[setup.fund_client]


def test_issuance_windows_are_ten_preference_sessions_then_five_leftover_sessions():
    """O anúncio conta como 1º pregão da preferência; a sobra começa no dia útil seguinte."""
    preference_ends_on, ends_on = issuance_windows(TODAY)

    assert preference_ends_on == date(2020, 1, 17)
    assert ends_on == ENDS_ON


def test_announce_fixes_the_price_and_the_rights_of_the_players_with_quotas(
    memory: MemoryFunds,
):
    """Preço = PL por cota do dia; direito = novas x (cotas do jogador / cotas em circulação)."""
    published: list[Headline] = []
    setup = _issuable(memory, published)

    issuance = setup.book.announce_issuance(TICKER, Decimal(200))

    fund = setup.book.get(TICKER)
    assert issuance.price == NAV
    assert (issuance.announced_on, issuance.sold) == (TODAY, 0)
    assert issuance.preference_ends_on == date(2020, 1, 17)
    assert {r.user_id: r.rights for r in fund.issuance_rights.values()} == {
        ANA.id: Decimal(20),  # floor(200 x 112 / 1120)
        CARLA.id: Decimal(10),  # floor(200 x 56 / 1120)
    }
    assert _news(published) == [NewsType.FUND_ISSUANCE_OPENED]
    assert memory.issuances(fund.terms.id) == [issuance]
    assert len(memory.issuance_rights(issuance.id)) == 2


def test_announce_is_rejected_when_the_rules_are_not_met(memory: MemoryFunds):
    setup = _setup(memory)
    with pytest.raises(ConflictError, match="oferta pública aberta"):
        setup.book.announce_issuance(TICKER, Decimal(10))

    setup.book.open_offer(TICKER, Decimal(200))
    with pytest.raises(ConflictError, match="em andamento"):
        setup.book.announce_issuance(TICKER, Decimal(10))

    setup.book.close_offer(TICKER)
    with pytest.raises(UnprocessableEntityError, match="inteira"):
        setup.book.announce_issuance(TICKER, Decimal("10.5"))
    with pytest.raises(UnprocessableEntityError, match="inteira"):
        setup.book.announce_issuance(TICKER, Decimal(0))
    with pytest.raises(UnprocessableEntityError, match="vai até"):
        setup.book.announce_issuance(TICKER, QUOTAS + 1)

    setup.book.announce_issuance(TICKER, Decimal(10))
    with pytest.raises(ConflictError, match="em andamento"):
        setup.book.announce_issuance(TICKER, Decimal(10))


def test_preference_purchase_moves_cash_issues_the_quotas_and_keeps_the_price(
    memory: MemoryFunds,
):
    """A compra paga o preço do anúncio, mesmo com o PL por cota andando, e o caixa entra na gestora."""
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    fund = setup.book.get(TICKER)
    # O PL por cota sobe de 100 para 110 depois do anúncio
    setup.engine.cash[setup.fund_client] += Decimal(11200)
    ana_cash, fund_cash = _cash(setup, ANA), _fund_cash(setup)

    setup.book.subscribe_issuance(TICKER, ANA, Decimal(15))

    assert _cash(setup, ANA) == ana_cash - 15 * NAV
    assert _fund_cash(setup) == fund_cash + 15 * NAV
    assert fund.account.quotas == QUOTAS + 15
    assert setup.book.quotas_of(fund, ANA) == 112 + 15
    assert fund.issuance is not None and fund.issuance.sold == 15
    assert fund.issuance_rights[ANA.id].bought == 15
    [sale] = memory.issuance_sales(fund.issuance.id)
    assert (sale.buyer_user_id, sale.quotas, sale.price) == (ANA.id, 15, NAV)


def test_preference_purchase_is_limited_to_the_remaining_right(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))

    setup.book.subscribe_issuance(TICKER, ANA, Decimal(15))

    with pytest.raises(UnprocessableEntityError, match="mais 5 cotas"):
        setup.book.subscribe_issuance(TICKER, ANA, Decimal(6))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(5))


def test_a_position_bought_after_the_announcement_gives_no_right(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    _give(setup, LATE, 500)

    with pytest.raises(UnprocessableEntityError, match="mais 0 cotas"):
        setup.book.subscribe_issuance(TICKER, LATE, Decimal(1))


def test_bots_have_no_preference(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))

    assert ROBOT.id not in setup.book.get(TICKER).issuance_rights


def test_preference_purchase_needs_cash(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.engine.cash[ANA.client_id] = Decimal(100)

    with pytest.raises(UnprocessableEntityError, match="Caixa insuficiente"):
        setup.book.subscribe_issuance(TICKER, ANA, Decimal(5))

    assert setup.book.get(TICKER).account.quotas == QUOTAS


def test_purchase_without_issuance_or_after_the_preference_is_rejected(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    with pytest.raises(ConflictError, match="preferência"):
        setup.book.subscribe_issuance(TICKER, ANA, Decimal(1))

    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.tick(LEFTOVER_START)

    with pytest.raises(ConflictError, match="preferência"):
        setup.book.subscribe_issuance(TICKER, ANA, Decimal(1))


def test_the_leftover_opens_to_everyone_at_the_fixed_price(memory: MemoryFunds):
    """Depois da preferência, o que sobrou vai ao livro ao preço do anúncio e qualquer um compra."""
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(20))
    fund = setup.book.get(TICKER)
    setup.engine.cash[setup.fund_client] += Decimal(
        20000
    )  # o PL por cota sai do anúncio

    setup.tick(LEFTOVER_START)

    assert fund.account.offer_remaining == 180
    # A sobra da emissão não devolve a gestora ao estágio de oferta de abertura
    summary = setup.book.summary(fund, {})
    assert summary.offer_remaining is None and summary.offer_session is None
    issuer = setup.engine.matching_engine.order_book.best_sell(TICKER)
    assert issuer is not None and issuer.client_id == FUND_ISSUER_CLIENT_ID
    assert issuer.price == float(NAV)

    setup.buy(30)

    assert fund.account.quotas == QUOTAS + 20 + 30
    assert fund.issuance is not None and fund.issuance.sold == 50
    assert fund.account.offer_remaining == 150
    [*_, sale] = memory.issuance_sales(fund.issuance.id)
    assert (sale.quotas, sale.price) == (30, NAV)


def test_what_does_not_sell_never_exists(memory: MemoryFunds):
    """Terminada a sobra, a emissão encerra e só as cotas vendidas passam a existir."""
    published: list[Headline] = []
    setup = _issuable(memory, published)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(20))
    fund = setup.book.get(TICKER)
    setup.tick(LEFTOVER_START)
    setup.buy(30)

    for day in range(20, 25):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))

    assert fund.issuance is None
    assert fund.account.quotas == QUOTAS + 50
    assert fund.account.offer_remaining is None
    orders = setup.engine.matching_engine.order_book.get_orders(TICKER)
    assert FUND_ISSUER_CLIENT_ID not in {o.client_id for o in orders}
    [closed] = memory.issuances(fund.terms.id)
    assert (closed.sold, closed.closed_on) == (50, ENDS_ON)
    assert _news(published) == [
        NewsType.FUND_ISSUANCE_OPENED,
        NewsType.FUND_ISSUANCE_CLOSED,
    ]


def test_selling_the_whole_issuance_closes_it_that_day(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(30))
    fund = setup.book.get(TICKER)
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(3))
    setup.tick(LEFTOVER_START)

    setup.buy(27)
    setup.book.on_close(LEFTOVER_START)

    assert fund.issuance is None
    [closed] = memory.issuances(fund.terms.id)
    assert (closed.sold, closed.closed_on) == (30, LEFTOVER_START)
    assert fund.account.quotas == QUOTAS + 30


def test_an_issuance_does_not_change_the_nav_of_who_did_not_buy(memory: MemoryFunds):
    """Cota nova entra ao PL por cota do dia, com o caixa que paga por ela: o PL por cota fica."""
    setup = _issuable(memory)
    fund = setup.book.get(TICKER)
    before = setup.book.nav_of(fund)

    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(20))
    setup.book.subscribe_issuance(TICKER, CARLA, Decimal(10))

    assert before == NAV
    assert setup.book.nav_of(fund) == before


def test_an_issuance_in_progress_survives_stopping_and_resuming(memory: MemoryFunds):
    """Preço, andamento e direitos voltam do que foi gravado."""
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(12))
    before = setup.book.get(TICKER)

    reloaded = FundBook(
        1, setup.engine, lambda user_id: MANAGER, None, None, lambda: [ANA, CARLA]
    ).get(TICKER)

    assert reloaded.issuance == before.issuance
    assert reloaded.issuance is not None and reloaded.issuance.sold == 12
    assert reloaded.issuance_rights == before.issuance_rights
    assert reloaded.issuance_rights[ANA.id].bought == 12


def _seller(setup: Setup, user: UserDTO, quotas: int, price: float) -> None:
    """O jogador põe cotas à venda no livro."""
    setup.engine.matching_engine.submit(
        LimitOrder(
            client_id=user.client_id,
            ticker=TICKER,
            size=Decimal(quotas),
            action=OrderAction.SELL,
            placed_on=setup.engine.current_date,
            price=price,
        )
    )


def test_buyback_needs_the_cash_for_the_maximum_price(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.engine.cash[setup.fund_client] = Decimal(500)

    with pytest.raises(UnprocessableEntityError, match="caixa"):
        setup.book.open_buyback(TICKER, Decimal(10), Decimal(100))

    assert setup.book.get(TICKER).buyback is None


def test_buyback_is_rejected_while_an_issuance_is_open(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(10))

    with pytest.raises(ConflictError, match="Encerre"):
        setup.book.open_buyback(TICKER, Decimal(10), Decimal(90))


def test_one_buyback_at_a_time_and_no_issuance_while_it_is_open(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.open_buyback(TICKER, Decimal(10), Decimal(90))

    with pytest.raises(ConflictError, match="em aberto"):
        setup.book.open_buyback(TICKER, Decimal(10), Decimal(90))
    with pytest.raises(ConflictError, match="Encerre a recompra"):
        setup.book.announce_issuance(TICKER, Decimal(10))


def test_buyback_burns_the_quotas_it_buys_and_never_makes_a_position(
    memory: MemoryFunds,
):
    """A cota comprada pela gestora deixa de existir: o total cai e a carteira dela não a guarda."""
    setup = _issuable(memory)
    fund = setup.book.get(TICKER)
    # Acima das ofertas de compra do formador, a recompra é a primeira da fila
    setup.book.open_buyback(TICKER, Decimal(20), Decimal("99.90"))

    _seller(setup, CARLA, 20, 90.0)

    assert setup.book.buyback_of(fund) is None  # executada por inteiro
    assert fund.account.quotas == QUOTAS - 20
    assert setup.engine.broker.get_positions(setup.fund_client).get(TICKER) is None
    [stored] = memory.buybacks(fund.terms.id)
    assert (stored.bought, stored.state) == (20, "done")
    assert stored.paid == 20 * Decimal("99.90")


def test_buyback_below_the_nav_raises_the_nav_of_who_stayed(memory: MemoryFunds):
    """Comprar a R$ 90 cotas que valem R$ 100 deixa o caixa menor que o patrimônio que saiu."""
    setup = _issuable(memory)
    fund = setup.book.get(TICKER)
    before = setup.book.nav_of(fund)
    setup.book.open_buyback(TICKER, Decimal(20), Decimal("99.90"))

    _seller(setup, CARLA, 20, 90.0)

    after = setup.book.nav_of(fund)
    assert before == NAV and after is not None and before is not None
    assert after > before


def test_cancel_returns_the_reserved_cash_and_keeps_what_was_bought(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    fund = setup.book.get(TICKER)
    nav = setup.book.nav_of(fund)

    setup.book.open_buyback(TICKER, Decimal(50), Decimal(90))
    assert fund.buyback is not None
    assert setup.book.nav_of(fund) == nav  # a reserva da ordem segue como patrimônio

    setup.book.cancel_buyback(TICKER)

    assert fund.buyback is None
    [stored] = memory.buybacks(fund.terms.id)
    assert stored.state == "canceled"
    assert setup.book.nav_of(fund) == nav
    with pytest.raises(ConflictError, match="não tem recompra"):
        setup.book.cancel_buyback(TICKER)


def test_resuming_cancels_the_buyback_that_was_open(memory: MemoryFunds):
    setup = _issuable(memory)
    setup.book.open_buyback(TICKER, Decimal(50), Decimal(90))

    reloaded = FundBook(1, setup.engine, lambda user_id: MANAGER).get(TICKER)

    assert reloaded.buyback is None
    [stored] = memory.buybacks(reloaded.terms.id)
    assert stored.state == "canceled"


def test_a_buyback_cannot_take_all_the_quotas(memory: MemoryFunds):
    setup = _issuable(memory)

    with pytest.raises(UnprocessableEntityError, match="todas as cotas"):
        setup.book.open_buyback(TICKER, QUOTAS, Decimal(1))


def test_the_day_after_the_announcement_still_counts_as_preference(
    memory: MemoryFunds,
):
    setup = _issuable(memory)
    setup.book.announce_issuance(TICKER, Decimal(200))

    setup.tick(TODAY + timedelta(days=1))

    assert setup.book.get(TICKER).issuance_phase(setup.engine.current_date) == (
        "preference"
    )
    setup.book.subscribe_issuance(TICKER, ANA, Decimal(1))
