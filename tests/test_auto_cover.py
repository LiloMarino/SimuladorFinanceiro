"""Cobertura automática: renda fixa vendida antes dos débitos do sistema, na ordem e com o aviso."""

from __future__ import annotations

import threading
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.base_event import BaseEventDTO
from backend.core.dto.events.credit import CreditEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import (
    CashflowEventType,
    CreditEventType,
    FixedIncomeType,
    IndicatorSeries,
    RateIndexType,
)
from backend.features.credit.credit_book import CreditBook
from backend.features.fixed_income import treasury
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.fixed_broker import FixedBroker
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.fixed_income.quotes import FixedIncomeQuotes
from tests.conftest import SetIndicator
from tests.fakes import FakeSimulationEngine, client, daily_series, monthly_series

INVESTOR = client("investor")
START = date(2030, 9, 2)
FIRST_MONTH = date(2030, 10, 1)
TODAY = date(2031, 3, 3)
PREMIUM = Decimal("0.02")
QUOTES = FixedIncomeQuotes(premium=PREMIUM)
CENT = Decimal("0.01")

PREFIXED = RateIndexType.PREFIXADO
SELIC = RateIndexType.SELIC
IPCA = RateIndexType.IPCA

type Sent = list[tuple[str, dict, uuid.UUID | None]]


class CoverEngine(FakeSimulationEngine):
    """Motor em memória com a renda fixa de verdade, para a porta de débito rodar inteira."""

    def __init__(self, cash: str, day: date = TODAY):
        super().__init__(cash={INVESTOR: Decimal(cash)}, current_date=day)
        self.fixed_broker = FixedBroker(self, threading.RLock())
        self.marked_allowed = False
        self.use_cover_marked(lambda _client: self.marked_allowed)

    def _move_cash(
        self, client_id, delta, event_type, life_event_key=None, ticker=None
    ) -> None:
        self.cash[client_id] += delta

    def hold(self, asset: FixedIncomeAssetDTO, applied: str, current: str) -> None:
        position = FixedIncomePosition(
            asset=asset,
            total_applied=Decimal(applied),
            first_applied_date=FIRST_MONTH,
        )
        position.current_value = Decimal(current)
        self.fixed_broker.get_fixed_positions(INVESTOR)[asset.asset_uuid] = position

    def held_names(self) -> set[str]:
        return {
            p.asset.name
            for p in self.fixed_broker.get_fixed_positions(INVESTOR).values()
        }


@pytest.fixture(autouse=True)
def economy(indicators: SetIndicator) -> None:
    """SELIC ~11% e IPCA ~4% ao ano, constantes, de 2018 a 2045."""
    indicators(
        IndicatorSeries.SELIC,
        daily_series(date(2018, 1, 1), date(2045, 1, 1), "0.0414"),
    )
    indicators(IndicatorSeries.IPCA, monthly_series(date(2018, 1, 1), 336, "0.33"))


@pytest.fixture(autouse=True)
def fixed_income_db(
    monkeypatch: pytest.MonkeyPatch, captured_events: list[BaseEventDTO]
) -> None:
    monkeypatch.setattr(
        repository.fixed_income, "get_events", lambda simulation_id, user_id: []
    )
    monkeypatch.setattr(
        repository.fixed_income, "get_or_create_asset", lambda simulation_id, asset: 7
    )


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> Sent:
    """Os avisos que a porta de débito mandou ao jogador."""
    messages: Sent = []
    monkeypatch.setattr(
        "backend.features.simulation.simulation_engine.notify",
        lambda name, payload, to=None: messages.append((name, payload, to)),
    )
    monkeypatch.setattr(
        "backend.features.credit.credit_book.notify", lambda *_args, **_kwargs: None
    )
    return messages


def title(rate_index: RateIndexType, nth: int = 0) -> FixedIncomeAssetDTO:
    """O `nth` título do Tesouro (por vencimento) do indexador, emitido em outubro de 2030."""
    titles = sorted(
        (
            a
            for a in treasury.issue(1, START, FIRST_MONTH, Decimal(0)).values()
            if a.rate_index is rate_index
        ),
        key=lambda a: a.maturity_date,
    )
    return titles[nth]


def cdb(name: str, rate: str) -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name=name,
        issuer="Banco Teste",
        investment_type=FixedIncomeType.CDB,
        rate_index=PREFIXED,
        maturity_date=date(2032, 1, 4),
        interest_rate=Decimal(rate),
        daily_liquidity=True,
    )


