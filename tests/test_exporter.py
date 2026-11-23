"""A mecânica do Exportador: o dólar do câmbio futuro, a renda com a trava e o mix, as recusas, o vencimento e a política dos bots."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from backend.core.dates import add_months
from backend.core.dto.profession import (
    EXCHANGE_LOCK,
    EXCHANGE_LOCK_ENDED,
    EXPORT_MIX,
    ExchangeLock,
    ExporterState,
    LockExchange,
    SetExportMix,
)
from backend.core.enum import (
    IndicatorSeries,
    LifeHistoryKind,
    MechanicStatus,
    Profession,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.exporter import forward_dollar, next_quarter_start
from backend.core.life_budget import LifeBudget
from backend.core.professions import DRIVER_CURVES, IncomeDriver, driver_factor
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.exporter import (
    after_payment,
    lock_exchange,
    lock_wanted,
    mix_change_allowed,
    mix_target,
    set_export_mix,
)
from backend.features.simulation import simulation as simulation_module
from backend.features.strategy.bots import resolve_bot
from tests.test_bots import (  # noqa: F401
    person,
    refusal,
    room,
    started,
)
from tests.test_clt import GROWING, STAGNANT, turn_of_month, with_growth
from tests.test_profession_mechanics import life_history, match
from tests.test_professions import budget

DAY = date(2012, 3, 30)
DOLLAR_A_YEAR_AGO = Decimal("2.0")

pytestmark = pytest.mark.usefixtures("room")


def exporter_budget(
    state: ExporterState,
    dollar: str,
    *,
    growth: str = "0.02",
) -> LifeBudget:
    """O orçamento do Exportador com o dólar de hoje em `dollar` e o de um ano atrás em R$ 2,00."""
    today = Decimal(dollar)
    life = budget(Profession.EXPORTER, growth=growth)
    return replace(
        life,
        dollar_on=lambda day: today if day == DAY else DOLLAR_A_YEAR_AGO,
        dollar_change_on=lambda _day: today / DOLLAR_A_YEAR_AGO - 1,
    ).with_mechanic_state(lambda: state)


def lock_of(share: str = "0.5", locked: str = "2.2", months: int = 12) -> ExchangeLock:
    return ExchangeLock(
        share=Decimal(share),
        months=months,
        locked_dollar=Decimal(locked),
        contracted_on=DAY,
    )


def test_the_forward_dollar_follows_the_interest_gap_over_the_term():
    spot, cdi, fed = Decimal("1.79"), Decimal("0.1366"), Decimal("0.0025")

    assert forward_dollar(spot, cdi, fed, 12) == Decimal("2.0294")
    assert forward_dollar(spot, cdi, fed, 6) == Decimal("1.9060")
    # Sem diferença de juros, o dólar travado é o do dia
    assert forward_dollar(spot, fed, fed, 12) == spot


def test_a_partial_lock_pays_less_than_no_lock_when_the_dollar_rises():
    state = ExporterState(lock=lock_of())
    free = exporter_budget(ExporterState(), "2.6")
    locked = exporter_budget(state, "2.6")

    assert locked.salary_on(DAY) < free.salary_on(DAY)
    assert locked.lock_gain_on(DAY) < 0


def test_a_partial_lock_pays_more_than_no_lock_when_the_dollar_falls():
    state = ExporterState(lock=lock_of())
    free = exporter_budget(ExporterState(), "1.6")
    locked = exporter_budget(state, "1.6")

    assert locked.salary_on(DAY) > free.salary_on(DAY)
    assert locked.lock_gain_on(DAY) > 0


def test_the_locked_part_uses_the_locked_dollar_and_the_loose_part_the_dollar_of_the_day():
    curve = DRIVER_CURVES[IncomeDriver.DOLLAR]
    locked_factor = driver_factor(curve, Decimal("2.2") / DOLLAR_A_YEAR_AGO - 1)
    free_factor = driver_factor(curve, Decimal("2.6") / DOLLAR_A_YEAR_AGO - 1)
    life = exporter_budget(ExporterState(lock=lock_of("0.4")), "2.6")

    assert (
        life.dollar_factor_on(DAY)
        == Decimal("0.4") * locked_factor + Decimal("0.6") * free_factor
    )


def test_a_lock_of_the_whole_revenue_ignores_the_dollar_of_the_day():
    state = ExporterState(lock=lock_of("1"))

    rising = exporter_budget(state, "2.6")
    falling = exporter_budget(state, "1.6")

    assert rising.salary_on(DAY) == falling.salary_on(DAY)


def test_the_income_weighs_the_dollar_and_the_gdp_by_the_mix():
    life = exporter_budget(
        ExporterState(export_share=Decimal("0.6")), "2.2", growth="0"
    )
    dollar = driver_factor(DRIVER_CURVES[IncomeDriver.DOLLAR], Decimal("0.1"))
    gdp = driver_factor(DRIVER_CURVES[IncomeDriver.GDP], Decimal("0"))

    assert life.driver_factor_on(DAY) == Decimal("0.6") * dollar + Decimal("0.4") * gdp


def test_the_initial_mix_of_the_whole_revenue_is_the_income_of_the_dollar_alone():
    assert ExporterState().export_share == 1
    with_state = exporter_budget(ExporterState(), "2.6")
    without_state = replace(
        with_state, current_mechanic_state=budget(Profession.CLT).current_mechanic_state
    )

    assert with_state.salary_on(DAY) == without_state.salary_on(DAY)


def test_the_lock_is_refused_while_another_is_active_and_after_the_expiry_it_is_free():
    contract = LockExchange(share=Decimal("0.5"), months=6, locked_dollar=Decimal(2))
    locked = lock_exchange(ExporterState(), contract, DAY)
    assert locked.lock is not None and locked.lock.contracted_on == DAY

    with pytest.raises(ConflictError, match="trava ativa"):
        lock_exchange(locked, contract, DAY)

    state = locked
    for month in range(6):
        state, ended = after_payment(state, Decimal(100))
        assert ended is (month == 5)
    assert state.lock is None
    assert lock_exchange(state, contract, DAY).lock is not None


@pytest.mark.parametrize(
    ("share", "months", "message"),
    [
        ("0.5", 9, "6 ou 12 meses"),
        ("0", 6, "1% a 100%"),
        ("1.01", 6, "1% a 100%"),
    ],
)
def test_the_lock_refuses_the_term_and_the_share_out_of_range(share, months, message):
    action = LockExchange(share=Decimal(share), months=months, locked_dollar=Decimal(2))

    with pytest.raises(ConflictError, match=message):
        lock_exchange(ExporterState(), action, DAY)


def test_the_gain_adds_up_month_by_month_until_the_expiry():
    state = ExporterState(lock=lock_of(months=12))

    state, _ = after_payment(state, Decimal("100.50"))
    state, _ = after_payment(state, Decimal("-30.25"))

    assert state.lock is not None
    assert (state.lock.paid_months, state.lock.gain) == (2, Decimal("70.25"))


def test_the_first_mix_change_is_free_and_the_next_waits_for_the_next_quarter():
    first = set_export_mix(ExporterState(), SetExportMix(share=Decimal("0.6")), DAY)
    assert first.export_share == Decimal("0.6") and first.mix_changed_on == DAY

    with pytest.raises(ConflictError, match="01/04/2012"):
        set_export_mix(first, SetExportMix(share=Decimal("0.3")), date(2012, 3, 31))

    later = set_export_mix(first, SetExportMix(share=Decimal("0.3")), date(2012, 4, 1))
    assert later.export_share == Decimal("0.3")
    assert later.mix_changed_on == date(2012, 4, 1)


def test_the_mix_refuses_the_same_fraction_and_the_values_out_of_range():
    state = ExporterState(export_share=Decimal("0.6"))

    with pytest.raises(ConflictError, match="já está nessa fração"):
        set_export_mix(state, SetExportMix(share=Decimal("0.6")), DAY)
    for share in ("-0.1", "1.1"):
        with pytest.raises(ConflictError, match="0% a 100%"):
            set_export_mix(state, SetExportMix(share=Decimal(share)), DAY)


def test_the_quarter_calendar_releases_the_mix_on_the_first_day_of_the_next_quarter():
    assert next_quarter_start(date(2012, 1, 1)) == date(2012, 4, 1)
    assert next_quarter_start(date(2012, 3, 31)) == date(2012, 4, 1)
    assert next_quarter_start(date(2012, 11, 15)) == date(2013, 1, 1)
    state = ExporterState(mix_changed_on=date(2012, 5, 20))
    assert not mix_change_allowed(state, date(2012, 6, 30))
    assert mix_change_allowed(state, date(2012, 7, 1))
    assert add_months(date(2012, 8, 31), 6) == date(2013, 2, 28)


def turn_dollars(*values: str) -> list[Decimal]:
    return [Decimal(value) for value in values]


def test_the_bot_locks_when_the_dollar_is_above_the_average_of_the_last_twelve_turns():
    twelve = turn_dollars(*["2.0"] * 12)

    assert lock_wanted(ExporterState(), Decimal("2.01"), twelve)
    assert not lock_wanted(ExporterState(), Decimal("2.0"), twelve)
    assert not lock_wanted(ExporterState(), Decimal("1.9"), twelve)


def test_the_bot_does_not_lock_without_twelve_samples_or_with_a_lock_active():
    assert not lock_wanted(ExporterState(), Decimal(9), turn_dollars(*["2.0"] * 11))
    assert not lock_wanted(
        ExporterState(lock=lock_of()), Decimal(9), turn_dollars(*["2.0"] * 12)
    )


@pytest.mark.parametrize(
    ("dollar_change", "growth", "expected"),
    [
        # Os dois acima do neutro, ou os dois abaixo: 50/50
        ("0.05", "0.03", "0.5"),
        ("-0.05", "0.01", "0.5"),
        # Só o dólar acima do neutro: pende para exportar
        ("0.05", "0.01", "0.7"),
        # Só o PIB acima do neutro: pende para o Brasil
        ("-0.05", "0.03", "0.3"),
        # No neutro, nenhum dos dois está acima
        ("0", "0.02", "0.5"),
        ("0", "0.03", "0.3"),
    ],
)
def test_the_bot_mix_follows_the_indicator_above_the_neutral(
    dollar_change, growth, expected
):
    assert mix_target(Decimal(dollar_change), Decimal(growth)) == Decimal(expected)


# A partida com dólar, juros e o PIB que os testes de integração controlam
def with_exchange_market(
    sim, monkeypatch: pytest.MonkeyPatch, *, dollar: str = "2.0"
) -> None:
    value = Decimal(dollar)
    monkeypatch.setattr(sim._engine, "dollar_on", lambda day: value)
    monkeypatch.setattr(
        simulation_module,
        "annual_index_rate",
        lambda series, day: (
            Decimal("0.12") if series is IndicatorSeries.CDI else Decimal("0.02")
        ),
    )


def exporter_state_of(sim, user) -> ExporterState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, ExporterState)
    return state


def exporter_keys(sim, user) -> list[str | None]:
    return [
        row.life_event_key
        for row in life_history(sim, user.client_id)
        if row.kind is LifeHistoryKind.PROFESSION_ACTION
    ]


def test_the_player_locks_the_exchange_and_the_history_records_the_action(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.EXPORTER)
    with_exchange_market(sim, monkeypatch)

    sim.lock_exchange(ana, Decimal("0.5"), 12)

    lock = exporter_state_of(sim, ana).lock
    assert lock is not None
    assert lock.locked_dollar == forward_dollar(
        Decimal(2), Decimal("0.12"), Decimal("0.02"), 12
    )
    assert exporter_keys(sim, ana) == [EXCHANGE_LOCK]
    assert "trava ativa" in refusal(lambda: sim.lock_exchange(ana, Decimal(1), 6))


def test_the_lock_expires_after_its_last_payment_and_the_history_records_the_end(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.EXPORTER)
    with_exchange_market(sim, monkeypatch)
    sim.lock_exchange(ana, Decimal("0.5"), 6)

    for month in range(6):
        turn_of_month(sim)
        lock = exporter_state_of(sim, ana).lock
        assert (lock is None) is (month == 5)
        if lock is not None:
            assert lock.paid_months == month + 1

    assert exporter_keys(sim, ana) == [EXCHANGE_LOCK, EXCHANGE_LOCK_ENDED]
    sim.lock_exchange(ana, Decimal("0.5"), 6)
    assert exporter_state_of(sim, ana).lock is not None


def test_the_mix_changes_once_per_quarter_and_the_history_records_it(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.EXPORTER)

    sim.set_export_mix(ana, Decimal("0.6"))

    assert exporter_state_of(sim, ana).export_share == Decimal("0.6")
    assert exporter_keys(sim, ana) == [EXPORT_MIX]
    assert "trimestre" in refusal(lambda: sim.set_export_mix(ana, Decimal("0.2")))


def test_only_the_exporter_has_the_lock_and_the_mix(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)

    assert "Exportador" in refusal(lambda: sim.lock_exchange(ana, Decimal("0.5"), 12))
    assert "Exportador" in refusal(lambda: sim.set_export_mix(ana, Decimal("0.5")))


def test_the_page_reads_the_exporter_block_in_the_three_states(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim.switch_profession(ana, Profession.EXPORTER)
    with_exchange_market(sim, monkeypatch)

    available = sim.get_profession_page(ana.client_id).mechanic
    assert available.kind == "exporter"
    assert available.status is MechanicStatus.AVAILABLE
    assert available.lock is None and available.can_change_mix
    assert [option.months for option in available.lock_options] == [6, 12]
    assert available.next_mix_change is None
    assert available.mix_factor == available.exported_factor

    sim.lock_exchange(ana, Decimal("0.5"), 12)
    sim.set_export_mix(ana, Decimal("0.6"))
    active = sim.get_profession_page(ana.client_id).mechanic
    assert active.kind == "exporter"
    assert active.status is MechanicStatus.ACTIVE
    assert active.lock is not None and active.lock.share == Decimal("0.5")
    assert active.lock.expires_on == add_months(sim.get_current_date(), 12)
    assert active.lock.dollar_gap == active.lock.locked_dollar - active.dollar
    assert not active.can_change_mix
    assert active.next_mix_change == next_quarter_start(sim.get_current_date())


def test_the_bot_follows_the_mix_policy_and_does_not_lock_without_twelve_samples(
    monkeypatch,
):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.EXPORTER)
    )
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    with_exchange_market(sim, monkeypatch)
    monkeypatch.setattr(sim, "_dollar_change_on", lambda day: Decimal("0.05"))

    turn_of_month(sim)

    state = exporter_state_of(sim, bot)
    # Só o dólar de 12 meses acima do neutro (e o PIB de 3% também): 50/50
    assert state.export_share == Decimal("0.5")
    assert state.lock is None


def test_the_bot_leans_to_the_dollar_when_only_the_dollar_is_above_the_neutral(
    monkeypatch,
):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.EXPORTER)
    )
    sim = match(monkeypatch)
    with_growth(sim, monkeypatch, STAGNANT)
    with_exchange_market(sim, monkeypatch)
    monkeypatch.setattr(sim, "_dollar_change_on", lambda day: Decimal("0.05"))

    turn_of_month(sim)

    assert exporter_state_of(sim, bot).export_share == Decimal("0.7")


def test_the_bot_locks_fifty_percent_for_twelve_months_with_the_dollar_above_the_average(
    monkeypatch,
):
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.EXPORTER)
    )
    sim = match(monkeypatch)
    with_exchange_market(sim, monkeypatch)
    # A série do dólar existe desde antes da partida; os 12 dólares de virada de mês valem R$ 2,00 e o de hoje R$ 2,50
    monkeypatch.setattr(sim, "_dollar_history_start", lambda: date(1990, 1, 1))
    today = sim.get_current_date()
    monkeypatch.setattr(
        sim._engine,
        "dollar_on",
        lambda day: Decimal("2.5") if day >= today else Decimal(2),
    )

    turn_of_month(sim)

    lock = exporter_state_of(sim, bot).lock
    assert lock is not None
    assert (lock.share, lock.months) == (Decimal("0.5"), 12)
