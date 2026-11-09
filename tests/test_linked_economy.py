"""
A economia interligada: sem ação do governo a partida é a história; com ela, as
ligações de um mês valem do seguinte em diante e o resultado não depende de quando se lê.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.economy import LinkEffectDTO
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
from backend.features.economy.growth import (
    UNEMPLOYMENT_HALF_LIFE_MONTHS,
    MacroCourse,
    next_month,
    starting_month,
)
from backend.features.economy.monetary import Monetary, SelicBoard, SelicDecision
from backend.features.economy.panel import build_economy_panel
from backend.features.government import budget
from backend.features.government.budget import base_spending_on
from backend.features.government.linked_economy import LinkedEconomy
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.government.state import Measure
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy
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
    monetary: Monetary | None = None,
    policy_on: Callable[[date], TaxPolicy] = lambda _day: DEFAULT_TAX_POLICY,
) -> LinkedEconomy:
    spending = SpendingEconomy()
    linked = LinkedEconomy(
        SIMULATION,
        START,
        MacroCourse(START),
        budget.initial_account(START, InitialAccount.PLAYABLE),
        policy_on,
        lambda day: base_spending_on(day) + extra_spending(day),
        lambda _day: Decimal(0),
        spending,
        monetary or SelicBoard(),
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


def test_the_unemployment_gap_returns_to_the_history_by_half_life(
    stored_series: None,
):
    month = starting_month(START - timedelta(days=1))
    gap = Decimal("0.05")
    month = replace(month, unemployment=month.base_unemployment + gap)
    steps: dict[int, Decimal] = {}

    # Sem governo o crescimento é o da história: só a volta mexe no desvio
    for elapsed in range(1, 2 * UNEMPLOYMENT_HALF_LIFE_MONTHS + 1):
        month = next_month(
            month, last_day_of_month(month.month_end + timedelta(days=1))
        )
        steps[elapsed] = month.unemployment - month.base_unemployment

    assert steps[UNEMPLOYMENT_HALF_LIFE_MONTHS] == pytest.approx(
        gap / 2, abs=Decimal("1e-6")
    )
    assert steps[2 * UNEMPLOYMENT_HALF_LIFE_MONTHS] == pytest.approx(
        gap / 4, abs=Decimal("1e-6")
    )


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
    # O primário do fechamento e o que estabiliza a dívida, da partida e da história
    assert debt.primary == linked.budget.latest(end).primary
    assert math.isfinite(debt.stabilizing_primary)
    assert math.isfinite(debt.history_stabilizing_primary)

    links = {effect.link: effect for effect in panel.links or []}
    risk = links[EconomyLink.FISCAL_RISK]
    assert risk.gap == linked.links_on(end).premium_gap > 0
    # O prêmio não soma IPCA direto: ele passa pelo dólar
    assert risk.inflation == 0
    assert risk.stocks < 0
    dollar = links[EconomyLink.DOLLAR]
    assert dollar.gap == pytest.approx(
        Decimal(str(linked.links_on(end).dollar_gap)), abs=Decimal("1e-6")
    )
    assert dollar.gap > 0
    assert dollar.inflation > 0
    assert dollar.selic == pytest.approx(
        dollar.inflation * Decimal("1.5"), abs=Decimal("0.001")
    )
    assert panel.dollar_parts.total > panel.dollar_parts.history
    assert panel.dollar_parts.inflation == dollar.inflation
    assert links[EconomyLink.GDP].inflation == 0

    parts = panel.growth_parts
    assert parts.growth == pytest.approx(
        parts.history_growth
        + parts.real_rate
        + parts.stocks
        + parts.works
        + parts.impulse
        + parts.inflation
        + parts.crowding_out
    )


def selic_set(selic: str, credibility: float = 100) -> SelicBoard:
    """O governo fixou a SELIC antes do primeiro dia da partida."""
    board = SelicBoard()
    board.record(SelicDecision(START - timedelta(days=1), Decimal(selic), credibility))
    return board


def test_the_government_selic_replaces_the_series(stored_series: None):
    linked = economy(monetary=selic_set("0.076"))
    day = date(2020, 6, 15)

    linked.close_until(day)

    assert annual_index_rate(IndicatorSeries.SELIC, day) == pytest.approx(
        Decimal("0.076"), abs=Decimal("1e-6")
    )
    assert linked.layer.first_day() == START


def test_a_real_rate_below_history_raises_inflation_with_lag(stored_series: None):
    stored = annual_index_rate(IndicatorSeries.SELIC, START, stored=True)
    linked = economy(monetary=selic_set(str(stored - Decimal("0.03"))))
    end = date(2021, 12, 31)

    linked.close_until(end)

    links = linked.links_until(end)
    # O juro real cai os 3 pontos da SELIC e mais o que a inflação sobe
    assert links[0].real_rate_gap == pytest.approx(
        Decimal("-0.03"), abs=Decimal("0.001")
    )
    assert all(link.real_rate_gap < Decimal("-0.029") for link in links)
    # A defasagem: pouco no começo, mais no segundo ano
    assert 0 < links[0].rate_points < links[11].rate_points < links[-1].rate_points
    assert annual_index_rate(IndicatorSeries.IPCA, end) > annual_index_rate(
        IndicatorSeries.IPCA, end, stored=True
    )


def test_lost_credibility_costs_premium_and_inflation(stored_series: None):
    stored = annual_index_rate(IndicatorSeries.SELIC, START, stored=True)
    selic = str(stored - Decimal("0.03"))
    calm = economy(monetary=selic_set(selic))
    doubted = economy(monetary=selic_set(selic, credibility=0))
    end = date(2020, 12, 31)

    calm.close_until(end)
    doubted.close_until(end)

    assert doubted.budget.latest(end).premium - calm.budget.latest(
        end
    ).premium == pytest.approx(Decimal("0.02"), abs=Decimal("0.001"))
    assert (
        doubted.links_until(end)[-1].rate_points > calm.links_until(end)[-1].rate_points
    )


def taxer(**rates: Decimal) -> LinkedEconomy:
    """Os impostos dados sobem de abril de 2020 em diante; o resto fica no padrão."""
    raised = replace(DEFAULT_TAX_POLICY, **rates)
    return economy(
        policy_on=lambda day: raised if day >= date(2020, 4, 1) else DEFAULT_TAX_POLICY
    )


def effects_of_links(
    linked: LinkedEconomy, end: date
) -> dict[EconomyLink, LinkEffectDTO]:
    panel = build_economy_panel(START, end, linked.macro, linked)
    return {effect.link: effect for effect in panel.links or []}


def test_a_higher_consumption_tax_improves_the_primary_and_raises_prices(
    stored_series: None,
):
    linked = taxer(
        consumption_rate=DEFAULT_TAX_POLICY.consumption_rate + Decimal("0.02")
    )
    end = date(2020, 12, 31)

    linked.close_until(end)

    last = linked.links_until(end)[-1]
    assert last.consumption_gap == Decimal("0.02")
    assert last.primary_gap > 0
    # A alta de 12 meses repassada aos preços: ainda vale no fim do primeiro ano
    assert last.consumption_points > 0
    effect = effects_of_links(linked, end)[EconomyLink.CONSUMPTION_TAX]
    assert effect.inflation > 0
    assert effect.selic > 0


def test_a_higher_corporate_tax_costs_the_stocks_and_a_cut_lifts_them(
    stored_series: None,
):
    up = taxer(corporate_rate=DEFAULT_TAX_POLICY.corporate_rate + Decimal("0.05"))
    down = taxer(corporate_rate=DEFAULT_TAX_POLICY.corporate_rate - Decimal("0.05"))
    end = date(2020, 12, 31)
    up.close_until(end)
    down.close_until(end)

    assert up.layer.stocks_parts(end).corporate < 0
    assert down.layer.stocks_parts(end).corporate > 0
    assert up.layer.level(end) < down.layer.level(end)
    assert effects_of_links(up, end)[EconomyLink.CORPORATE_TAX].stocks < 0


def test_a_higher_payroll_tax_raises_the_unemployment(stored_series: None):
    linked = taxer(payroll_rate=DEFAULT_TAX_POLICY.payroll_rate + Decimal("0.05"))
    end = date(2021, 12, 31)

    linked.close_until(end)

    country = linked.macro.latest(end)
    assert country.unemployment > country.base_unemployment
    effect = effects_of_links(linked, end)[EconomyLink.PAYROLL_TAX]
    assert effect.unemployment > 0
    # A Phillips leva o emprego menor para os preços, sem nenhum gasto a mais
    assert linked.layer.inflation_points(end) != 0


def test_the_personal_income_tax_changes_the_primary_but_no_link(stored_series: None):
    linked = taxer(personal_rate=DEFAULT_TAX_POLICY.personal_rate + Decimal("0.05"))
    end = date(2020, 12, 31)

    linked.close_until(end)

    last = linked.links_until(end)[-1]
    assert last.primary_gap > 0
    assert last.consumption_gap == last.corporate_gap == last.payroll_gap == 0
