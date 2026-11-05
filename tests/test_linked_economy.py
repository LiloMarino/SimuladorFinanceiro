"""
A economia interligada: sem ação do governo a partida é a história; com ela, as
ligações de um mês valem do seguinte em diante e o resultado não depende de quando se lê.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.enum import (
    EconomyLink,
    IndicatorSeries,
    InitialAccount,
    MeasureKind,
    MeasureStatus,
)
from backend.core.indicators import annual_index_rate
from backend.core.repository.economic import IndicatorHistory
from backend.core.utils import last_day_of_month
from backend.features.economy.growth import MacroCourse
from backend.features.economy.panel import build_economy_panel
from backend.features.government import budget
from backend.features.government.budget import base_spending_on
from backend.features.government.linked_economy import LinkedEconomy
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.government.state import Measure
from backend.features.tax_policy import DEFAULT_TAX_POLICY
from tests.fakes import monthly_series

START = date(2020, 1, 1)
SIMULATION = 1


@pytest.fixture
def stored_series(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    As séries em memória, com a camada registrada da partida aplicada na leitura sem
    `stored`: a mesma regra do repositório, sem o banco. SELIC de ~10,6% ao ano, IPCA
    de ~4,3% e Ibovespa subindo 8% ao ano, de 2016 a 2032.
    """
    histories = {
        IndicatorSeries.SELIC: monthly_series(date(2016, 1, 1), 204, "0.04"),
        IndicatorSeries.CDI: monthly_series(date(2016, 1, 1), 204, "0.04"),
        IndicatorSeries.IPCA: monthly_series(date(2016, 1, 1), 204, "0.35"),
        IndicatorSeries.IBOV: {
            day: Decimal(str(round(100000 * 1.08 ** (index / 12), 2)))
            for index, day in enumerate(monthly_series(date(2016, 1, 1), 204, "0"))
        },
    }
    cache: dict[IndicatorSeries, IndicatorHistory] = {}

    def get_history(
        series: IndicatorSeries,
        _simulation_id: int | None = None,
        *,
        stored: bool = False,
    ) -> IndicatorHistory:
        values = histories.get(series, {})
        history = IndicatorHistory(sorted(values), values)
        adjustment = repository.economic._adjustments.get(SIMULATION)
        if stored or adjustment is None:
            return history
        if series not in cache:
            cache[series] = adjustment.adjust(series, history)
        return cache[series]

    monkeypatch.setattr(repository.economic, "_adjustments", {})
    monkeypatch.setattr(repository.economic, "get_history", get_history)
    monkeypatch.setattr(
        repository.economic, "refresh_adjusted", lambda _simulation_id: cache.clear()
    )


def aux(value: str, effective: date) -> Measure:
    return Measure(
        id=1,
        kind=MeasureKind.WELFARE_SPENDING,
        value=Decimal(value),
        before=Decimal("0.015"),
        sector=None,
        segment=None,
        proposer_id=1,
        term_start=START,
        proposed=START,
        status=MeasureStatus.APPROVED,
        effective=effective,
    )


def economy(
    measures: list[Measure] | None = None,
    extra_spending: Callable[[date], Decimal] = lambda _day: Decimal(0),
) -> LinkedEconomy:
    spending = SpendingEconomy()
    linked = LinkedEconomy(
        SIMULATION,
        START,
        MacroCourse(START),
        budget.initial_account(START, InitialAccount.PLAYABLE),
        lambda _day: DEFAULT_TAX_POLICY,
        lambda day: base_spending_on(day) + extra_spending(day),
        lambda _day: Decimal(0),
        spending,
    )
    spending.update(measures or [])
    return linked


def month_ends(until: date) -> list[date]:
    ends, day = [], last_day_of_month(START)
    while day <= until:
        ends.append(day)
        day = last_day_of_month(day + timedelta(days=1))
    return ends


def spender(effective: date = date(2020, 4, 1)) -> LinkedEconomy:
    """Auxílio de 1,5% para 3% do PIB e 2% do PIB a mais de gasto, desde abril de 2020."""
    return economy(
        [aux("0.03", effective)],
        lambda day: Decimal("0.02") if day >= effective else Decimal(0),
    )


