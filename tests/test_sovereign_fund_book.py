"""O Fundo Soberano no livro do governo: caixa, retorno ao Tesouro, manchetes e favorecimento."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.enum import (
    EquityEventType,
    MeasureKind,
    NewsType,
    SovereignFlowKind,
    VoterGroup,
)
from backend.core.utils import required
from backend.features.government import voters
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from backend.features.sovereign_fund import rules as fund_rules
from backend.features.sovereign_fund.book import FundQuotas, budget_month_end
from tests.test_government_book import (
    ALICE,
    TERM_START,
    USERS,
    book,
    engine,
    govern,
    headlines,
    market,
    notices,
    office,
    settings,
    stored,
)
from tests.test_sovereign_fund_measures import fund_cash
from tests.test_state_company_measures import match, no_frozen_portfolio

D = Decimal
BILLION = D(10) ** 9
BUY = EquityEventType.BUY
SELL = EquityEventType.SELL
# O primeiro dia depois da posse: o partido do presidente já governa
DAY = TERM_START + timedelta(days=1)


def fund_texts(headlines, news_type: NewsType) -> list[str]:
    return [h.text for _day, h in headlines if h.news_type is news_type]


def fund_with_cash(book: GovernmentBook, engine, billions: int = 25) -> None:
    """O fundo com o aporte já no caixa, como depois da vigência da medida."""
    engine.add_cash(book.sovereign_fund().client_id, billions * BILLION)


def settle(
    book: GovernmentBook,
    engine,
    side: EquityEventType,
    ticker: str,
    size: int,
    price: int,
) -> None:
    """Uma ordem do fundo liquidada no livro de ofertas, como o engine avisa."""
    engine.on_settled(book.sovereign_fund().client_id, side, ticker, D(size), D(price))


# Caixa e retorno ao Tesouro


def test_the_fund_starts_with_no_cash_so_it_has_nothing_to_buy_with(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)

    assert fund_cash(book, engine) == 0
    assert book.sovereign_fund().contributed() == 0


def test_a_sale_goes_back_to_the_treasury_and_cuts_the_debt(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    fund_with_cash(book, engine, 25)
    engine.current_date = DAY

    # O caixa do fundo recebe o dinheiro da venda e o livro o repassa ao Tesouro
    engine.add_cash(book.sovereign_fund().client_id, 3 * BILLION)
    settle(book, engine, SELL, "PETR4", 100_000_000, 30)

    assert fund_cash(book, engine) == 25 * BILLION
    assert book.sovereign_fund().returned() == 3 * BILLION
    assert book.sovereign_fund().assets_in(budget_month_end(DAY)) == 3 * BILLION
    [flow] = repository.sovereign_fund.flows(match)
    assert (flow.kind, flow.amount) == (SovereignFlowKind.SALE, 3 * BILLION)


def test_a_dividend_goes_back_to_the_treasury_the_same_day(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    fund_with_cash(book, engine, 25)
    engine.current_date = DAY
    client = book.sovereign_fund().client_id

    engine.add_cash(client, 2 * BILLION)
    engine.on_dividend(client, "PETR4", 2 * BILLION)

    assert fund_cash(book, engine) == 25 * BILLION
    assert book.sovereign_fund().dividends_in(budget_month_end(DAY)) == 2 * BILLION
    assert book.sovereign_fund().returned() == 2 * BILLION


def test_what_other_accounts_do_never_reaches_the_fund_book(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    engine.current_date = DAY

    engine.on_settled(ALICE.client_id, SELL, "PETR4", D(100), D(30))
    engine.on_dividend(ALICE.client_id, "PETR4", D(500))

    assert book.sovereign_fund().returned() == 0
    assert repository.sovereign_fund.flows(match) == []


def test_the_flows_come_back_when_the_game_resumes(
    book: GovernmentBook, engine, market, match
):
    govern(book, engine)
    engine.current_date = DAY
    client = book.sovereign_fund().client_id
    engine.add_cash(client, BILLION)
    settle(book, engine, SELL, "PETR4", 1_000_000, 30)

    reloaded = repository.sovereign_fund.flows(match)

    assert sum(flow.amount for flow in reloaded) == 30 * 10**6


# Manchetes e favorecimento


def test_a_purchase_becomes_one_headline_at_the_end_of_the_day(
    book: GovernmentBook, engine, market, match, headlines
):
    govern(book, engine)
    fund_with_cash(book, engine, 25)
    engine.current_date = DAY

    settle(book, engine, BUY, "PETR4", 40_000_000, 25)
    settle(book, engine, BUY, "PETR4", 20_000_000, 25)
    assert fund_texts(headlines, NewsType.SOVEREIGN_FUND_BOUGHT) == []
    book.close_state_market(DAY)

    [text] = fund_texts(headlines, NewsType.SOVEREIGN_FUND_BOUGHT)
    assert "compra R$ 1,5 bi em PETR4" in text


def test_a_sale_is_a_headline_too(
    book: GovernmentBook, engine, market, match, headlines
):
    govern(book, engine)
    engine.current_date = DAY
    engine.add_cash(book.sovereign_fund().client_id, 3 * BILLION)

    settle(book, engine, SELL, "PETR4", 100_000_000, 30)
    book.close_state_market(DAY)

    [text] = fund_texts(headlines, NewsType.SOVEREIGN_FUND_SOLD)
    assert "vende PETR4 e devolve R$ 3 bi ao Tesouro" in text


def use_manager(book: GovernmentBook, party: str | None, quotas: int = 1000) -> None:
    book.use_fund_lookup(lambda ticker: FundQuotas("Aura", D(quotas), party))


def rejection(book: GovernmentBook) -> dict[VoterGroup, Decimal]:
    term = book.state.term
    assert term is not None
    return dict(book.state.parties[required(term.party_id)].rejection)


def test_buying_a_neutral_manager_stake_gives_no_favoritism(
    book: GovernmentBook, engine, market, match, headlines
):
    govern(book, engine)
    fund_with_cash(book, engine)
    engine.current_date = DAY
    use_manager(book, "ZZZ")
    before = rejection(book)

    settle(book, engine, BUY, "AURA11", 100, 10)
    book.close_state_market(DAY)

    assert fund_texts(headlines, NewsType.SOVEREIGN_FUND_FAVORITISM) == []
    assert rejection(book) == before


def test_buying_an_allied_manager_stake_costs_two_points_per_twelve_percent(
    book: GovernmentBook, engine, market, match, headlines
):
    govern(book, engine)
    fund_with_cash(book, engine)
    engine.current_date = DAY
    # Governa o partido AAA, o mesmo do gestor: 120 de 1000 cotas são 12% de fatia
    use_manager(book, "AAA", 1000)
    before = rejection(book)

    settle(book, engine, BUY, "AURA11", 120, 10)
    book.close_state_market(DAY)

    [text] = fund_texts(headlines, NewsType.SOVEREIGN_FUND_FAVORITISM)
    assert "12% da gestora Aura" in text
    assert fund_texts(headlines, NewsType.SOVEREIGN_FUND_BOUGHT) == []
    after = rejection(book)
    for group in VoterGroup:
        assert after[group] == voters.add_rejection(before[group], D(2))


def test_the_favoritism_adds_up_buy_by_buy(
    book: GovernmentBook, engine, market, match, headlines
):
    govern(book, engine)
    fund_with_cash(book, engine)
    use_manager(book, "AAA", 1000)
    before = rejection(book)

    for offset in (1, 2):
        engine.current_date = TERM_START + timedelta(days=offset)
        settle(book, engine, BUY, "AURA11", 60, 10)
        book.close_state_market(engine.current_date)

    after = rejection(book)
    for group in VoterGroup:
        # Duas compras de 6% de fatia valem 1 ponto cada, como uma de 12% valeria 2
        step = voters.add_rejection(voters.add_rejection(before[group], D(1)), D(1))
        assert after[group] == step


def test_the_favoritism_rebuilds_from_the_events(
    book: GovernmentBook, engine, market, match, stored
):
    govern(book, engine)
    fund_with_cash(book, engine)
    engine.current_date = DAY
    use_manager(book, "AAA", 1000)
    settle(book, engine, BUY, "AURA11", 120, 10)
    book.close_state_market(DAY)

    rebuilt = replay(stored)

    term = rebuilt.term
    assert term is not None
    assert rebuilt.parties[required(term.party_id)].rejection == rejection(book)


# As regras puras


def test_the_stake_and_the_room_under_the_ceiling():
    assert fund_rules.stake(D(120), D(1000)) == D("0.12")
    assert fund_rules.stake(D(5), D(0)) == 0
    assert fund_rules.room(D(150), D(1000)) == 50
    assert fund_rules.room(D(250), D(1000)) == 0
    assert D("0.20") == fund_rules.CEILING


def test_twelve_percent_of_stake_are_two_points():
    assert fund_rules.favoritism_points(D("0.12")) == 2
