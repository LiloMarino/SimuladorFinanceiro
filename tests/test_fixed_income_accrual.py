from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest

import backend.features.fixed_income.fixed_broker as fixed_broker
from backend.core import repository
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType, RateIndexType
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import (
    daily_factor,
    effective_annual_rate,
    income_tax_rate,
    index_rate_on,
    net_redemption,
    project,
    redemption_date,
)
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)

CLIENT_ID = uuid.uuid4()
BUY_DATE = date(2020, 1, 6)  # segunda-feira


def _asset(
    rate_index: RateIndexType = RateIndexType.PREFIXADO,
    interest_rate: str = "0.1234",
    investment_type: FixedIncomeType = FixedIncomeType.CDB,
    maturity: date = date(2021, 3, 14),  # domingo: resgate na segunda seguinte
) -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name="CDB Teste",
        issuer="Banco Teste",
        investment_type=investment_type,
        rate_index=rate_index,
        maturity_date=maturity,
        interest_rate=Decimal(interest_rate),
    )


def _tick_until(position: FixedIncomePosition, start: date, end: date) -> None:
    """Simula o loop: um `accrue` por dia útil depois de `start`, até `end`."""
    day = start
    while day < end:
        day = next_business_day(day)
        position.accrue(day)


def _buy_event(asset_id: int, amount: str, on: date) -> FixedIncomeEventDTO:
    return FixedIncomeEventDTO(
        simulation_id=1,
        user_id=1,
        asset_id=asset_id,
        event_type=FixedIncomeEventType.BUY,
        amount=Decimal(amount),
        event_date=on,
    )


@pytest.fixture
def replay_events(monkeypatch: pytest.MonkeyPatch):
    """Faz `load_fixed_assets` ler os eventos informados no lugar do banco."""

    def _set(events: list[tuple[FixedIncomeAssetDTO, FixedIncomeEventDTO]]):
        monkeypatch.setattr(fixed_broker.UserManager, "get_user_id", lambda _: 1)
        monkeypatch.setattr(
            fixed_broker.repository.fixed_income,
            "get_events",
            lambda simulation_id, user_id: events,
        )

    return _set


def test_prefixed_live_resumed_and_projected_match(replay_events):
    """Prefixado credita o mesmo valor rodando direto, retomado e na projeção."""
    asset = _asset()
    amount = Decimal("10000")

    projection = project(asset, amount, BUY_DATE, Decimal(0))

    # (a) rodando direto
    live = FixedIncomePosition(asset, amount, BUY_DATE)
    _tick_until(live, BUY_DATE, live.redemption_date)

    # (b) pausando no meio: reconstrói dos eventos e segue tick a tick
    resume_from = date(2020, 7, 15)
    replay_events([(asset, _buy_event(1, "10000", BUY_DATE))])
    resumed = fixed_broker.load_fixed_assets(1, CLIENT_ID, resume_from)[
        asset.asset_uuid
    ]
    _tick_until(resumed, resume_from, resumed.redemption_date)

    assert live.net_redemption_value() == projection.net_amount
    assert resumed.net_redemption_value() == projection.net_amount
    assert resumed.current_value == live.current_value
    assert projection.redemption_date == date(2021, 3, 15)


def test_rebuild_with_contributions_on_different_days_matches_live(replay_events):
    """Reconstrução com aportes em dias diferentes bate com o jogo ao vivo."""
    asset = _asset(RateIndexType.CDI, "1.05")
    second_buy = date(2020, 3, 11)
    until = date(2020, 9, 30)

    live = FixedIncomePosition(asset, Decimal("5000"), BUY_DATE)
    _tick_until(live, BUY_DATE, second_buy)
    live.invest(Decimal("2500.50"))
    _tick_until(live, second_buy, until)

    replay_events(
        [
            (asset, _buy_event(1, "5000", BUY_DATE)),
            (asset, _buy_event(1, "2500.50", second_buy)),
        ]
    )
    rebuilt = fixed_broker.load_fixed_assets(1, CLIENT_ID, until)[asset.asset_uuid]

    assert rebuilt.current_value == live.current_value
    assert rebuilt.total_applied == Decimal("7500.50")


def test_redeemed_position_is_not_rebuilt(replay_events):
    """Posição já resgatada não volta na reconstrução."""
    asset = _asset()
    redeem = FixedIncomeEventDTO(
        simulation_id=1,
        user_id=1,
        asset_id=1,
        event_type=FixedIncomeEventType.REDEEM,
        amount=Decimal("12000"),
        event_date=date(2021, 3, 15),
    )
    replay_events([(asset, _buy_event(1, "10000", BUY_DATE)), (asset, redeem)])

    assert fixed_broker.load_fixed_assets(1, CLIENT_ID, date(2021, 4, 1)) == {}


def test_same_day_accrues_once_and_nothing_after_redemption():
    """Cada dia rende uma única vez e nada rende depois do resgate."""
    position = FixedIncomePosition(_asset(), Decimal("1000"), BUY_DATE)
    day = next_business_day(BUY_DATE)

    position.accrue(day)
    after_first = position.current_value
    position.accrue(day)

    assert after_first > Decimal("1000")
    assert position.current_value == after_first

    _tick_until(position, day, position.redemption_date)
    at_redemption = position.current_value
    position.accrue(next_business_day(position.redemption_date))
    assert position.current_value == at_redemption


