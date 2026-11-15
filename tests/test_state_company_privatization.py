"""A oferta de privatização: pedidos na janela, rateio, caixa, sobra, dívida do Tesouro e fim da estatal."""

# As fixtures do livro do governo e da economia vêm dos módulos dos testes deles
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.enum import (
    DividendPolicy,
    GovernmentEventType,
    InitialAccount,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.economy.growth import MacroCourse
from backend.features.government import budget
from backend.features.government.budget import BudgetCourse
from backend.features.government.government_book import GovernmentBook
from backend.features.market_maker.account import MakerAccount
from backend.features.state_companies.book import (
    StateCompanyBook,
    government_shares,
    maker_shares,
)
from backend.features.state_companies.market import StateCompanyMarket
from backend.features.state_companies.orders import StateOrder
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.fakes import FakeSimulationEngine, client, simulation_settings
from tests.test_government_book import (
    TERM_START,
    close_months,
    engine,
    govern,
    headlines,
    market,
    notices,
    office,
    stored,
)
from tests.test_government_state_orders import (
    FUEL,
    company,
    events_of,
    given,
    new_state_book,
    order,
)
from tests.test_state_company_price import flat_economy

D = Decimal
FOUNDED_ON = date(2020, 1, 2)
OPENED_ON = date(2020, 1, 6)
LAST_SESSION = date(2020, 1, 10)
RICH = D(10) ** 15

type History = dict[date, dict[str, StateOrder]]


class Accounts:
    """O caixa de cada carteira em memória: a entrega debita `shares` x `price`."""

    def __init__(self, wallet: dict[int, Decimal]) -> None:
        self.wallet = dict(wallet)
        self.delivered: dict[int, int] = {}

    def cash(self, portfolio_id: int) -> Decimal:
        return self.wallet.get(portfolio_id, D(0))

    def deliver(
        self, portfolio_id: int, ticker: str, shares: int, price: Decimal
    ) -> None:
        self.wallet[portfolio_id] -= shares * price
        self.delivered[portfolio_id] = shares


class Offer:
    """A estatal fundada com a oferta aberta e duas carteiras de jogador."""

    def __init__(self, history: History | None = None) -> None:
        self.simulation_id = repository.simulation.create_simulation(
            simulation_settings()
        )
        self.history: History = history if history is not None else {}
        self.book = StateCompanyBook(self.simulation_id, 7, lambda: self.history)
        found = self.book.found(
            ticker="PNOV3",
            name="Petro Nova",
            size=StateCompanySize.SMALL,
            lever=StateLever.FUEL,
            real_interest=D("0.05"),
            today=FOUNDED_ON,
        )
        assert found is not None
        self.book.open_privatization("PNOV3", OPENED_ON)
        users = [
            repository.user.create_user(client(name), name).id
            for name in ("Ana", "Bia")
        ]
        portfolios = repository.portfolio.create(self.simulation_id, users)
        self.ana, self.bia = (portfolios[user] for user in users)

    @property
    def offered(self) -> int:
        return government_shares(required_company(self.book))

    def reserve(self, portfolio_id: int, quantity: int, day: date = OPENED_ON) -> None:
        self.book.reserve("PNOV3", portfolio_id, D(quantity), day)

    def close(self, accounts: Accounts, day: date = LAST_SESSION):
        return self.book.close_privatization("PNOV3", day, accounts)


def required_company(book: StateCompanyBook):
    found = book.company("PNOV3")
    assert found is not None
    return found


# Os pedidos na janela


def test_a_reservation_inside_the_window_is_saved_without_touching_cash(
    database: Engine,
) -> None:
    offer = Offer()

    offer.reserve(offer.ana, 100)
    offer.reserve(offer.ana, 150, LAST_SESSION)

    assert repository.state_company.reservations_of(
        required_company(offer.book).id
    ) == {offer.ana: D(150)}


def test_a_reservation_outside_the_window_is_refused(database: Engine) -> None:
    offer = Offer()

    with pytest.raises(ConflictError):
        offer.reserve(offer.ana, 100, date(2020, 1, 3))
    with pytest.raises(ConflictError):
        offer.reserve(offer.ana, 100, date(2020, 1, 13))

    assert (
        repository.state_company.reservations_of(required_company(offer.book).id) == {}
    )


def test_a_reservation_on_a_company_without_an_open_offer_is_refused(
    database: Engine,
) -> None:
    offer = Offer()
    offer.close(Accounts({}))

    with pytest.raises(ConflictError):
        offer.reserve(offer.ana, 100)
    with pytest.raises(NotFoundError):
        offer.book.reserve("NADA3", offer.ana, D(1), OPENED_ON)


@pytest.mark.parametrize("quantity", [D(0), D(-5), D("1.5")])
def test_a_reservation_takes_only_a_positive_whole_quantity(
    database: Engine, quantity: Decimal
) -> None:
    offer = Offer()

    with pytest.raises(UnprocessableEntityError):
        offer.book.reserve("PNOV3", offer.ana, quantity, OPENED_ON)


# O rateio e o caixa


def test_without_excess_everyone_receives_the_request(database: Engine) -> None:
    offer = Offer()
    offer.reserve(offer.ana, 1_000)
    offer.reserve(offer.bia, 2_000)
    accounts = Accounts({offer.ana: RICH, offer.bia: RICH})

    result = offer.close(accounts)

    assert result.delivered == {offer.ana: 1_000, offer.bia: 2_000}
    assert accounts.delivered == result.delivered
    assert result.leftover == offer.offered - 3_000


def test_with_excess_the_allocation_is_proportional(database: Engine) -> None:
    offer = Offer()
    offered = offer.offered
    offer.reserve(offer.ana, offered)
    offer.reserve(offer.bia, offered // 2)
    accounts = Accounts({offer.ana: RICH, offer.bia: RICH})

    result = offer.close(accounts)

    # Pedido total de 1,5x a oferta: cada conta leva dois terços do que pediu
    assert result.delivered[offer.ana] == pytest.approx(offered * 2 / 3, abs=1)
    assert result.delivered[offer.bia] == pytest.approx(offered / 3, abs=1)
    assert sum(result.delivered.values()) <= offered
    assert result.leftover == offered - sum(result.delivered.values())
    assert result.leftover <= 2


def test_cash_limits_the_allocation_to_whole_shares(database: Engine) -> None:
    offer = Offer()
    offer.reserve(offer.ana, 1_000)
    offer.reserve(offer.bia, 1_000)
    probe = offer.book.offer_price(required_company(offer.book), LAST_SESSION)
    assert probe is not None
    accounts = Accounts({offer.ana: probe * 400 + probe / 2, offer.bia: RICH})

    result = offer.close(accounts)

    assert result.delivered == {offer.ana: 400, offer.bia: 1_000}
    assert accounts.wallet[offer.ana] == probe / 2
    assert result.leftover == offer.offered - 1_400


def test_an_account_without_cash_receives_nothing(database: Engine) -> None:
    offer = Offer()
    offer.reserve(offer.ana, 1_000)

    result = offer.close(Accounts({}))

    assert result.delivered == {}
    assert result.leftover == offer.offered


# A sobra, o Tesouro e o fim da estatal


def test_the_leftover_goes_to_the_maker_stock(database: Engine) -> None:
    offer = Offer()
    offer.reserve(offer.ana, 5_000)
    result = offer.close(Accounts({offer.ana: RICH}))
    company = required_company(offer.book)
    trading = FakeSimulationEngine(current_date=LAST_SESSION)

    market = StateCompanyMarket(offer.simulation_id, trading, offer.book)
    account = trading.broker.maker_accounts["PNOV3"]
    assert isinstance(account, MakerAccount)
    # Sem entregas gravadas, a ação privatizada nasce inteira no estoque do formador
    assert account.maker_quotas == company.shares
    account.maker_quotas = D(maker_shares(company))
    market.add_leftover("PNOV3", result.leftover)

    assert account.maker_quotas == maker_shares(company) + result.leftover
    assert account.quotas == company.shares


def test_the_government_receives_the_fair_value_of_the_whole_slice(
    database: Engine,
) -> None:
    offer = Offer()
    offer.reserve(offer.ana, 1_000)
    company = required_company(offer.book)
    fair_per_share = offer.book.fair_value_on(company, LAST_SESSION) / company.shares

    result = offer.close(Accounts({offer.ana: RICH}))

    assert result.price == fair_per_share.quantize(D("0.01"))
    assert result.proceeds == result.price * offer.offered
    assert offer.book.assets_in(date(2020, 1, 31)) == result.proceeds
    assert offer.book.assets_in(date(2020, 2, 29)) == 0


def test_a_sale_on_the_last_day_of_the_month_counts_in_the_next(
    database: Engine,
) -> None:
    offer = Offer()

    result = offer.close(Accounts({}), date(2020, 1, 31))

    assert offer.book.assets_in(date(2020, 1, 31)) == 0
    assert offer.book.assets_in(date(2020, 2, 29)) == result.proceeds


def test_the_debt_falls_by_the_assets_and_the_primary_stays(
    database: Engine, flat_economy: None
) -> None:
    offer = Offer()
    offer.close(Accounts({}))
    account = budget.initial_account(date(2020, 1, 1), InitialAccount.PLAYABLE)

    def course(assets_on) -> BudgetCourse:
        return BudgetCourse(
            date(2020, 1, 1),
            lambda _day: DEFAULT_TAX_POLICY,
            account,
            MacroCourse(date(2020, 1, 1)),
            state_assets_on=assets_on,
        )

    sold = course(offer.book.assets_in).months_until(date(2020, 1, 31))[-1]
    plain = course(lambda _day: D(0)).months_until(date(2020, 1, 31))[-1]

    assert sold.state_assets > 0
    assert sold.debt < plain.debt
    assert sold.revenue == plain.revenue
    assert sold.primary == plain.primary


def test_the_company_becomes_privatized_and_the_order_stops_acting(
    database: Engine,
) -> None:
    holding = StateOrder(StateControl.P10, DividendPolicy.REINVEST)
    offer = Offer({date(2020, 1, 1): {"PNOV3": holding}})
    before = offer.book.founded_price_factor("PNOV3", LAST_SESSION)

    result = offer.close(Accounts({}))

    company = required_company(offer.book)
    stored_company = repository.state_company.of_simulation(offer.simulation_id)[0]
    assert (company.status, company.privatized_on, company.proceeds) == (
        StateCompanyStatus.PRIVATIZED,
        LAST_SESSION,
        result.proceeds,
    )
    assert stored_company == company
    assert before != 1.0
    assert offer.book.founded_price_factor("PNOV3", LAST_SESSION) == 1.0
    assert offer.book.founded_price_factor("PNOV3", date(2020, 1, 9)) == before


def test_a_closed_offer_cannot_close_again(database: Engine) -> None:
    offer = Offer()
    offer.close(Accounts({}))

    with pytest.raises(ConflictError):
        offer.close(Accounts({}))


# O livro do governo: fechamento no último pregão e fim da ordem


def test_the_government_closes_the_offer_on_the_last_session_and_undoes_the_order(
    database, engine, stored, notices, captured_events, office, headlines, market
):
    book = new_state_book(engine, office, headlines, [company(FUEL, StateLever.FUEL)])
    engine.matching_engine = SimpleNamespace(
        market_data=SimpleNamespace(
            get_last=lambda _ticker: SimpleNamespace(close=20.0)
        )
    )
    govern(book, engine)
    order(book, FUEL, StateControl.P10)
    assert FUEL in given(book)
    book.state_companies().open_privatization(FUEL, TERM_START)
    ends_on = book.state_companies().offer_ends_on(FUEL)
    assert ends_on is not None

    book.close_state_market(date(2022, 1, 5))
    assert required_status(book) is StateCompanyStatus.PRIVATIZING

    book.close_state_market(ends_on)

    privatized = book.state_companies().company(FUEL)
    assert privatized is not None
    assert privatized.status is StateCompanyStatus.PRIVATIZED
    assert privatized.proceeds == D(20) * government_shares(privatized)
    assert given(book) == {}
    released = events_of(stored, GovernmentEventType.STATE_ORDER_SET)[-1]
    assert released.payload["ticker"] == FUEL
    assert released.payload["control"] == StateControl.NONE.value


def required_status(book: GovernmentBook) -> StateCompanyStatus:
    found = book.state_companies().company(FUEL)
    assert found is not None
    return found.status
