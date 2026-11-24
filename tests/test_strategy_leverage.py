"""Alavancagem das estratégias: contexto de crédito, política comum, parâmetro booleano e estratégias mistas."""

from __future__ import annotations

import uuid
from decimal import Decimal

from backend.core.enum import CreditGrade, PrepaymentMode, StrategyAction
from backend.core.utils import required
from backend.features.strategy import leverage
from backend.features.strategy.base_strategy import LEVERAGE_KEY, TARGET_DEBT_KEY
from backend.features.strategy.buy_and_hold import BuyAndHold
from backend.features.strategy.context import FixedHolding, Holding
from backend.features.strategy.rebalance import TargetRebalance
from backend.features.strategy.registry import STRATEGIES
from tests.strategy_helpers import closes, context, credit_offer, loan, offer

ON = {LEVERAGE_KEY: True, TARGET_DEBT_KEY: 20}
OFF = {LEVERAGE_KEY: False, TARGET_DEBT_KEY: 20}
SUPPORTING = {
    "buy_and_hold",
    "target_rebalance",
    "moving_average_cross",
    "rsi",
    "volume_breakout",
    "momentum_12m",
    "state_companies",
    "fund_quotas",
}


def plan(uptrend: bool, params=ON, **kwargs):
    # Sem caixa, salvo o que o teste pede: o caixa parado muda o que a política faz
    kwargs.setdefault("cash", "0")
    ctx = context(history={"AAA": closes([100.0])}, **kwargs)
    leverage.plan(ctx, params, uptrend)
    return ctx


def actions(ctx) -> list[StrategyAction]:
    return [intent.action for intent in ctx.intents]


# ---------------------------------------------------------------- contexto


def test_the_context_carries_debt_grade_offer_and_loans():
    open_loan = loan(2, "8000", rate="0.18")
    ctx = context(
        debt="8000",
        grade=CreditGrade.AA,
        loans=[open_loan],
        credit_offer=credit_offer("5000"),
        networth="92000",
    )

    assert ctx.debt == Decimal(8000)
    assert ctx.grade is CreditGrade.AA
    assert [(x.number, x.balance, x.annual_rate) for x in ctx.loans] == [
        (2, Decimal(8000), Decimal("0.18"))
    ]
    assert required(ctx.offer).max_amount == Decimal(5000)
    assert ctx.networth == Decimal(92000)


def test_the_context_without_credit_has_no_offer_and_no_debt():
    ctx = context()

    assert ctx.debt == 0
    assert ctx.loans == []
    assert ctx.offer is None


def test_the_credit_actions_only_queue_intents_with_the_reason():
    open_loan = loan()
    ctx = context(loans=[open_loan])

    ctx.take_loan(Decimal(5000), 24, "Precisava de caixa")
    ctx.prepay_loan(open_loan.id, Decimal(1000), "Sobrou caixa")
    ctx.payoff_loan(open_loan.id, "Quitou tudo")
    ctx.pay_overdue(open_loan.id, "Pagou o atraso")

    take, prepay, payoff, overdue = ctx.intents
    assert actions(ctx) == [
        StrategyAction.TAKE_LOAN,
        StrategyAction.PREPAY_LOAN,
        StrategyAction.PAYOFF_LOAN,
        StrategyAction.PAY_OVERDUE,
    ]
    assert (take.value, take.term_months) == (Decimal(5000), 24)
    # A tela amortiza encurtando o prazo, e o contexto herda esse padrão
    assert prepay.mode is PrepaymentMode.SHORTEN_TERM
    assert {i.asset_uuid for i in (prepay, payoff, overdue)} == {open_loan.id}
    assert [i.reason for i in ctx.intents] == [
        "Precisava de caixa",
        "Sobrou caixa",
        "Quitou tudo",
        "Pagou o atraso",
    ]


# ---------------------------------------------------------------- tendência


def test_the_trend_needs_200_sessions_and_a_level_above_their_average():
    rising = [Decimal(100 + i) for i in range(200)]
    falling = list(reversed(rising))

    assert leverage.is_uptrend(rising)
    assert not leverage.is_uptrend(falling)
    assert not leverage.is_uptrend(rising[-199:])