def test_cdi_yields_percentage_of_cdi():
    """Título CDI rende o percentual contratado do CDI."""
    asset = _asset(RateIndexType.CDI, "1.05")
    assert effective_annual_rate(asset, Decimal("0.10")) == Decimal("0.1050")


def test_ipca_and_selic_compound_spread_over_index():
    """IPCA+ e SELIC+ compõem o spread sobre o índice, como no mercado."""
    ipca = _asset(RateIndexType.IPCA, "0.06")
    selic = _asset(RateIndexType.SELIC, "0.001")

    # (1 + 4,68%) * (1 + 6%) - 1 = 10,9608%
    assert effective_annual_rate(ipca, Decimal("0.0468")) == Decimal("0.109608")
    assert effective_annual_rate(selic, Decimal("0.15")) == Decimal("0.15115")


def test_income_tax_brackets_and_lci_lca_exemption():
    """IR segue a tabela regressiva nas fronteiras de faixa; LCI e LCA são isentas."""
    assert income_tax_rate(FixedIncomeType.CDB, 180) == Decimal("0.225")
    assert income_tax_rate(FixedIncomeType.CDB, 181) == Decimal("0.20")
    assert income_tax_rate(FixedIncomeType.CDB, 720) == Decimal("0.175")
    assert income_tax_rate(FixedIncomeType.CDB, 721) == Decimal("0.15")
    assert income_tax_rate(FixedIncomeType.LCI, 10) == Decimal(0)
    assert income_tax_rate(FixedIncomeType.LCA, 10) == Decimal(0)


def test_zero_amount_projection_has_percentages():
    """Projeção com valor zero ainda mostra os percentuais de rendimento."""
    projection = project(_asset(), Decimal(0), BUY_DATE, Decimal(0))

    assert projection.net_amount == Decimal("0.00")
    assert projection.gross_return_pct > 0
    assert projection.net_return_pct == projection.gross_return_pct * (
        1 - projection.income_tax_rate
    )


def test_lci_projection_net_equals_gross():
    """LCI isenta: o líquido da projeção é o bruto arredondado ao centavo."""
    asset = _asset(investment_type=FixedIncomeType.LCI)

    projection = project(asset, Decimal("1000"), BUY_DATE, Decimal(0))

    assert projection.income_tax_rate == 0
    assert projection.net_amount == projection.gross_amount.quantize(Decimal("0.01"))


def test_daily_factor_compounds_to_annual_rate():
    """252 dias úteis do fator diário recompõem a taxa anual."""
    compounded = daily_factor(Decimal("0.12")) ** 252

    assert abs(compounded - Decimal("1.12")) < Decimal("1e-20")


def test_redemption_date_moves_weekend_to_monday():
    """Vencimento no fim de semana resgata na segunda; em dia útil, no próprio dia."""
    assert redemption_date(date(2021, 3, 13)) == date(2021, 3, 15)
    assert redemption_date(date(2021, 3, 14)) == date(2021, 3, 15)
    assert redemption_date(date(2021, 3, 16)) == date(2021, 3, 16)


def test_net_redemption_without_profit_charges_no_tax():
    """Sem lucro não há IR: o resgate devolve o montante inteiro."""
    assert net_redemption(Decimal("950"), Decimal("1000"), Decimal("0.225")) == Decimal(
        "950.00"
    )


def test_net_redemption_taxes_only_profit_and_rounds_half_even():
    """IR incide só sobre o lucro e o resgate arredonda ao centavo pelo método bancário."""
    # 1100 - 100 * 0,15 = 1085
    assert net_redemption(Decimal("1100"), Decimal("1000"), Decimal("0.15")) == Decimal(
        "1085.00"
    )
    assert net_redemption(
        Decimal("100.125"), Decimal("100.125"), Decimal(0)
    ) == Decimal("100.12")
    assert net_redemption(
        Decimal("100.135"), Decimal("100.135"), Decimal(0)
    ) == Decimal("100.14")


def test_index_rate_on_reads_the_asset_index(monkeypatch: pytest.MonkeyPatch):
    """Cada indexador lê a sua própria série; prefixado não tem indexador."""
    monkeypatch.setattr(repository.economic, "get_cdi_rate", lambda _: Decimal("0.10"))
    monkeypatch.setattr(repository.economic, "get_ipca_rate", lambda _: Decimal("0.04"))
    monkeypatch.setattr(
        repository.economic, "get_selic_rate", lambda _: Decimal("0.11")
    )

    assert index_rate_on(RateIndexType.CDI, BUY_DATE) == Decimal("0.10")
    assert index_rate_on(RateIndexType.IPCA, BUY_DATE) == Decimal("0.04")
    assert index_rate_on(RateIndexType.SELIC, BUY_DATE) == Decimal("0.11")
    assert index_rate_on(RateIndexType.PREFIXADO, BUY_DATE) == Decimal(0)
