"""A previdência do Aposentado: o saldo inicial, o rendimento, o juro real, a renda vitalícia convertida, o resgate com IR regressivo, o patrimônio travado, a troca de profissão, a política dos bots e a leitura da página."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dates import add_months
from backend.core.dto.profession import (
    CONVERT_PENSION,
    REDEEM_PENSION,
    ConvertPension,
    PensionConversion,
    RedeemPension,
    RetireeState,
)
from backend.core.dto.profession_page import RetireeMechanicDTO
from backend.core.enum import (
    IndicatorSeries,
    LifeHistoryKind,
    LockedAssetKind,
    MechanicStatus,
    Profession,
)
from backend.core.indicators import FOCUS_MAX_AGE
from backend.core.life_budget import LifeBudget
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.pension import (
    REDEEM_BRACKETS,
    annual_yield,
    balance_after_month,
    converted_income,
    income_rate,
    months_in_plan,
    next_bracket,
    opening_balance,
    real_rate,
    redeem_net,
    redeem_rate,
    redeem_tax,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.pension import (
    apply_retiree,
    converted_amount,
    converted_real_rate,
    open_balance,
    pay_month,
    policy_convert_amount,
    policy_redeem_amount,
)
from backend.features.simulation import simulation as simulation_module
from backend.features.strategy.bots import resolve_bot
from tests.fakes import macro_month
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_clt import turn_of_month
from tests.test_profession_mechanics import life_history, match

GROWING = macro_month("0.03")
DAY = date(2020, 3, 2)
# Os números do exemplo do quadro: SELIC de 13,76% e IPCA esperado de 5,2% ao ano
SELIC = Decimal("0.1376")
EXPECTED_IPCA = Decimal("0.052")
BOARD_RATE = real_rate(SELIC, EXPECTED_IPCA)
CDI = Decimal("0.1365")

pytestmark = pytest.mark.usefixtures("room")


def retiree(monkeypatch, **changes):
    """A partida com a Ana Aposentada; devolve a partida e a jogadora."""
    ana = person("Ana")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.RETIREE)
    return sim, ana


def state_of(sim, user) -> RetireeState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, RetireeState)
    return state


def retiree_budget(sim) -> LifeBudget:
    budget = sim._life.for_profession(Profession.RETIREE)
    assert budget is not None
    return budget


def save(sim, user, **fields) -> None:
    """Grava o estado da Aposentada com os campos dados."""
    sim._profession_book.save_state(user.id, RetireeState(**fields))


def page_of(sim, user) -> RetireeMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, RetireeMechanicDTO)
    return mechanic


def with_rates(sim, monkeypatch, real: Decimal = BOARD_RATE) -> None:
    """O juro real do dia que a partida lê: o dado."""
    monkeypatch.setattr(
        sim, "_pension_real_rate", lambda day: (real, EXPECTED_IPCA, True)
    )


def with_cdi(monkeypatch, cdi: Decimal = CDI) -> None:
    """O CDI que o pagamento do mês lê; as demais séries seguem as da partida."""
    real = simulation_module.annual_index_rate
    monkeypatch.setattr(
        simulation_module,
        "annual_index_rate",
        lambda series, day: cdi if series is IndicatorSeries.CDI else real(series, day),
    )


def test_the_opening_balance_is_twenty_four_incomes_of_the_month():
    assert opening_balance(Decimal("5000.50")) == Decimal("120012.00")
    assert opening_balance(Decimal(0)) == 0


def test_the_plan_yields_the_cdi_minus_one_percent_a_year_each_month():
    assert annual_yield(CDI) == Decimal("0.1265")
    paid = balance_after_month(Decimal(10000), CDI)
    # 10.000 x 1,1265 elevado a 1/12: cerca de 1% ao mês
    assert Decimal("10099") < paid < Decimal("10101")
    # Doze meses fecham a taxa anual do plano
    balance = Decimal(10000)
    for _ in range(12):
        balance = balance_after_month(balance, CDI)
    assert abs(balance - Decimal(11265)) < Decimal("0.5")


def test_the_real_rate_is_the_selic_over_the_expected_ipca():
    assert real_rate(SELIC, EXPECTED_IPCA) == (1 + SELIC) / (1 + EXPECTED_IPCA) - 1
    assert round(real_rate(SELIC, EXPECTED_IPCA), 4) == Decimal("0.0814")
    assert real_rate(Decimal("0.05"), Decimal("0.05")) == 0
    assert real_rate(Decimal("0.04"), Decimal("0.06")) < 0


def test_the_converted_income_matches_the_two_examples_of_the_board():
    assert converted_income(Decimal(20000), BOARD_RATE) == Decimal("130.81")
    assert converted_income(Decimal(40000), Decimal("0.068")) == Decimal("219.89")
    assert income_rate(Decimal(0)) == 0


@pytest.mark.parametrize(
    ("months", "rate"),
    [
        (0, "0.35"),
        (23, "0.35"),
        (24, "0.30"),
        (47, "0.30"),
        (48, "0.25"),
        (71, "0.25"),
        (72, "0.20"),
        (95, "0.20"),
        (96, "0.15"),
        (119, "0.15"),
        (120, "0.10"),
        (400, "0.10"),
    ],
)
def test_the_redeem_table_has_six_brackets_with_the_edges_in_the_new_one(months, rate):
    assert redeem_rate(months) == Decimal(rate)
    assert len(REDEEM_BRACKETS) == 6


def test_the_redeem_tax_is_on_the_whole_amount_and_the_next_bracket_comes_from_the_table():
    assert redeem_tax(Decimal(20000), 40) == Decimal("6000.00")
    assert redeem_net(Decimal(20000), 40) == Decimal("14000.00")
    later = next_bracket(40)
    assert later is not None
    assert (later.from_months, later.rate) == (48, Decimal("0.25"))
    assert next_bracket(120) is None


def test_the_months_in_the_plan_are_complete_months():
    assert months_in_plan(date(2020, 1, 31), date(2020, 3, 1)) == 1
    assert months_in_plan(date(2020, 1, 15), date(2020, 3, 14)) == 1
    assert months_in_plan(date(2020, 1, 15), date(2020, 3, 15)) == 2
    assert months_in_plan(date(2020, 1, 15), date(2019, 1, 1)) == 0


def test_the_state_opens_the_balance_once_and_keeps_the_day():
    opened = open_balance(RetireeState(), Decimal(5000), DAY)

    assert (opened.balance, opened.since) == (Decimal(120000), DAY)
    assert open_balance(opened, Decimal(9000), date(2021, 1, 4)) is opened


def test_the_conversion_takes_the_amount_out_of_the_balance_and_keeps_the_part():
    state = RetireeState(balance=Decimal(50000), since=DAY)

    converted = apply_retiree(
        state,
        ConvertPension(amount=Decimal(20000), real_rate=BOARD_RATE),
        DAY,
        GROWING,
    )

    assert converted.balance == Decimal(30000)
    [part] = converted.conversions
    assert (part.converted_on, part.amount, part.income) == (
        DAY,
        Decimal(20000),
        Decimal("130.81"),
    )
    assert part.real_rate == BOARD_RATE


def test_the_real_rate_of_the_conversions_is_the_average_weighted_by_the_amount():
    state = RetireeState(
        balance=Decimal(0),
        conversions=[
            PensionConversion(
                converted_on=DAY,
                amount=Decimal(20000),
                real_rate=Decimal("0.08"),
                income=Decimal(0),
            ),
            PensionConversion(
                converted_on=DAY,
                amount=Decimal(40000),
                real_rate=Decimal("0.068"),
                income=Decimal(0),
            ),
        ],
    )

    assert converted_amount(state) == 60000
    assert converted_real_rate(state) == Decimal("0.072")
    assert converted_real_rate(RetireeState()) is None


def test_the_balance_that_never_opened_is_not_paid():
    assert pay_month(RetireeState(), CDI).balance is None
    paid = pay_month(RetireeState(balance=Decimal(10000), since=DAY), CDI)
    assert paid.balance == balance_after_month(Decimal(10000), CDI)


def test_the_exit_of_the_pension_pays_the_regressive_tax_by_the_time_in_the_plan():
    exit_ = LOCKED_EXITS[LockedAssetKind.PENSION]

    assert "IR regressivo" in exit_.rule
    since = date(2016, 1, 4)
    # Quatro anos e dois meses no plano: 25% de IR
    assert exit_.payout(Decimal(10000), since, date(2020, 3, 2)) == Decimal("7500.00")
    # Sem a data de entrada no plano vale a faixa mais alta
    assert exit_.payout(Decimal(10000), None, date(2020, 3, 2)) == Decimal("6500.00")


def test_the_balance_opens_in_twenty_four_incomes_on_the_first_read_without_touching_the_cash(
    monkeypatch,
):
    ana = person("Ana")
    sim = match(monkeypatch)

    sim.switch_profession(ana, Profession.RETIREE)
    cash = sim.get_cash(ana.client_id)
    state = state_of(sim, ana)

    income = retiree_budget(sim).net_salary_on(sim.get_current_date())
    assert state.balance == opening_balance(income)
    assert state.since == sim.get_current_date()
    assert sim.get_cash(ana.client_id) == cash


def test_a_saved_match_opens_the_balance_on_the_first_read_from_that_date(monkeypatch):
    sim, ana = retiree(monkeypatch)
    save(sim, ana)
    saved = sim._profession_book.state_of(ana.id, Profession.RETIREE)
    assert isinstance(saved, RetireeState)
    assert saved.balance is None

    turn_of_month(sim)
    turn_of_month(sim)
    state = state_of(sim, ana)

    assert state.balance is not None and state.balance > 0
    assert state.since is not None
    # Outra leitura não abre de novo: o tempo no plano conta da primeira
    sim.get_profession_page(ana.client_id)
    assert state_of(sim, ana).since == state.since


def test_the_pension_enters_the_networth_and_the_portfolio_as_a_locked_asset(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(60000), since=sim.get_current_date())
    cash = sim.get_cash(ana.client_id)

    portfolio = sim.get_portfolio(ana.client_id)

    [asset] = portfolio.locked_assets
    assert asset.kind is LockedAssetKind.PENSION
    assert asset.value == 60000
    assert asset.since == sim.get_current_date()
    assert "IR regressivo" in asset.exit_rule
    assert portfolio.locked_value == 60000
    assert portfolio.total_networth == cash + 60000
    assert sim._balance_snapshot(ana).total_networth == cash + 60000


def test_the_month_pays_the_plan_yield_on_the_balance(monkeypatch):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(60000), since=sim.get_current_date())
    with_cdi(monkeypatch)

    turn_of_month(sim)

    assert state_of(sim, ana).balance == balance_after_month(Decimal(60000), CDI)


def test_the_real_rate_uses_the_focus_ipca_when_it_has_at_most_thirty_days(
    monkeypatch,
):
    sim, _ = retiree(monkeypatch)
    monkeypatch.setattr(sim, "_selic_on", lambda day: SELIC)
    monkeypatch.setattr(
        simulation_module, "recent_focus_rate", lambda series, day: EXPECTED_IPCA
    )

    rate, expected, from_focus = sim._pension_real_rate(sim.get_current_date())

    assert (expected, from_focus) == (EXPECTED_IPCA, True)
    assert rate == BOARD_RATE
    assert FOCUS_MAX_AGE.days == 30


def test_the_real_rate_falls_back_to_the_realized_ipca_without_a_recent_focus(
    monkeypatch,
):
    sim, _ = retiree(monkeypatch)
    monkeypatch.setattr(sim, "_selic_on", lambda day: SELIC)
    monkeypatch.setattr(simulation_module, "recent_focus_rate", lambda s, d: None)
    realized = Decimal("0.0431")
    real = simulation_module.annual_index_rate
    monkeypatch.setattr(
        simulation_module,
        "annual_index_rate",
        lambda series, day: (
            realized if series is IndicatorSeries.IPCA else real(series, day)
        ),
    )

    rate, expected, from_focus = sim._pension_real_rate(sim.get_current_date())

    assert (expected, from_focus) == (realized, False)
    assert rate == real_rate(SELIC, realized)


def test_the_conversion_makes_a_lifelong_income_without_tax_and_leaves_the_cash(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(50000), since=sim.get_current_date())
    with_rates(sim, monkeypatch)
    cash = sim.get_cash(ana.client_id)
    before = sim.get_profession_page(ana.client_id).header.income

    sim.convert_pension(ana, Decimal(20000))

    state = state_of(sim, ana)
    assert state.balance == 30000
    [part] = state.conversions
    assert part.income == Decimal("130.81")
    assert sim.get_cash(ana.client_id) == cash
    header = sim.get_profession_page(ana.client_id).header
    # A renda convertida soma inteira à renda do mês, sem desvio de imposto, e sai do patrimônio como saldo
    assert header.income == before + Decimal("130.81")
    assert header.mechanic_income == Decimal("130.81")
    assert sim.get_portfolio(ana.client_id).locked_value == 30000
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.life_event_key == CONVERT_PENSION
    ]
    assert row.kind is LifeHistoryKind.PROFESSION_ACTION
    assert not row.amount


def test_the_converted_income_stays_fixed_in_a_room_without_correction(monkeypatch):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(50000), since=sim.get_current_date())
    with_rates(sim, monkeypatch)
    sim.convert_pension(ana, Decimal(20000))
    budget = retiree_budget(sim).with_mechanic_state(lambda: state_of(sim, ana))

    assert budget.converted_income_on(sim.get_current_date()) == Decimal("130.81")
    assert budget.converted_income_on(date(2023, 6, 1)) == Decimal("130.81")


def test_the_converted_income_follows_the_ipca_only_in_a_room_with_correction(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch, inflation_adjusted=True)
    save(sim, ana, balance=Decimal(50000), since=sim.get_current_date())
    with_rates(sim, monkeypatch)
    converted_on = sim.get_current_date()
    sim.convert_pension(ana, Decimal(20000))
    budget = retiree_budget(sim).with_mechanic_state(lambda: state_of(sim, ana))
    later = add_months(converted_on, 12)

    assert budget.converted_income_on(converted_on) == Decimal("130.81")
    assert budget.converted_income_on(later) > Decimal("130.81")
    assert page_of(sim, ana).inflation_indexed


def test_the_conversion_is_refused_outside_the_range_with_a_zero_real_rate_and_outside_the_profession(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(1000), since=sim.get_current_date())
    with_rates(sim, monkeypatch)

    for amount in ("0", "-5", "1000.01", "10.005"):
        assert "R$ 0,01 até o saldo" in refusal(
            lambda amount=amount: sim.convert_pension(ana, Decimal(amount))
        )
    sim.convert_pension(ana, Decimal("0.01"))
    assert state_of(sim, ana).balance == Decimal("999.99")

    with_rates(sim, monkeypatch, real=Decimal(0))
    assert "juro real" in refusal(lambda: sim.convert_pension(ana, Decimal(10)))
    with_rates(sim, monkeypatch, real=Decimal("-0.01"))
    assert "juro real" in refusal(lambda: sim.convert_pension(ana, Decimal(10)))
    assert state_of(sim, ana).balance == Decimal("999.99")

    bia = person("Bia")
    assert "Aposentado" in refusal(lambda: sim.convert_pension(bia, Decimal(1)))
    assert "Aposentado" in refusal(lambda: sim.redeem_pension(bia, Decimal(1)))


def test_the_redeem_pays_the_tax_on_the_whole_amount_and_the_net_goes_to_the_cash(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    # Três anos e quatro meses no plano: IR de 30%
    since = add_months(sim.get_current_date(), -40)
    save(sim, ana, balance=Decimal(50000), since=since)
    cash = sim.get_cash(ana.client_id)

    sim.redeem_pension(ana, Decimal(20000))

    assert state_of(sim, ana).balance == 30000
    assert sim.get_cash(ana.client_id) == cash + Decimal("14000.00")
    assert sim.get_portfolio(ana.client_id).locked_value == 30000
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.life_event_key == REDEEM_PENSION
    ]
    assert row.kind is LifeHistoryKind.PROFESSION_ACTION
    assert row.amount == Decimal("14000.00")


def test_the_redeem_is_refused_outside_the_range(monkeypatch):
    sim, ana = retiree(monkeypatch)
    save(sim, ana, balance=Decimal(1000), since=sim.get_current_date())
    cash = sim.get_cash(ana.client_id)

    for amount in ("0", "-1", "1000.01", "5.001"):
        assert "R$ 0,01 até o saldo" in refusal(
            lambda amount=amount: sim.redeem_pension(ana, Decimal(amount))
        )

    assert state_of(sim, ana).balance == 1000
    assert sim.get_cash(ana.client_id) == cash


def test_the_switch_turns_the_balance_into_cash_with_the_tax_of_the_day_and_ends_the_income(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    since = add_months(sim.get_current_date(), -50)
    save(sim, ana, balance=Decimal(40000), since=since)
    with_rates(sim, monkeypatch)
    sim.convert_pension(ana, Decimal(10000))
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.WELFARE)

    # Quatro anos e dois meses no plano: IR de 25% sobre o que restou no saldo
    assert sim.get_cash(ana.client_id) == cash + Decimal("22500.00")
    assert sim.get_portfolio(ana.client_id).locked_value == 0
    assert sim.get_profession_page(ana.client_id).header.mechanic_income == 0
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_SWITCHED
        and r.life_event_key == Profession.WELFARE.value
    ]
    assert row.amount == Decimal("22500.00")


def test_the_bot_policy_converts_half_once_and_redeems_all_after_ten_years():
    state = RetireeState(balance=Decimal(60000), since=DAY)

    assert policy_convert_amount(state, Decimal("0.06")) is None
    assert policy_convert_amount(state, Decimal("0.0601")) == Decimal("30000.00")
    converted = apply_retiree(
        state, ConvertPension(amount=Decimal(30000), real_rate=BOARD_RATE), DAY, GROWING
    )
    assert isinstance(converted, RetireeState)
    assert policy_convert_amount(converted, Decimal("0.09")) is None
    assert policy_convert_amount(RetireeState(), Decimal("0.09")) is None

    assert policy_redeem_amount(state, add_months(DAY, 119)) is None
    assert policy_redeem_amount(state, add_months(DAY, 120)) == 60000
    assert policy_redeem_amount(RetireeState(), DAY) is None
    assert (
        policy_redeem_amount(
            state.model_copy(update={"balance": Decimal(0)}), add_months(DAY, 130)
        )
        is None
    )


def test_the_bot_converts_half_in_the_first_good_month_and_never_again(monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", professions_rules(end_date=date(2006, 12, 31))
    )
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.RETIREE)
    )
    sim = match(monkeypatch, end_date=date(2006, 12, 31))
    with_rates(sim, monkeypatch, real=Decimal("0.03"))
    with_cdi(monkeypatch)

    turn_of_month(sim)
    assert not state_of(sim, bot).conversions

    with_rates(sim, monkeypatch, real=Decimal("0.07"))
    turn_of_month(sim)
    state = state_of(sim, bot)
    [part] = state.conversions
    assert part.real_rate == Decimal("0.07")
    # Converteu a metade do saldo: o que sobrou, já rendido no mês, é do tamanho do valor convertido
    assert state.balance is not None
    assert Decimal("0.99") < state.balance / part.amount < Decimal("1.03")

    turn_of_month(sim)
    assert len(state_of(sim, bot).conversions) == 1


def test_the_bot_redeems_the_whole_balance_after_ten_years_in_the_plan(monkeypatch):
    monkeypatch.setattr(
        SettingsManager, "_settings", professions_rules(end_date=date(2006, 12, 31))
    )
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.RETIREE)
    )
    sim = match(monkeypatch, end_date=date(2006, 12, 31))
    with_rates(sim, monkeypatch, real=Decimal("0.03"))
    since = add_months(sim.get_current_date(), -125)
    save(sim, bot, balance=Decimal(80000), since=since)

    turn_of_month(sim)

    assert state_of(sim, bot).balance == 0
    [row] = [
        r
        for r in life_history(sim, bot.client_id)
        if r.life_event_key == REDEEM_PENSION
    ]
    assert row.amount == redeem_net(Decimal(80000), 125)


def test_the_page_reads_the_block_with_the_table_the_next_bracket_and_the_conversions(
    monkeypatch,
):
    sim, ana = retiree(monkeypatch)
    since = add_months(sim.get_current_date(), -40)
    save(sim, ana, balance=Decimal(50000), since=since)
    with_rates(sim, monkeypatch)
    with_cdi(monkeypatch)

    start = page_of(sim, ana)
    assert start.status is MechanicStatus.AVAILABLE
    assert start.balance == 50000
    assert (start.annual_rate, start.cdi) == (Decimal("0.1265"), CDI)
    assert start.converted_income == 0 and start.converted_amount == 0
    assert start.converted_real_rate is None
    assert (start.months_in_plan, start.redeem_rate) == (40, Decimal("0.30"))
    assert (start.next_rate, start.next_rate_months) == (Decimal("0.25"), 8)
    assert start.next_rate_on == add_months(sim.get_current_date(), 8)
    assert [(b.label, b.rate, b.current) for b in start.brackets] == [
        (b.label, b.rate, b.from_months == 24) for b in REDEEM_BRACKETS
    ]
    assert start.real_rate == BOARD_RATE and start.expected_ipca_from_focus
    assert start.income_rate == income_rate(BOARD_RATE)
    assert not start.inflation_indexed

    sim.convert_pension(ana, Decimal(20000))
    converted = page_of(sim, ana)
    assert converted.status is MechanicStatus.ACTIVE
    assert converted.balance == 30000
    assert converted.converted_income == Decimal("130.81")
    assert converted.converted_amount == 20000
    assert converted.converted_real_rate == BOARD_RATE


def test_the_page_reads_the_last_bracket_without_a_next_one(monkeypatch):
    sim, ana = retiree(monkeypatch)
    save(
        sim,
        ana,
        balance=Decimal(1000),
        since=add_months(sim.get_current_date(), -130),
    )
    with_rates(sim, monkeypatch)

    page = page_of(sim, ana)

    assert page.redeem_rate == Decimal("0.10")
    assert (page.next_rate, page.next_rate_months, page.next_rate_on) == (
        None,
        None,
        None,
    )


def test_the_actions_are_in_the_mechanic_actions():
    assert ConvertPension(amount=Decimal(1), real_rate=Decimal("0.05")).kind == (
        CONVERT_PENSION
    )
    assert RedeemPension(amount=Decimal(1)).kind == REDEEM_PENSION
