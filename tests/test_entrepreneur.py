"""O reinvestimento do Empreendedor: a divisão do lucro, o rendimento do capital pelo PIB, a venda com desconto, o patrimônio travado, a troca de profissão, a política dos bots e a leitura da página."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.profession import (
    SELL_CAPITAL,
    SET_REINVEST_SHARE,
    CltState,
    EntrepreneurState,
    SellCapital,
    SetReinvestShare,
)
from backend.core.dto.profession_page import EntrepreneurMechanicDTO
from backend.core.entrepreneur import (
    after_payment,
    capital_income,
    capital_rate,
    negative_quarters,
    sale_proceeds,
    split_profit,
)
from backend.core.enum import (
    LifeHistoryKind,
    LockedAssetKind,
    MechanicStatus,
    Profession,
)
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.features.profession.entrepreneur import (
    capital_months_ago,
    pay_month,
    policy_recession_flag,
    policy_reinvest_share,
    policy_sale_due,
    sale_payout,
)
from backend.features.strategy.bots import resolve_bot
from tests.fakes import macro_month
from tests.test_bots import (  # noqa: F401
    person,
    professions_rules,
    refusal,
    room,
    started,
)
from tests.test_clt import turn_of_month, with_growth
from tests.test_profession_mechanics import life_history, match

GROWING = macro_month("0.03")
RECESSION = macro_month("-0.012")
NEUTRAL_GDP = Decimal("0.02")

pytestmark = pytest.mark.usefixtures("room")


def entrepreneur(monkeypatch, **changes):
    """A partida com a Ana Empreendedora; devolve a partida e a jogadora."""
    ana = person("Ana")
    sim = match(monkeypatch, **changes)
    sim.switch_profession(ana, Profession.ENTREPRENEUR)
    return sim, ana


def state_of(sim, user) -> EntrepreneurState:
    state = sim.get_profession_state(user.client_id).state
    assert isinstance(state, EntrepreneurState)
    return state


def save(sim, user, **fields) -> None:
    """Grava o estado da Empreendedora com os campos dados."""
    sim._profession_book.save_state(user.id, EntrepreneurState(**fields))


def page_of(sim, user) -> EntrepreneurMechanicDTO:
    mechanic = sim.get_profession_page(user.client_id).mechanic
    assert isinstance(mechanic, EntrepreneurMechanicDTO)
    return mechanic


def spy_capital_moves(sim, monkeypatch) -> dict[str, list[Decimal]]:
    """Os valores que o pagamento do mês manda para o capital e para o caixa."""
    moves: dict[str, list[Decimal]] = {"reinvested": [], "income": []}
    engine = sim._engine
    reinvest, income = engine.reinvest_profit, engine.pay_capital_income

    def spy_reinvest(client_id, amount):
        moves["reinvested"].append(amount)
        return reinvest(client_id, amount)

    def spy_income(client_id, amount):
        moves["income"].append(amount)
        return income(client_id, amount)

    monkeypatch.setattr(engine, "reinvest_profit", spy_reinvest)
    monkeypatch.setattr(engine, "pay_capital_income", spy_income)
    return moves


def test_the_rate_follows_the_two_lines_through_zero():
    # Com o PIB em 1,4% rende 0,9% ao mês; com o PIB em -1,2% rende -1,4% ao mês
    assert capital_rate(Decimal("0.014")) == Decimal("0.009")
    assert capital_rate(Decimal("-0.012")) == Decimal("-0.014")
    assert capital_rate(Decimal(0)) == 0
    # Cada lado é uma reta: o dobro do PIB dá o dobro da taxa
    assert capital_rate(Decimal("0.028")) == Decimal("0.018")
    assert capital_rate(Decimal("-0.006")) == Decimal("-0.007")


def test_the_income_is_the_rate_on_the_capital_in_cents():
    assert capital_income(Decimal(38000), Decimal("0.014")) == Decimal("342.00")
    assert capital_income(Decimal("36480"), Decimal("-0.012")) == Decimal("-510.72")
    assert capital_income(Decimal(38000), Decimal(0)) == 0


def test_the_profit_splits_between_the_company_and_the_cash():
    reinvested, cash = split_profit(Decimal(7200), Decimal("0.3"))

    assert (reinvested, cash) == (Decimal("2160.00"), Decimal("5040.00"))
    assert split_profit(Decimal(7200), Decimal(0)) == (Decimal(0), Decimal(7200))
    assert split_profit(Decimal(7200), Decimal(1)) == (Decimal(7200), Decimal(0))


def test_a_positive_income_goes_to_the_cash_and_the_capital_keeps_the_reinvested_profit():
    capital, reinvested, income = after_payment(
        Decimal(38000), Decimal("0.014"), Decimal(7200), Decimal("0.3")
    )

    assert income == Decimal("342.00")
    assert reinvested == Decimal("2160.00")
    assert capital == Decimal(38000) + Decimal("2160.00")


def test_a_negative_income_shrinks_the_capital_and_never_below_zero():
    capital, _, income = after_payment(
        Decimal(36480), Decimal("-0.012"), Decimal(7200), Decimal(0)
    )

    assert income == Decimal("-510.72")
    assert capital == Decimal("35969.28")
    # O capital que o rendimento negativo zera fica em zero, sem passar para baixo dele
    capital, _, _ = after_payment(
        Decimal(0), Decimal("-0.5"), Decimal(7200), Decimal(0)
    )
    assert capital == 0
    assert after_payment(Decimal(100), Decimal("-5"), Decimal(0), Decimal(0))[0] == 0


def test_the_payment_moves_a_negative_income_out_of_the_cash_flow():
    state = EntrepreneurState(capital=Decimal(36480))

    paid, reinvested, positive = pay_month(state, Decimal("-0.012"), Decimal(7200))

    assert paid.capital == Decimal("35969.28")
    assert (reinvested, positive) == (0, 0)


def test_the_state_keeps_the_capital_before_each_of_the_last_three_payments():
    state = EntrepreneurState(capital=Decimal(38000))
    assert capital_months_ago(state) is None

    for _ in range(4):
        state, _, _ = pay_month(state, Decimal("-0.012"), Decimal(0))

    assert len(state.capital_history) == 3
    months_ago = capital_months_ago(state)
    assert months_ago == state.capital_history[0]
    assert months_ago is not None
    assert months_ago > state.capital


def test_the_four_sales_pay_eighty_percent_of_the_part_sold():
    state = EntrepreneurState(capital=Decimal(38000))

    assert [
        sale_payout(state, Decimal(share)) for share in ("0.1", "0.25", "0.5", "1")
    ] == [
        Decimal("3040.00"),
        Decimal("7600.00"),
        Decimal("15200.00"),
        Decimal("30400.00"),
    ]
    assert sale_proceeds(Decimal(9500)) == Decimal(7600)


@pytest.mark.parametrize("share", ["0.1", "0.25", "0.5", "1"])
def test_the_sale_takes_the_part_from_the_capital_and_puts_the_proceeds_in_the_cash(
    monkeypatch, share
):
    sim, ana = entrepreneur(monkeypatch)
    save(sim, ana, capital=Decimal(38000))
    cash = sim.get_cash(ana.client_id)

    sim.sell_capital(ana, Decimal(share))

    sold = Decimal(38000) * Decimal(share)
    assert state_of(sim, ana).capital == Decimal(38000) - sold
    assert sim.get_cash(ana.client_id) == cash + sold * Decimal("0.8")
    [row] = [
        r for r in life_history(sim, ana.client_id) if r.life_event_key == SELL_CAPITAL
    ]
    assert row.kind is LifeHistoryKind.PROFESSION_ACTION
    assert row.amount == sold * Decimal("0.8")


def test_the_sale_is_refused_without_capital_out_of_the_options_and_outside_the_profession(
    monkeypatch,
):
    sim, ana = entrepreneur(monkeypatch)

    assert "ainda não tem capital" in refusal(lambda: sim.sell_capital(ana, Decimal(1)))
    save(sim, ana, capital=Decimal(1000))
    for share in ("0.3", "0", "1.5"):
        assert "10%, 25%, 50% ou 100%" in refusal(
            lambda share=share: sim.sell_capital(ana, Decimal(share))
        )
    assert state_of(sim, ana).capital == 1000

    bia = person("Bia")
    assert "Empreendedor" in refusal(lambda: sim.sell_capital(bia, Decimal(1)))
    assert "Empreendedor" in refusal(lambda: sim.set_reinvest_share(bia, Decimal(0)))


def test_the_saved_share_goes_from_zero_to_one_in_steps_of_one_percent(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    assert state_of(sim, ana).reinvest_share == 0

    sim.set_reinvest_share(ana, Decimal("0.37"))
    assert state_of(sim, ana).reinvest_share == Decimal("0.37")
    sim.set_reinvest_share(ana, Decimal(1))
    sim.set_reinvest_share(ana, Decimal(0))
    for share in ("-0.01", "1.01", "0.375"):
        assert "0% a 100%" in refusal(
            lambda share=share: sim.set_reinvest_share(ana, Decimal(share))
        )
    keys = [
        r.life_event_key
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_ACTION
    ]
    assert keys == [SET_REINVEST_SHARE] * 3


def test_the_payment_sends_the_share_of_the_profit_to_the_capital(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    sim.set_reinvest_share(ana, Decimal("0.3"))
    moves = spy_capital_moves(sim, monkeypatch)

    turn_of_month(sim)

    profit = page_of(sim, ana).profit
    assert moves["reinvested"] == [split_profit(profit, Decimal("0.3"))[0]]
    assert state_of(sim, ana).capital == moves["reinvested"][0]


def test_with_zero_percent_the_whole_profit_stays_the_income_of_today(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    moves = spy_capital_moves(sim, monkeypatch)

    turn_of_month(sim)

    assert moves == {"reinvested": [], "income": []}
    assert state_of(sim, ana).capital == 0
    header = sim.get_profession_page(ana.client_id).header
    assert header.income == page_of(sim, ana).profit


def test_the_positive_income_enters_the_cash_and_the_negative_shrinks_the_capital(
    monkeypatch,
):
    sim, ana = entrepreneur(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)
    save(sim, ana, capital=Decimal(38000))
    moves = spy_capital_moves(sim, monkeypatch)

    turn_of_month(sim)

    expected = capital_income(Decimal(38000), Decimal("0.03"))
    assert expected > 0
    assert moves["income"] == [expected]
    assert state_of(sim, ana).capital == 38000

    with_growth(sim, monkeypatch, RECESSION)
    turn_of_month(sim)

    assert moves["income"] == [expected]
    assert state_of(sim, ana).capital == 38000 + capital_income(
        Decimal(38000), Decimal("-0.012")
    )


def test_the_capital_is_a_locked_asset_in_the_networth_and_the_portfolio(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    cash_only = sim.get_portfolio(ana.client_id).total_networth
    save(sim, ana, capital=Decimal(38000))

    portfolio = sim.get_portfolio(ana.client_id)

    [asset] = portfolio.locked_assets
    assert asset.kind is LockedAssetKind.COMPANY_CAPITAL
    assert asset.value == 38000
    assert asset.exit_rule == LOCKED_EXITS[LockedAssetKind.COMPANY_CAPITAL].rule
    assert "20%" in asset.exit_rule
    assert portfolio.locked_value == 38000
    assert portfolio.total_networth == cash_only + 38000
    assert sim._balance_snapshot(ana).total_networth == cash_only + 38000


def test_the_switch_turns_the_whole_capital_into_cash_with_the_discount(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    save(sim, ana, capital=Decimal(38000))
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.WELFARE)

    assert sim.get_cash(ana.client_id) == cash + Decimal(30400)
    assert sim.get_portfolio(ana.client_id).locked_value == 0
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_SWITCHED
        and r.life_event_key == Profession.WELFARE.value
    ]
    assert row.amount == 30400


def test_the_switch_turns_the_whole_fgts_into_cash_without_the_fine(monkeypatch):
    ana = person("Ana")
    sim = match(monkeypatch)
    sim._profession_book.save_state(ana.id, CltState(fgts_balance=Decimal(10000)))
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.WELFARE)

    assert sim.get_cash(ana.client_id) == cash + Decimal(10000)
    assert sim.get_portfolio(ana.client_id).locked_value == 0
    [row] = [
        r
        for r in life_history(sim, ana.client_id)
        if r.kind is LifeHistoryKind.PROFESSION_SWITCHED
    ]
    assert row.amount == 10000


def test_the_exit_rate_lives_with_the_kind_of_the_locked_asset():
    day = date(2020, 1, 1)
    assert LOCKED_EXITS[LockedAssetKind.FGTS].payout(Decimal(100), None, day) == 100
    assert LOCKED_EXITS[LockedAssetKind.COMPANY_CAPITAL].payout(
        Decimal(100), None, day
    ) == Decimal(80)
    assert set(LOCKED_EXITS) == set(LockedAssetKind)


def test_the_switch_without_locked_assets_pays_nothing(monkeypatch):
    sim, ana = entrepreneur(monkeypatch)
    cash = sim.get_cash(ana.client_id)

    sim.switch_profession(ana, Profession.WELFARE)

    assert sim.get_cash(ana.client_id) == cash


def test_the_bot_reinvests_thirty_percent_above_the_neutral_and_nothing_below():
    assert policy_reinvest_share(Decimal("0.03"), NEUTRAL_GDP) == Decimal("0.3")
    assert policy_reinvest_share(NEUTRAL_GDP, NEUTRAL_GDP) == 0
    assert policy_reinvest_share(Decimal("0.01"), NEUTRAL_GDP) == 0


def test_the_recession_counts_the_negative_quarters_back_from_the_latest():
    assert negative_quarters([]) == 0
    assert negative_quarters([Decimal("-0.01"), Decimal("0.01")]) == 0
    assert negative_quarters([Decimal("0.01"), Decimal("-0.01")]) == 1
    assert (
        negative_quarters([Decimal("-0.02"), Decimal("-0.01"), Decimal("-0.03")]) == 3
    )


def test_the_bot_sells_once_per_recession_and_again_only_after_a_new_one():
    capital = EntrepreneurState(capital=Decimal(1000))
    negative, positive = Decimal("-0.01"), Decimal("0.01")

    # Um trimestre negativo não basta; dois seguidos vendem
    assert not policy_sale_due(capital, [positive, negative])
    assert policy_sale_due(capital, [positive, negative, negative])
    # A venda liga a marca, que segura a recessão que continua
    sold = policy_recession_flag(capital, [negative, negative], sold=True)
    assert sold.recession_sold
    assert not policy_sale_due(sold, [negative, negative, negative])
    assert (
        policy_recession_flag(sold, [negative, negative, negative], sold=False) is sold
    )
    # Um trimestre não negativo encerra a recessão e desliga a marca
    ended = policy_recession_flag(sold, [negative, negative, positive], sold=False)
    assert not ended.recession_sold
    assert not policy_sale_due(ended, [negative, negative, positive, negative])
    assert policy_sale_due(ended, [negative, positive, negative, negative])
    # Sem capital não há o que vender
    assert not policy_sale_due(EntrepreneurState(), [negative, negative])


def test_the_bot_reinvests_in_the_growth_and_sells_a_quarter_once_per_recession(
    monkeypatch,
):
    changes = {"end_date": date(2006, 12, 31)}
    monkeypatch.setattr(SettingsManager, "_settings", professions_rules(**changes))
    person("Ana")
    bot = UserManager.add_bot(
        "Robô", resolve_bot("cdi_100", {}, profession=Profession.ENTREPRENEUR)
    )
    sim = match(monkeypatch, **changes)
    with_growth(sim, monkeypatch, GROWING)

    turn_of_month(sim)
    state = state_of(sim, bot)
    assert state.reinvest_share == Decimal("0.3")
    assert state.capital > 0

    with_growth(sim, monkeypatch, RECESSION)
    quarters = {"series": [Decimal("-0.01"), Decimal("-0.02")]}
    monkeypatch.setattr(sim, "_gdp_quarters", lambda day: list(quarters["series"]))
    before = state_of(sim, bot).capital

    turn_of_month(sim)
    after = state_of(sim, bot)
    assert after.reinvest_share == 0
    assert after.recession_sold
    # Vendeu 25% do capital e o rendimento negativo encolheu o resto
    assert after.capital < before * Decimal("0.76")

    turn_of_month(sim)
    assert state_of(sim, bot).capital > after.capital * Decimal("0.98")

    quarters["series"] = [Decimal("-0.01"), Decimal("-0.02"), Decimal("0.01")]
    turn_of_month(sim)
    assert not state_of(sim, bot).recession_sold

    quarters["series"] = [Decimal("0.01"), Decimal("-0.02"), Decimal("-0.03")]
    before = state_of(sim, bot).capital
    turn_of_month(sim)
    assert state_of(sim, bot).capital < before * Decimal("0.76")


def test_the_page_reads_the_block_before_and_after_saving_and_in_the_recession(
    monkeypatch,
):
    sim, ana = entrepreneur(monkeypatch)
    with_growth(sim, monkeypatch, GROWING)

    start = page_of(sim, ana)
    assert start.status is MechanicStatus.AVAILABLE
    assert (start.capital, start.reinvest_share, start.reinvested) == (0, 0, 0)
    assert start.capital_months_ago is None
    assert not start.recession and start.income == 0
    assert start.rate == capital_rate(Decimal("0.03"))
    assert [option.share for option in start.sale_options] == [
        Decimal("0.1"),
        Decimal("0.25"),
        Decimal("0.5"),
        Decimal(1),
    ]
    assert all(option.proceeds == 0 for option in start.sale_options)

    sim.set_reinvest_share(ana, Decimal("0.3"))
    save(sim, ana, capital=Decimal(38000), reinvest_share=Decimal("0.3"))
    saved = page_of(sim, ana)
    assert saved.status is MechanicStatus.ACTIVE
    assert saved.reinvested == split_profit(saved.profit, Decimal("0.3"))[0]
    assert saved.income == capital_income(Decimal(38000), Decimal("0.03"))
    [_, quarter, *_] = saved.sale_options
    assert (quarter.part, quarter.proceeds) == (Decimal("9500.00"), Decimal("7600.00"))

    with_growth(sim, monkeypatch, RECESSION)
    monkeypatch.setattr(
        sim, "_gdp_quarters", lambda day: [Decimal("-0.01"), Decimal("-0.012")]
    )
    shrinking = page_of(sim, ana)
    assert shrinking.recession and shrinking.negative_quarters == 2
    assert shrinking.income == Decimal("-532.00")
    assert shrinking.rate < 0


def test_the_actions_are_in_the_mechanic_actions():
    assert SetReinvestShare(share=Decimal("0.5")).kind == SET_REINVEST_SHARE
    assert SellCapital(share=Decimal(1)).kind == SELL_CAPITAL