# ---------------------------------------------------------------- política


def test_it_borrows_up_to_the_target_debt_when_the_index_is_above_its_average():
    ctx = plan(True, networth="100000", credit_offer=credit_offer())

    [take] = ctx.intents
    assert take.action is StrategyAction.TAKE_LOAN
    # 20% de R$ 100.000, no prazo fixo mais longo
    assert (take.value, take.term_months) == (Decimal("20000.00"), 60)
    assert "Ibovespa acima da média" in take.reason


def test_it_does_not_borrow_when_the_index_is_below_its_average():
    ctx = plan(False, networth="100000", credit_offer=credit_offer())

    assert ctx.intents == []


def test_the_rating_ceiling_and_the_offer_cap_what_it_borrows():
    ctx = plan(True, networth="100000", credit_offer=credit_offer(max_amount="6000"))

    [take] = ctx.intents
    assert take.value == Decimal("6000.00")


def test_it_does_not_borrow_without_an_offer():
    blocked = credit_offer(max_amount="0", rate=None, available=False)

    assert plan(True, networth="100000", credit_offer=blocked).intents == []
    assert plan(True, networth="100000").intents == []


def test_the_tolerance_band_keeps_a_small_gap_from_borrowing_again():
    # Dívida de R$ 17.000 contra a meta de R$ 20.000: falta 15%, dentro da banda de 20%
    ctx = plan(
        True,
        networth="50000",
        debt="17000",
        loans=[loan(balance="17000", age_days=5)],
        credit_offer=credit_offer(),
    )

    assert ctx.intents == []


def test_idle_cash_already_covering_the_gap_is_not_borrowed_against():
    ctx = plan(True, cash="20000", networth="100000", credit_offer=credit_offer())

    assert ctx.intents == []


def test_it_sells_in_proportion_and_pays_off_when_the_index_falls():
    holdings = {
        "AAA": Holding("AAA", Decimal(1000), Decimal(0), Decimal(100)),
        "BBB": Holding("BBB", Decimal(1000), Decimal(0), Decimal(100)),
    }
    ctx = context(
        cash="0",
        history={"AAA": closes([100.0]), "BBB": closes([100.0])},
        holdings=holdings,
        debt="20000",
        loans=[loan(balance="20000")],
    )

    leverage.plan(ctx, ON, False)

    sells = [i for i in ctx.intents if i.action is StrategyAction.SELL]
    [payoff] = [i for i in ctx.intents if i.action is StrategyAction.PAYOFF_LOAN]
    # Cobre a dívida com a margem e vende o mesmo tanto de cada ação
    assert {s.ticker: s.quantity for s in sells} == {"AAA": 101, "BBB": 101}
    assert ctx.intents[-1] is payoff
    assert "abaixo da média" in payoff.reason


def test_selling_everything_that_covers_the_balance_pays_the_loan_off():
    ctx = plan(
        False,
        holdings={"AAA": Holding("AAA", Decimal(200), Decimal(0), Decimal(100))},
        debt="20000",
        loans=[loan(balance="20000")],
    )

    assert actions(ctx) == [StrategyAction.SELL, StrategyAction.PAYOFF_LOAN]


def test_a_loan_in_arrears_that_the_sale_cannot_pay_off_gets_its_overdue_paid():
    late = loan(balance="10000", overdue="800")
    ctx = plan(False, cash="1000", debt="10000", loans=[late])

    [payment] = ctx.intents
    assert payment.action is StrategyAction.PAY_OVERDUE
    assert payment.asset_uuid == late.id


def test_it_pays_off_with_the_cash_before_selling_anything():
    ctx = plan(
        False,
        cash="25000",
        holdings={"AAA": Holding("AAA", Decimal(1000), Decimal(0), Decimal(100))},
        debt="20000",
        loans=[loan(balance="20000")],
    )

    assert actions(ctx) == [StrategyAction.PAYOFF_LOAN]