def names(messages: Sent) -> list[str]:
    return [payload["asset_name"] for _name, payload, _to in messages]


def test_sells_loss_free_titles_from_the_lowest_rate_to_the_highest(sent: Sent):
    engine = CoverEngine("0")
    low, high, selic = cdb("CDB baixo", "0.01"), cdb("CDB alto", "0.30"), title(SELIC)
    for asset in (high, selic, low):
        engine.hold(asset, "1000", "1000")

    engine.cover_before_debit(INVESTOR, Decimal(2500), CashflowEventType.EXPENSE)

    assert names(sent) == [low.name, selic.name, high.name]
    assert engine.cash[INVESTOR] >= Decimal(2500) - CENT


def test_sells_only_what_the_debit_needs(sent: Sent):
    engine = CoverEngine("0")
    engine.hold(cdb("CDB", "0.10"), "10000", "10000")

    engine.cover_before_debit(INVESTOR, Decimal(3000), CashflowEventType.EXPENSE)

    assert engine.cash[INVESTOR] == Decimal(3000)
    [position] = engine.fixed_broker.get_fixed_positions(INVESTOR).values()
    assert Decimal(6900) < position.current_value < Decimal(7100)


def test_cash_that_covers_the_debit_sells_nothing(sent: Sent):
    engine = CoverEngine("5000")
    engine.hold(cdb("CDB", "0.10"), "10000", "10000")

    engine.cover_before_debit(INVESTOR, Decimal(5000), CashflowEventType.EXPENSE)

    assert sent == []
    assert engine.cash[INVESTOR] == Decimal(5000)
    assert engine.held_names() == {"CDB"}


def test_negative_cash_is_brought_back_to_cover_the_debit(sent: Sent):
    engine = CoverEngine("-200")
    engine.hold(cdb("CDB", "0.10"), "10000", "10000")

    engine.cover_before_debit(INVESTOR, Decimal(800), CashflowEventType.EXPENSE)

    assert engine.cash[INVESTOR] == Decimal(800)


def test_option_off_keeps_the_prefixed_and_the_ipca_titles(sent: Sent):
    engine = CoverEngine("0")
    engine.use_risk_premium(lambda _day: PREMIUM)
    engine.hold(title(PREFIXED), "10000", "10500")
    engine.hold(title(IPCA), "10000", "10500")

    engine.cover_before_debit(INVESTOR, Decimal(3000), CashflowEventType.EXPENSE)

    assert sent == []
    assert engine.cash[INVESTOR] == 0
    assert len(engine.held_names()) == 2


def test_option_on_sells_the_loss_free_titles_before_the_marked_ones(sent: Sent):
    engine = CoverEngine("0")
    engine.marked_allowed = True
    engine.use_risk_premium(lambda _day: PREMIUM)
    prefixed = title(PREFIXED)
    cash_like = cdb("CDB", "0.10")
    engine.hold(prefixed, "10000", "10500")
    engine.hold(cash_like, "1000", "1000")

    engine.cover_before_debit(INVESTOR, Decimal(1500), CashflowEventType.EXPENSE)

    assert names(sent) == [cash_like.name, prefixed.name]
    assert engine.cash[INVESTOR] >= Decimal(1500) - CENT


def test_option_on_sells_the_marked_title_that_loses_least_first(sent: Sent):
    engine = CoverEngine("0")
    engine.marked_allowed = True
    engine.use_risk_premium(lambda _day: PREMIUM)
    near, far = title(PREFIXED, 0), title(PREFIXED, 1)
    engine.hold(far, "10000", "10500")
    engine.hold(near, "10000", "10500")
    near_position = engine.fixed_broker.get_fixed_positions(INVESTOR)[near.asset_uuid]
    far_position = engine.fixed_broker.get_fixed_positions(INVESTOR)[far.asset_uuid]
    assert near_position.mark(TODAY, QUOTES) > far_position.mark(TODAY, QUOTES)

    engine.cover_before_debit(INVESTOR, Decimal(1000), CashflowEventType.EXPENSE)

    assert names(sent) == [near.name]
    assert engine.cash[INVESTOR] >= Decimal(1000) - CENT
    assert far.name in engine.held_names()


def test_covers_what_it_can_when_the_titles_are_not_enough(sent: Sent):
    engine = CoverEngine("100")
    engine.hold(cdb("CDB", "0.10"), "1000", "1000")

    engine.cover_before_debit(INVESTOR, Decimal(5000), CashflowEventType.EXPENSE)

    assert engine.held_names() == set()
    assert engine.cash[INVESTOR] == Decimal(1100)