def test_without_the_government_the_game_is_the_history(stored_series: None):
    linked = economy()
    end = date(2022, 12, 31)

    linked.close_until(end)

    for month_end in month_ends(end):
        country = linked.macro.latest(month_end)
        assert country.growth == country.base_growth
        assert country.unemployment == country.base_unemployment
        game = linked.budget.latest(month_end)
        base = linked.base_budget().latest(month_end)
        assert (game.debt, game.premium) == (base.debt, base.premium)
    assert all(link.is_zero for link in linked.links_until(end))
    assert linked.layer.first_day() is None
    assert annual_index_rate(IndicatorSeries.SELIC, end) == annual_index_rate(
        IndicatorSeries.SELIC, end, stored=True
    )
    assert linked.premium_gap_on(end) == 0


def test_a_spender_moves_the_links_from_the_month_after(stored_series: None):
    linked = spender()
    end = date(2022, 12, 31)

    linked.close_until(end)

    last = linked.links_until(end)[-1]
    assert last.month_end == end
    # Gasto a mais é primário abaixo da história, dívida e prêmio acima dela
    assert last.primary_gap < 0
    assert last.premium_gap > 0
    # O empurrão no crescimento vale no ano em que o gasto subiu; mantido o patamar, acaba
    first_year = linked.links_until(date(2020, 12, 31))[-1]
    assert first_year.impulse > 0
    assert last.impulse == 0
    # A ligação de um mês vale do primeiro dia do seguinte em diante
    november = linked.links_until(date(2022, 11, 30))[-1]
    assert linked.links_on(date(2022, 12, 30)) == november
    assert linked.links_on(date(2023, 1, 2)) == last
    assert linked.premium_gap_on(date(2023, 1, 2)) == last.premium_gap


def test_reading_month_by_month_or_at_once_gives_the_same_economy(
    stored_series: None,
):
    end = date(2023, 6, 30)
    stepped = spender()
    for month_end in month_ends(end):
        stepped.close_until(month_end)
    stepped_links = stepped.links_until(end)
    stepped_debt = stepped.budget.latest(end).debt

    at_once = spender()
    at_once.close_until(end)

    assert at_once.links_until(end) == stepped_links
    assert at_once.budget.latest(end).debt == stepped_debt


def test_a_closed_month_never_changes(stored_series: None):
    linked = spender()
    linked.close_until(date(2021, 6, 30))
    before = linked.links_until(date(2021, 6, 30))

    linked.close_until(date(2022, 6, 30))

    assert linked.links_until(date(2021, 6, 30)) == before


def test_ten_years_of_spending_stay_finite(stored_series: None):
    linked = economy(
        [aux("0.05", date(2020, 4, 1))],
        lambda day: Decimal("0.05") if day >= date(2020, 4, 1) else Decimal(0),
    )
    end = date(2029, 12, 31)

    linked.close_until(end)

    month = linked.budget.latest(end)
    country = linked.macro.latest(end)
    assert math.isfinite(month.debt) and month.debt > 0
    assert math.isfinite(month.premium)
    assert -1 < country.growth < 1
    assert 0 < country.unemployment < 1
    level = linked.layer.level(end)
    assert math.isfinite(level) and level > 0
    assert math.isfinite(linked.layer.inflation_points(end))


def test_the_panel_splits_the_debt_the_links_and_the_growth_by_cause(
    stored_series: None,
):
    linked = spender()
    end = date(2022, 12, 31)

    panel = build_economy_panel(START, end, linked.macro, linked)

    debt = panel.debt
    assert debt is not None
    # As quatro causas somam a variação dos últimos 12 meses fechados
    year_ago = linked.budget.latest(date(2021, 12, 31)).debt
    causes = debt.causes
    assert causes.months == 12
    assert causes.interest + causes.growth + causes.inflation + causes.primary == (
        pytest.approx(debt.debt - year_ago, abs=Decimal("1e-20"))
    )
    assert debt.history_debt == linked.base_budget().latest(end).debt
    assert debt.debt > debt.history_debt

    links = {effect.link: effect for effect in panel.links or []}
    risk = links[EconomyLink.FISCAL_RISK]
    assert risk.gap == linked.links_on(end).premium_gap > 0
    assert risk.inflation > 0
    assert risk.selic == pytest.approx(
        risk.inflation * Decimal("1.5"), abs=Decimal("0.001")
    )
    assert risk.stocks < 0
    assert links[EconomyLink.GDP].inflation == 0

    parts = panel.growth_parts
    assert parts.growth == pytest.approx(
        parts.history_growth
        + parts.real_rate
        + parts.stocks
        + parts.works
        + parts.impulse
    )