def test_idle_cash_prepays_the_most_expensive_loan_first():
    cheap, dear = loan(1, "10000", rate="0.12"), loan(2, "10000", rate="0.18")
    ctx = plan(
        True,
        cash="3000",
        networth="50000",
        debt="20000",
        loans=[cheap, dear],
        credit_offer=credit_offer(),
    )

    [prepay] = ctx.intents
    assert prepay.action is StrategyAction.PREPAY_LOAN
    assert (prepay.asset_uuid, prepay.value) == (dear.id, Decimal("3000.00"))


def test_idle_cash_that_covers_the_balance_pays_the_loan_off():
    ctx = plan(
        True,
        cash="12000",
        networth="50000",
        debt="10000",
        loans=[loan(balance="10000")],
        credit_offer=credit_offer(),
    )

    assert actions(ctx) == [StrategyAction.PAYOFF_LOAN]


def test_a_new_loan_is_not_prepaid_with_the_cash_it_just_brought():
    ctx = plan(
        True,
        cash="3000",
        networth="50000",
        debt="10000",
        loans=[loan(balance="10000", age_days=3)],
        credit_offer=credit_offer(),
    )

    assert ctx.intents == []


def test_it_pays_the_overdue_installments_when_there_is_cash():
    late = loan(balance="10000", overdue="800")
    ctx = plan(
        True,
        cash="1000",
        networth="50000",
        debt="10000",
        loans=[late],
        credit_offer=credit_offer(),
    )

    [payment] = ctx.intents
    assert payment.action is StrategyAction.PAY_OVERDUE
    assert payment.asset_uuid == late.id


def test_it_leaves_the_overdue_alone_without_cash_for_it():
    ctx = plan(
        True,
        cash="100",
        networth="50000",
        debt="10000",
        loans=[loan(balance="10000", overdue="800")],
        credit_offer=credit_offer(),
    )

    assert ctx.intents == []


def sells_of(ctx) -> dict[str, Decimal]:
    return {
        i.ticker: required(i.quantity)
        for i in ctx.intents
        if i.action is StrategyAction.SELL
    }


AAA_1000 = {"AAA": Holding("AAA", Decimal(1000), Decimal(0), Decimal(100))}


def test_in_an_uptrend_it_sells_only_the_gap_between_the_installments_and_the_account_cash():
    ctx = plan(
        True,
        holdings=AAA_1000,
        installments_due="3000",
        gross_cash="2000",
        networth="50000",
        debt="10000",
        loans=[loan(balance="10000")],
        credit_offer=credit_offer(),
    )

    # Faltam 1.000 para as parcelas, e 1.010 com a margem da venda: 11 ações a 100
    assert sells_of(ctx) == {"AAA": 11}
    [sell] = ctx.intents
    assert "Caixa abaixo das parcelas dos próximos 30 dias" in sell.reason


def test_in_an_uptrend_it_does_not_sell_when_the_account_cash_covers_the_installments():
    ctx = plan(
        True,
        holdings=AAA_1000,
        installments_due="3000",
        gross_cash="3000",
        networth="50000",
        debt="10000",
        loans=[loan(balance="10000")],
        credit_offer=credit_offer(),
    )

    assert sells_of(ctx) == {}


def test_in_an_uptrend_the_overdue_with_no_cash_makes_it_sell_and_pays_it_the_same_day():
    late = loan(balance="10000", overdue="800")
    ctx = plan(
        True,
        holdings=AAA_1000,
        installments_due="300",
        gross_cash="300",
        networth="50000",
        debt="10000",
        loans=[late],
        credit_offer=credit_offer(),
    )

    # Falta o atraso de 800 (o caixa de 300 cobre as parcelas): vende 9 ações a 100, que rendem
    # mais que 800 mesmo com a margem, e a venda vem antes do pagamento na fila
    assert sells_of(ctx) == {"AAA": 9}
    assert actions(ctx) == [StrategyAction.SELL, StrategyAction.PAY_OVERDUE]
    assert ctx.intents[1].asset_uuid == late.id