def test_each_sale_notifies_the_player_with_the_covered_expense(sent: Sent):
    engine = CoverEngine("0")
    asset = cdb("CDB do jogador", "0.10")
    engine.hold(asset, "10000", "10000")

    engine.cover_before_debit(INVESTOR, Decimal(900), CashflowEventType.TAX)

    [(name, payload, to)] = sent
    assert name == "auto_redeem"
    assert to == INVESTOR
    assert payload["asset_name"] == "CDB do jogador"
    assert Decimal(payload["net_amount"]) == Decimal(900)
    assert payload["reason"] == "o imposto de renda"


@pytest.mark.parametrize(
    ("pay", "reason"),
    [
        (lambda e: e.pay_expense(INVESTOR, Decimal(600)), "a despesa do mês"),
        (
            lambda e: e.charge_unexpected(INVESTOR, Decimal(600), "key"),
            "o imprevisto",
        ),
        (lambda e: e.pay_income_tax(INVESTOR, Decimal(600)), "o imposto de renda"),
    ],
)
def test_automatic_debits_sell_before_debiting(pay, reason, sent: Sent):
    engine = CoverEngine("100")
    engine.hold(cdb("CDB", "0.10"), "10000", "10000")

    pay(engine)

    assert engine.cash[INVESTOR] == 0
    assert [payload["reason"] for _n, payload, _t in sent] == [reason]


def test_loan_installment_is_covered_before_it_becomes_late(
    monkeypatch: pytest.MonkeyPatch, sent: Sent, captured_events: list[BaseEventDTO]
):
    engine = CoverEngine("10000", day=START)
    engine.fixed_income_market = FixedIncomeMarket(1, date(2035, 1, 1))
    engine.credit_book = CreditBook(
        engine,
        threading.RLock(),
        history=lambda _client_id, _before, _last: [],
    )
    monkeypatch.setattr(
        repository.credit, "get_events", lambda _simulation_id, _user_id: []
    )
    engine.receive_loan = lambda client_id, amount: engine.add_cash(client_id, amount)
    engine.pay_loan = lambda client_id, amount: engine.add_cash(client_id, -amount)
    engine.assets_value = lambda client_id: engine.cash[client_id]
    loan = engine.credit_book.contract(INVESTOR, Decimal(5000), 12)
    installment = loan.state.due_amount()
    due = loan.state.next_due
    # O caixa todo vai para um título de liquidez diária
    engine.cash[INVESTOR] = Decimal(0)
    engine.hold(cdb("CDB", "0.10"), "20000", "20000")

    day = START
    while day < due:
        day += timedelta(days=1)
        engine.current_date = day
        engine.credit_book.process_due([INVESTOR], day, 1)

    events = [e for e in captured_events if isinstance(e, CreditEventDTO)]
    assert events[-1].event_type is CreditEventType.INSTALLMENT_PAID
    assert CreditEventType.INSTALLMENT_LATE not in {e.event_type for e in events}
    assert loan.paid_installments == 1
    assert engine.cash[INVESTOR] == 0
    assert [payload["reason"] for _n, payload, _t in sent] == [
        "a parcela do empréstimo"
    ]
    assert Decimal(sent[0][1]["net_amount"]) == installment


def test_covers_a_debit_selling_dollars_of_the_dollar_account(sent: Sent):
    """A conta em dólar vende como os demais títulos de liquidez diária: tira US$ ao dólar de hoje e cobre o débito em reais."""
    engine = CoverEngine("0")
    engine.use_dollar_history(lambda _day: Decimal("5"))
    account = FixedIncomeAssetDTO(
        name="Conta em dólar",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.DOLLAR_ACCOUNT,
        rate_index=RateIndexType.FED_FUNDS,
        maturity_date=date(2032, 1, 4),
        interest_rate=Decimal(1),
        daily_liquidity=True,
    )
    engine.hold(account, "8000", "2000")

    engine.cover_before_debit(INVESTOR, Decimal(3000), CashflowEventType.EXPENSE)

    assert names(sent) == [account.name]
    assert engine.cash[INVESTOR] >= Decimal(3000) - CENT
    [position] = engine.fixed_broker.get_fixed_positions(INVESTOR).values()
    assert Decimal(1300) < position.current_value < Decimal(1500)
