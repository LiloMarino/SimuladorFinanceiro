"""Preço e provento da ação de estatal sob as ordens do presidente, e o dividendo que o Tesouro recebe."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine

from backend.core import repository
from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.state_company import StateCompanyDTO, StateOwnedStockRequest
from backend.core.enum import (
    AssetClass,
    CorporateEventKind,
    DividendPolicy,
    IndicatorSeries,
    InitialAccount,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
)
from backend.features.economy.growth import MacroCourse
from backend.features.economy.layer import EconomyLayer, StateFactors
from backend.features.government import budget
from backend.features.government import spending_effects as fx
from backend.features.government.budget import BudgetCourse
from backend.features.state_companies import gdp, payout, price
from backend.features.state_companies.book import (
    FOUNDING_GOVERNMENT_SHARE,
    StateCompanyBook,
)
from backend.features.state_companies.orders import StateOrder
from backend.features.state_companies.panel import build_order_preview
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series, simulation_settings

START = date(2020, 1, 1)
JUNE = date(2022, 6, 1)
IMPORTED = "PETR4"
FOUNDED = "PNOV3"
FOUNDED_ON = date(2022, 4, 15)

type History = dict[date, dict[str, StateOrder]]


def _company() -> StateCompanyDTO:
    return StateCompanyDTO(
        id=1,
        stock_id=1,
        ticker=IMPORTED,
        origin=StateCompanyOrigin.IMPORTED,
        government_share=Decimal("0.5"),
        shares=1000,
        lever=StateLever.FUEL,
        size=None,
        invested=Decimal(0),
        mean_return=None,
        seed=None,
        status=StateCompanyStatus.ACTIVE,
        founded_on=None,
        offer_opened_on=None,
        privatized_on=None,
        proceeds=None,
    )


def _wired(order: StateOrder | None) -> tuple[EconomyLayer, EconomyLayer]:
    """A camada ligada ao livro com a ordem de junho (ou sem ordem) e uma camada sem estatais."""
    history: History = {} if order is None else {JUNE: {IMPORTED: order}}
    book = StateCompanyBook(1, 7, lambda: history, [_company()])
    wired = EconomyLayer(1, START, fx.SpendingEconomy())
    wired.use_state_companies(
        StateFactors(book.is_founded, book.price_factor, book.dividend_factor)
    )
    return wired, EconomyLayer(1, START, fx.SpendingEconomy())


def test_without_an_order_the_stock_factor_is_the_one_of_a_layer_without_state_companies() -> (
    None
):
    wired, plain = _wired(None)
    day = date(2022, 6, 15)

    assert wired.stock_factor(IMPORTED, day) == plain.stock_factor(IMPORTED, day)
    assert wired.stock_factor("VALE3", day) == plain.stock_factor("VALE3", day)


def test_price_control_cuts_the_price_by_the_same_proportion_as_the_profit() -> None:
    order = StateOrder(StateControl.P10, DividendPolicy.NORMAL)
    wired, plain = _wired(order)
    day = date(2022, 6, 15)

    cut = float(payout.profit_cut(StateControl.P10))

    assert cut == pytest.approx(0.15)
    assert wired.stock_factor(IMPORTED, day) == pytest.approx(
        plain.stock_factor(IMPORTED, day) * (1 - cut)
    )
    # A ação que não é estatal não sente a ordem
    assert wired.stock_factor("VALE3", day) == plain.stock_factor("VALE3", day)


def test_the_order_only_acts_from_the_month_it_is_in_force() -> None:
    order = StateOrder(StateControl.P10, DividendPolicy.NORMAL)
    wired, plain = _wired(order)

    assert wired.stock_factor(IMPORTED, date(2022, 5, 31)) == plain.stock_factor(
        IMPORTED, date(2022, 5, 31)
    )


def test_the_price_factor_of_an_order_reflects_only_the_control() -> None:
    cut = float(payout.profit_cut(StateControl.P10))

    for policy in DividendPolicy:
        assert price.price_factor(StateOrder(StateControl.NONE, policy)) == 1.0
        assert price.price_factor(StateOrder(StateControl.P10, policy)) == (
            pytest.approx(1 - cut)
        )


def test_reinvesting_pays_in_the_price_later_and_squeezing_charges_later() -> None:
    reinvest = price.sustained_policy_factor(DividendPolicy.REINVEST)
    normal = price.sustained_policy_factor(DividendPolicy.NORMAL)
    squeeze = price.sustained_policy_factor(DividendPolicy.SQUEEZE)

    assert normal == 1.0
    assert reinvest > 1.0 > squeeze
    # O efeito cresce com os meses seguidos na política
    short = price.sustained_policy_factor(DividendPolicy.REINVEST, 12)
    assert 1.0 < short < reinvest


def test_the_dividend_factor_is_one_without_an_order() -> None:
    wired, plain = _wired(None)
    day = date(2022, 6, 15)

    assert wired.dividend_factor(IMPORTED, day) == plain.dividend_factor(IMPORTED, day)
    assert wired.dividend_factor(IMPORTED, day) == 1.0


def test_squeezing_raises_the_imported_dividend_by_the_payout_over_normal() -> None:
    wired, _ = _wired(StateOrder(StateControl.NONE, DividendPolicy.SQUEEZE))

    # O histórico já paga o payout Normal (50%); o aperto paga 80%
    assert wired.dividend_factor(IMPORTED, date(2022, 6, 15)) == pytest.approx(
        0.8 / 0.5
    )


def test_the_control_cut_also_shrinks_the_imported_dividend() -> None:
    wired, _ = _wired(StateOrder(StateControl.P10, DividendPolicy.SQUEEZE))

    assert wired.dividend_factor(IMPORTED, date(2022, 6, 15)) == pytest.approx(
        (0.8 / 0.5) * (1 - 0.15)
    )


def test_the_price_factor_is_separate_from_the_dividend_factor() -> None:
    wired, plain = _wired(StateOrder(StateControl.NONE, DividendPolicy.SQUEEZE))
    day = date(2022, 6, 15)

    # O primeiro mês de aperto encolhe o porte um passo, e o preço anda essa fração do mês
    month = price.policy_price_factor(gdp.size_path([DividendPolicy.SQUEEZE]))
    elapsed = (day.day - 1) / 30
    assert wired.stock_factor(IMPORTED, day) == pytest.approx(
        plain.stock_factor(IMPORTED, day) * month**elapsed
    )
    assert wired.stock_factor(IMPORTED, day) < plain.stock_factor(IMPORTED, day)
    assert wired.dividend_factor(IMPORTED, day) == pytest.approx(1.6)


def test_the_policy_price_accumulates_month_after_month() -> None:
    history: History = {
        date(2022, month, 1): {IMPORTED: StateOrder(dividend_policy=policy)}
        for month, policy in [(6, DividendPolicy.SQUEEZE), (7, DividendPolicy.NORMAL)]
    }
    book = StateCompanyBook(1, 7, lambda: history, [_company()])

    assert book.price_factor(IMPORTED, date(2022, 6, 1)) == 1.0
    squeezed = book.price_factor(IMPORTED, date(2022, 6, 30))
    assert squeezed < 1.0
    # A empresa segue menor depois do aperto, então o preço continua crescendo menos
    assert book.price_factor(IMPORTED, date(2022, 9, 15)) < book.price_factor(
        IMPORTED, date(2022, 7, 1)
    )


# A estatal fundada: dividendo mensal e o que chega ao Tesouro


def _founded_book(history: History | None = None) -> StateCompanyBook:
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    orders = history if history is not None else {}
    return StateCompanyBook(simulation_id, 7, lambda: orders)


def _found(book: StateCompanyBook):
    company = book.found(
        ticker=FOUNDED,
        name="Petro Nova",
        size=StateCompanySize.SMALL,
        lever=StateLever.FUEL,
        real_interest=Decimal("0.05"),
        today=FOUNDED_ON,
    )
    assert company is not None
    return company


def test_a_founded_company_pays_the_month_dividend_to_every_shareholder(
    database: Engine,
) -> None:
    book = _founded_book()
    company = _found(book)

    [row] = book.on_month(date(2022, 5, 31))

    # A data ex é o pregão seguinte ao fechamento; o evento sai pela via dos eventos corporativos
    ex_date = date(2022, 6, 1)
    events = repository.corporate_event.get_between(
        date(2022, 5, 31), ex_date, book._simulation_id
    )
    [event] = [e for e in events if e.stock_id == company.stock_id]
    assert event.kind is CorporateEventKind.DIVIDEND
    assert event.ex_date == ex_date
    total = book.month_dividend(company, date(2022, 5, 1))
    assert total > 0
    assert event.value == pytest.approx(float(total / company.shares))
    # O Tesouro recebe a fatia do governo sobre o mesmo total
    assert row.treasury_dividend == total * FOUNDING_GOVERNMENT_SHARE


def test_the_dividend_follows_the_payout_policy_and_the_control_cut(
    database: Engine,
) -> None:
    order = StateOrder(StateControl.P10, DividendPolicy.SQUEEZE)
    book = _founded_book({date(2022, 5, 1): {FOUNDED: order}})
    company = _found(book)

    [row] = book.on_month(date(2022, 5, 31))

    assert book.month_dividend(company, date(2022, 5, 1)) == payout.dividend(
        max(row.profit, Decimal(0)), order.dividend_policy, order.control
    )


def test_the_treasury_receives_the_government_share_of_the_month_dividend(
    database: Engine,
) -> None:
    book = _founded_book()
    company = _found(book)
    month = date(2022, 5, 1)

    received = book.treasury_dividends(date(2022, 5, 31))

    assert received == book.month_dividend(company, month) * FOUNDING_GOVERNMENT_SHARE
    assert received > 0
    # Antes do primeiro mês fechado e sem estatal fundada o Tesouro não recebe nada
    assert book.treasury_dividends(date(2022, 4, 30)) == 0
    assert StateCompanyBook(1, 7, dict).treasury_dividends(date(2022, 5, 31)) == 0


def test_a_founded_stock_follows_its_own_price_and_not_the_exchange(
    database: Engine,
) -> None:
    book = _founded_book()
    _found(book)
    layer = EconomyLayer(1, START, fx.SpendingEconomy())
    layer.use_state_companies(
        StateFactors(book.is_founded, book.price_factor, book.dividend_factor)
    )

    assert layer.stock_factor(FOUNDED, date(2022, 6, 15)) == 1.0
    assert layer.dividend_factor(FOUNDED, date(2022, 6, 15)) == 1.0


# A estatal importada: o provento histórico escalado pela ordem, na tela e no orçamento

EX_DATE = date(2022, 6, 10)
HISTORIC_PER_SHARE = 2.0
# 1000 ações a 50% de governo: o Tesouro tem 500 ações
GOVERNMENT_SHARES = 500
HISTORIC_RECEIVED = Decimal(GOVERNMENT_SHARES) * 2


def _imported_book(history: History | None = None) -> StateCompanyBook:
    """A importada da base com o provento histórico de 2,00 por ação na data ex de junho."""
    stock = repository.stock.add_stock(IMPORTED, "Petrobras", AssetClass.STOCK)
    repository.state_company.mark(
        IMPORTED,
        StateOwnedStockRequest(
            government_share=Decimal("0.5"), shares=1000, lever=StateLever.FUEL
        ),
    )
    repository.corporate_event.replace_real(
        stock.id,
        [
            CorporateEventDTO(
                stock_id=stock.id,
                ex_date=EX_DATE,
                kind=CorporateEventKind.DIVIDEND,
                value=HISTORIC_PER_SHARE,
            )
        ],
        date(2022, 1, 1),
    )
    simulation_id = repository.simulation.create_simulation(simulation_settings())
    repository.state_company.copy_marks(simulation_id)
    orders = history if history is not None else {}
    return StateCompanyBook(
        simulation_id,
        7,
        lambda: orders,
        repository.state_company.of_simulation(simulation_id),
    )


def test_an_imported_company_without_order_adds_nothing_to_the_budget_and_shows_the_historic_total(
    database: Engine,
) -> None:
    book = _imported_book()
    [company] = book.companies()

    # Fator 1: o desvio é exatamente zero e o orçamento fica igual ao histórico
    assert book.budget_dividends(date(2022, 6, 30)) == 0
    assert book.treasury_dividends(date(2022, 6, 30)) == HISTORIC_RECEIVED
    # Fora do mês da data ex o Tesouro não recebe nada
    assert book.treasury_dividends(date(2022, 5, 31)) == 0
    assert book.imported_dividends_12m(company, date(2022, 9, 15)) == HISTORIC_RECEIVED


def test_squeezing_the_imported_company_adds_the_positive_deviation_to_the_budget(
    database: Engine,
) -> None:
    order = StateOrder(StateControl.NONE, DividendPolicy.SQUEEZE)
    book = _imported_book({JUNE: {IMPORTED: order}})
    [company] = book.companies()

    # Fator 1,6: o Tesouro recebe 1600 e o orçamento soma os 600 acima da história
    assert book.treasury_dividends(date(2022, 6, 30)) == HISTORIC_RECEIVED * 8 / 5
    assert book.budget_dividends(date(2022, 6, 30)) == HISTORIC_RECEIVED * 3 / 5
    assert book.imported_dividends_12m(
        company, date(2022, 9, 15)
    ) == book.treasury_dividends(date(2022, 6, 30))


def test_the_price_control_makes_the_budget_deviation_negative(
    database: Engine,
) -> None:
    order = StateOrder(StateControl.P10, DividendPolicy.NORMAL)
    book = _imported_book({JUNE: {IMPORTED: order}})

    # P10 corta 15% do lucro: o Tesouro recebe 850 e o orçamento perde 150 da história
    assert book.treasury_dividends(date(2022, 6, 30)) == HISTORIC_RECEIVED * Decimal(
        "0.85"
    )
    assert book.budget_dividends(date(2022, 6, 30)) == -HISTORIC_RECEIVED * Decimal(
        "0.15"
    )


def test_the_privatized_imported_company_takes_the_historic_dividend_out_of_the_budget(
    database: Engine,
) -> None:
    book = _imported_book()
    [company] = book.companies()
    privatized = company.model_copy(
        update={
            "status": StateCompanyStatus.PRIVATIZED,
            "privatized_on": date(2022, 6, 1),
        }
    )
    sold = StateCompanyBook(book._simulation_id, 7, dict, [privatized])

    # A história ainda paga a União; vendida, a receita do orçamento perde esse provento
    assert sold.treasury_dividends(date(2022, 6, 30)) == 0
    assert sold.budget_dividends(date(2022, 6, 30)) == -HISTORIC_RECEIVED


def test_the_founded_company_gives_the_budget_the_whole_treasury_dividend(
    database: Engine,
) -> None:
    book = _founded_book()
    _found(book)
    month_end = date(2022, 5, 31)

    assert book.budget_dividends(month_end) == book.treasury_dividends(month_end) > 0


def test_the_order_preview_gives_the_imported_company_the_treasury_dividend_of_each_option(
    database: Engine,
) -> None:
    book = _imported_book()
    today = date(2022, 6, 20)

    preview = build_order_preview(
        book, IMPORTED, today=today, can_command=True, given={}, name="Petrobras"
    )

    steps = {step.control: step for step in preview.steps}
    assert steps[StateControl.NONE].monthly_treasury_dividend == HISTORIC_RECEIVED
    assert steps[StateControl.P10].monthly_treasury_dividend == HISTORIC_RECEIVED * (
        Decimal("0.85")
    )
    policies = {p.dividend_policy: p for p in preview.policies}
    assert policies[DividendPolicy.SQUEEZE].monthly_treasury_dividend == (
        HISTORIC_RECEIVED * Decimal("1.6")
    )
    assert policies[DividendPolicy.REINVEST].monthly_treasury_dividend == (
        HISTORIC_RECEIVED / 2
    )


def test_the_order_preview_uses_the_monthly_average_when_the_month_has_no_event(
    database: Engine,
) -> None:
    book = _imported_book()

    preview = build_order_preview(
        book,
        IMPORTED,
        today=date(2022, 8, 20),
        can_command=True,
        given={},
        name="Petrobras",
    )

    # O único provento dos 12 meses anteriores, repartido em 12 meses
    steps = {step.control: step for step in preview.steps}
    assert steps[StateControl.NONE].monthly_treasury_dividend == pytest.approx(
        HISTORIC_RECEIVED / 12
    )


@pytest.fixture
def flat_economy(indicators: SetIndicator) -> None:
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2030, 1, 1), "0.0551"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 144, "0.33"))


def _course(state_dividends: Decimal | None) -> BudgetCourse:
    account = budget.initial_account(START, InitialAccount.PLAYABLE)
    if state_dividends is None:
        return BudgetCourse(
            START, lambda _day: DEFAULT_TAX_POLICY, account, MacroCourse(START)
        )
    return BudgetCourse(
        START,
        lambda _day: DEFAULT_TAX_POLICY,
        account,
        MacroCourse(START),
        state_dividends_on=lambda _day: state_dividends,
    )


def test_the_dividends_of_the_state_companies_enter_the_revenue_of_the_budget(
    flat_economy: None,
) -> None:
    day = date(2020, 1, 31)
    without = _course(None).months_until(day)[-1]
    with_dividends = _course(Decimal(10_000_000_000)).months_until(day)[-1]

    assert without.state_dividends == 0
    assert with_dividends.state_dividends > 0
    assert with_dividends.revenue == without.revenue + with_dividends.state_dividends
    # Receita a mais melhora o resultado primário do mês
    assert with_dividends.primary > without.primary