def test_in_an_uptrend_the_overdue_paid_by_the_cash_does_not_count_in_the_gap():
    late = loan(balance="10000", overdue="800")
    ctx = plan(
        True,
        cash="1000",
        holdings=AAA_1000,
        installments_due="300",
        gross_cash="1300",
        networth="50000",
        debt="10000",
        loans=[late],
        credit_offer=credit_offer(),
    )

    # O caixa de 1.000 paga o atraso de 800 e os 500 restantes da conta cobrem as parcelas de 300
    assert actions(ctx) == [StrategyAction.PAY_OVERDUE]


# ---------------------------------------------------------------- parâmetro


def test_the_boolean_param_must_be_on_or_off():
    errors = BuyAndHold.validate(
        {"asset": "AAA", "cash_pct": 20, LEVERAGE_KEY: "sim", TARGET_DEBT_KEY: 20},
        {"AAA"},
    )

    assert errors == {LEVERAGE_KEY: "Alavancar precisa ser ligado ou desligado."}


def test_the_target_debt_keeps_its_range():
    errors = BuyAndHold.validate(
        {"asset": "AAA", "cash_pct": 20, LEVERAGE_KEY: True, TARGET_DEBT_KEY: 80},
        {"AAA"},
    )

    assert list(errors) == [TARGET_DEBT_KEY]


def test_leverage_is_off_by_default_with_a_target_of_20_percent():
    by_key = {spec.key: spec for spec in BuyAndHold.params}

    assert by_key[LEVERAGE_KEY].default is False
    assert by_key[TARGET_DEBT_KEY].default == 20
    assert by_key[TARGET_DEBT_KEY].enabled_by == LEVERAGE_KEY


def test_only_the_supporting_strategies_get_the_leverage_params():
    supporting = {key for key, cls in STRATEGIES.items() if cls.supports_leverage}

    assert supporting == SUPPORTING
    for key, cls in STRATEGIES.items():
        keys = [spec.key for spec in cls.params]
        assert (LEVERAGE_KEY in keys) == (key in SUPPORTING)
        if key in SUPPORTING:
            assert keys[-2:] == [LEVERAGE_KEY, TARGET_DEBT_KEY]


def test_a_saved_strategy_without_the_key_is_not_leveraged():
    ctx = context(debt="20000")

    assert leverage.financed_debt(ctx, {}) == 0
    assert leverage.financed_debt(ctx, OFF) == 0
    assert leverage.financed_debt(ctx, ON) == Decimal(20000)


# ---------------------------------------------------------------- mistas


def test_the_debt_goes_entirely_to_the_risk_side_of_a_mixed_strategy():
    liquid = offer(daily_liquidity=True, name="CDB Liquidez Diária")
    params = {"asset": "AAA", "stock_target": 60, "max_deviation": 5}

    def run(extra):
        # Patrimônio de R$ 100.000 mais R$ 20.000 emprestados, tudo em caixa
        ctx = context(
            cash="120000",
            history={"AAA": closes([100.0])},
            offers=[liquid],
            debt="20000",
        )
        TargetRebalance().next(ctx, {**params, **extra})
        buy, invest = ctx.intents
        return buy.quantity, invest.value

    # 60% do patrimônio próprio (60.000) mais toda a dívida (20.000) em ações
    assert run(ON) == (800, Decimal("40000.00"))
    # Sem alavancar, a dívida é só mais caixa e a meta vale sobre a carteira inteira
    assert run(OFF) == (720, Decimal("48000.00"))


def test_the_view_shows_the_effective_target_with_debt():
    held = {"AAA": Holding("AAA", Decimal(800), Decimal(0), Decimal(100))}
    fixed = FixedHolding(uuid.uuid4(), "CDB", Decimal(40000), True, Decimal(40000))
    ctx = context(
        cash="0",
        history={"AAA": closes([100.0])},
        holdings=held,
        fixed_holdings=[fixed],
        offers=[offer(daily_liquidity=True)],
        debt="20000",
    )

    view = TargetRebalance().view(
        ctx, {"asset": "AAA", "stock_target": 60, "max_deviation": 5, **ON}
    )

    assert view is not None
    assert view.items[0].target_pct == Decimal("66.7")  # type: ignore[union-attr]
