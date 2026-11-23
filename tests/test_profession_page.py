"""A página Profissão: o cabeçalho, as séries e o bloco da mecânica de cada profissão, a hora extra que volta e o patrimônio travado do FGTS."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.profession import (
    OVERTIME_AVAILABLE,
    OVERTIME_ENDED,
    OVERTIME_ON,
    CltState,
    SetOvertime,
)
from backend.core.dto.profession_page import CltMechanicDTO, PublicServantMechanicDTO
from backend.core.enum import (
    GameType,
    IncomeSeriesKey,
    LifeHistoryKind,
    LockedAssetKind,
    MeasureKind,
    MechanicStatus,
    Profession,
    SalaryMode,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.professions import LifeLevers
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.profession.page import _lever_changes, appointee_block
from backend.features.simulation import simulation as simulation_module
from backend.features.simulation.simulation_loader import SimulationLoader
from tests.test_bots import (  # noqa: F401
    person,
    refusal,
    room,
    rules,
    started,
)
from tests.test_clt import (
    GROWING,
    RECESSION,
    turn_of_month,
    with_growth,
    with_tr,
)
from tests.test_profession_mechanics import life_history, match
from tests.test_professions import budget

pytestmark = pytest.mark.usefixtures("room")


def clt_mechanic(sim, client_id) -> CltMechanicDTO:
    """O bloco da mecânica do CLT na página da pessoa."""
    mechanic = sim.get_profession_page(client_id).mechanic
    assert isinstance(mechanic, CltMechanicDTO)
    return mechanic


def keys_of_actions(sim, client_id) -> list[str | None]:
    return [
        r.life_event_key
        for r in life_history(sim, client_id)
        if r.kind is LifeHistoryKind.PROFESSION_ACTION
    ]


def test_the_clt_page_has_the_fgts_the_overtime_and_the_gdp_and_unemployment_series(
    monkeypatch,
):
    with_tr(monkeypatch, "0.2")
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    page = sim.get_profession_page(ana.client_id)

    assert page.profession is Profession.CLT
    assert page.mechanic.kind == "clt"
    assert page.mechanic.fgts_balance == Decimal(10000)
    assert page.mechanic.layoff_payout == Decimal(14000)
    assert page.mechanic.status is MechanicStatus.AVAILABLE
    assert page.mechanic.overtime_offered
    assert [s.key for s in page.series] == [
        IncomeSeriesKey.GDP,
        IncomeSeriesKey.UNEMPLOYMENT,
    ]
    gdp = page.series[0]
    assert len(gdp.points) == 12 and gdp.guides[0].overtime
    assert page.header.layoff_factor is not None
    assert page.header.real_raise is not None


def test_the_overtime_is_locked_in_a_recession_and_active_when_on(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, RECESSION)
    assert clt_mechanic(sim, ana.client_id).status is MechanicStatus.LOCKED

    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    page = sim.get_profession_page(ana.client_id)

    assert clt_mechanic(sim, ana.client_id).status is MechanicStatus.ACTIVE
    assert page.header.mechanic_income > 0


def test_the_servant_page_shows_the_margin_and_the_lever_series(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)

    page = sim.get_profession_page(ana.client_id)

    assert page.mechanic.kind == "public_servant"
    assert page.mechanic.status is MechanicStatus.AVAILABLE
    assert page.mechanic.margin_free == page.mechanic.margin > 0
    assert page.mechanic.loans == [] and page.mechanic.next_release is None
    levers = [s for s in page.series if s.lever]
    assert [s.key for s in levers] == [IncomeSeriesKey.SERVANT_RAISE]
    assert levers[0].changes == []


def test_the_servant_page_locks_when_the_margin_is_all_used(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch, starting_cash=Decimal(1000000))
    sim.switch_profession(ana, Profession.PUBLIC_SERVANT)
    quote = sim.quote_payroll(ana, ana.client_id, Decimal(1000), 24)
    sim.contract_payroll(ana, ana.client_id, quote.max_amount, 24)

    mechanic = sim.get_profession_page(ana.client_id).mechanic
    assert isinstance(mechanic, PublicServantMechanicDTO)

    assert len(mechanic.loans) == 1
    assert mechanic.margin_free == 0
    assert mechanic.status is MechanicStatus.LOCKED
    assert mechanic.next_release is not None
    # O consignado único libera a própria parcela ao terminar; a SELIC é o juro menos o spread
    assert mechanic.next_release_amount == mechanic.loans[0].installment
    assert mechanic.selic == mechanic.annual_rate - Decimal("0.02")


def test_the_banker_page_lists_the_three_house_cdbs(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.BANKER)
    turn_of_month(sim)

    page = sim.get_profession_page(ana.client_id)

    assert page.mechanic.kind == "banker"
    assert [c.years for c in page.mechanic.cdbs] == [1, 2, 3]
    for cdb in page.mechanic.cdbs:
        assert cdb.annual_rate - cdb.treasury_rate == Decimal("0.01")
        assert cdb.cap > 0 and cdb.applied == 0
    assert page.mechanic.status is MechanicStatus.AVAILABLE


def test_the_retiree_has_no_mechanic_and_only_the_lever_series(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.RETIREE)

    page = sim.get_profession_page(ana.client_id)

    assert page.mechanic.kind == "retiree"
    assert page.header.layoff_factor is None and page.header.income_loss is None
    assert [s.key for s in page.series] == [IncomeSeriesKey.RETIREE_RAISE]


def test_the_heir_page_shows_the_inheritance(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.HEIR)

    page = sim.get_profession_page(ana.client_id)

    assert page.mechanic.kind == "heir"
    assert page.mechanic.inheritance > 0 and page.mechanic.covered_years > 0
    # A renda do Herdeiro só sobe com o IPCA: nenhum indicador a move
    assert page.series == [] and page.header.real_raise is None


def test_the_page_is_refused_without_the_professions_mode(monkeypatch):
    ana = person("Ana")
    settings = rules(
        game_type=GameType.FINANCIAL_INDEPENDENCE,
        salary_mode=SalaryMode.EQUAL,
        unexpected_per_year=0,
    )
    monkeypatch.setattr(SettingsManager, "_settings", settings)
    SimulationLoader.create(settings)
    sim = SimulationManager.get_active_simulation()

    with pytest.raises(ConflictError):
        sim.get_profession_page(ana.client_id)


def test_the_overtime_that_the_recession_ended_is_announced_once_when_it_can_return(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)
    sent: list[str] = []
    monkeypatch.setattr(
        simulation_module,
        "notify",
        lambda event, *args, **kwargs: sent.append(event),
    )
    with_growth(sim, monkeypatch, GROWING)
    sim.apply_profession_action(ana, SetOvertime(kind=OVERTIME_ON))
    with_growth(sim, monkeypatch, RECESSION)
    turn_of_month(sim)
    assert clt_mechanic(sim, ana.client_id).overtime_waiting

    with_growth(sim, monkeypatch, GROWING)
    turn_of_month(sim)
    turn_of_month(sim)

    assert keys_of_actions(sim, ana.client_id) == [
        OVERTIME_ON,
        OVERTIME_ENDED,
        OVERTIME_AVAILABLE,
    ]
    assert sent.count("overtime_available") == 1
    assert not clt_mechanic(sim, ana.client_id).overtime_waiting


def test_the_fgts_is_a_locked_asset_with_the_exit_rule(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    portfolio = sim.get_portfolio(ana.client_id)

    assert [(a.kind, a.value, a.exit_rule) for a in portfolio.locked_assets] == [
        (LockedAssetKind.FGTS, Decimal(10000), LOCKED_EXITS[LockedAssetKind.FGTS].rule)
    ]


def test_the_banker_page_reads_the_term_and_the_value_today_of_each_cdb(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch, starting_cash=Decimal(1000000))
    sim.switch_profession(ana, Profession.BANKER)
    turn_of_month(sim)
    market = sim._engine.fixed_income_market
    two_years = market.get_house_asset(ana.client_id, 2)
    assert two_years is not None
    sim.buy_fixed_income(ana.client_id, two_years, Decimal(1000))

    mechanic = sim.get_profession_page(ana.client_id).mechanic
    assert mechanic.kind == "banker"

    assert [c.years for c in mechanic.cdbs] == list(
        market.get_house_terms(ana.client_id)
    )
    by_years = {c.years: c for c in mechanic.cdbs}
    assert by_years[1].current_value == 0 and by_years[3].current_value == 0
    assert by_years[2].applied == 1000
    assert by_years[2].current_value >= by_years[2].applied > 0


def test_the_appointee_block_counts_the_months_to_the_election():
    life = budget(Profession.COMMISSIONED)
    today = date(2024, 3, 10)

    ahead = appointee_block(life, today, "XYZ", date(2024, 10, 6))
    same_month = appointee_block(life, today, "XYZ", date(2024, 3, 24))
    none = appointee_block(life, today, "XYZ", None)

    assert ahead.election_in_months == 7
    assert same_month.election_in_months == 0
    assert none.election_in_months is None


def test_each_locked_asset_carries_its_share_of_the_networth(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))

    portfolio = sim.get_portfolio(ana.client_id)

    [fgts] = portfolio.locked_assets
    assert fgts.networth_pct == fgts.value / portfolio.assets_value
    assert fgts.networth_pct == portfolio.locked_networth_pct


def test_each_lever_change_carries_who_proposed_the_measure():
    switch = date(2022, 6, 1)

    def levers_on(on: date) -> LifeLevers:
        return LifeLevers(servant_raise=Decimal("0.03") if on >= switch else Decimal(0))

    def author_on(kind: MeasureKind, on: date) -> tuple[str | None, str | None]:
        assert kind is MeasureKind.SERVANT_RAISE
        return ("Alice", "AAA") if on >= switch else (None, None)

    [change] = _lever_changes(
        date(2022, 9, 1),
        lambda lv: lv.servant_raise,
        levers_on,
        MeasureKind.SERVANT_RAISE,
        author_on,
    )

    assert (change.before, change.after) == (Decimal(0), Decimal("0.03"))
    assert (change.proposer_name, change.proposer_party) == ("Alice", "AAA")


def test_a_room_without_government_has_no_author_on_the_lever(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    assert sim._lever_author_on(MeasureKind.SERVANT_RAISE, date(2022, 6, 1)) == (
        None,
        None,
    )
    assert sim.get_profession_page(ana.client_id) is not None
