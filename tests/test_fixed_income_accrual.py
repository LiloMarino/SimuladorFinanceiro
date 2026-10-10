from __future__ import annotations

import json
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

import backend.features.fixed_income.fixed_broker as fixed_broker
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import (
    FixedIncomeEventType,
    FixedIncomeType,
    IndicatorSeries,
    RateIndexType,
)
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import (
    annual_to_daily_factor,
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
from tests.conftest import SetIndicator
from tests.fakes import daily_series, monthly_series

CDI_2020 = Path(__file__).parent / "fixtures" / "cdi_2020.json"

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

    projection = project(asset, amount, BUY_DATE)

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


def test_rebuild_with_contributions_on_different_days_matches_live(
    replay_events, indicators: SetIndicator
):
    """Reconstrução com aportes em dias diferentes bate com o jogo ao vivo."""
    indicators(
        IndicatorSeries.CDI, daily_series(date(2020, 1, 1), date(2020, 12, 31), "0.04")
    )
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
    projection = project(_asset(), Decimal(0), BUY_DATE)

    assert projection.net_amount == Decimal("0.00")
    assert projection.gross_return_pct > 0
    assert projection.net_return_pct == projection.gross_return_pct * (
        1 - projection.income_tax_rate
    )


def test_lci_projection_net_equals_gross():
    """LCI isenta: o líquido da projeção é o bruto arredondado ao centavo."""
    asset = _asset(investment_type=FixedIncomeType.LCI)

    projection = project(asset, Decimal("1000"), BUY_DATE)

    assert projection.income_tax_rate == 0
    assert projection.net_amount == projection.gross_amount.quantize(Decimal("0.01"))


def test_daily_factor_compounds_to_annual_rate():
    """252 dias úteis do fator diário recompõem a taxa anual."""
    compounded = annual_to_daily_factor(Decimal("0.12")) ** 252

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


def test_index_rate_on_annualizes_the_asset_index(indicators: SetIndicator):
    """
    A taxa anual de cada indexador sai da sua série: CDI/SELIC compõem o valor do
    dia por 252 dias úteis; IPCA acumula os últimos 12 meses.
    """
    indicators(IndicatorSeries.CDI, daily_series(BUY_DATE, BUY_DATE, "0.04"))
    indicators(IndicatorSeries.SELIC, daily_series(BUY_DATE, BUY_DATE, "0.05"))
    indicators(IndicatorSeries.IPCA, monthly_series(date(2019, 1, 1), 13, "0.5"))

    assert index_rate_on(RateIndexType.CDI, BUY_DATE) == Decimal("1.0004") ** 252 - 1
    assert index_rate_on(RateIndexType.SELIC, BUY_DATE) == Decimal("1.0005") ** 252 - 1
    ipca_12m = index_rate_on(RateIndexType.IPCA, BUY_DATE)
    assert abs(ipca_12m - (Decimal("1.005") ** 12 - 1)) < Decimal("1e-20")
    assert index_rate_on(RateIndexType.PREFIXADO, BUY_DATE) == Decimal(0)


def test_cdi_live_rebuilt_and_projected_match_on_constant_series(
    replay_events, indicators: SetIndicator
):
    """Com o CDI constante, a projeção na compra é o que o jogo credita no resgate."""
    indicators(
        IndicatorSeries.CDI, daily_series(date(2020, 1, 1), date(2021, 6, 30), "0.04")
    )
    asset = _asset(RateIndexType.CDI, "1.1")
    amount = Decimal("10000")

    projection = project(asset, amount, BUY_DATE)

    live = FixedIncomePosition(asset, amount, BUY_DATE)
    _tick_until(live, BUY_DATE, live.redemption_date)

    resume_from = date(2020, 7, 15)
    replay_events([(asset, _buy_event(1, "10000", BUY_DATE))])
    resumed = fixed_broker.load_fixed_assets(1, CLIENT_ID, resume_from)[
        asset.asset_uuid
    ]
    _tick_until(resumed, resume_from, resumed.redemption_date)

    assert live.net_redemption_value() == projection.net_amount
    assert resumed.current_value == live.current_value


def test_day_without_cdi_inside_the_series_does_not_accrue(indicators: SetIndicator):
    """Feriado (dia útil sem CDI publicado) não rende: nem o índice, nem o spread."""
    holiday = date(2020, 1, 7)
    values = daily_series(BUY_DATE, date(2020, 1, 31), "0.04")
    del values[holiday]
    indicators(IndicatorSeries.CDI, values)
    asset = _asset(RateIndexType.CDI, "1")
    position = FixedIncomePosition(asset, Decimal("1000"), BUY_DATE)

    position.accrue(holiday)  # rende a noite de 06/01 com o CDI de 06/01
    after_holiday_tick = position.current_value
    position.accrue(date(2020, 1, 8))  # a noite de 07/01 não teve CDI

    assert after_holiday_tick == Decimal("1000") * Decimal("1.0004")
    assert position.current_value == after_holiday_tick


def test_after_the_series_ends_the_last_value_holds(indicators: SetIndicator):
    """Depois do último dado real vale o último valor conhecido, como no preço das ações."""
    indicators(IndicatorSeries.CDI, {date(2020, 1, 3): Decimal("0.04")})
    asset = _asset(RateIndexType.CDI, "1")
    position = FixedIncomePosition(asset, Decimal("1000"), BUY_DATE)

    _tick_until(position, BUY_DATE, date(2020, 1, 10))

    assert position.current_value == Decimal("1000") * Decimal("1.0004") ** 4


def test_ipca_month_spread_over_its_business_days_closes_the_monthly_rate(
    indicators: SetIndicator,
):
    """O IPCA do mês, distribuído pelos dias úteis, fecha a taxa mensal publicada."""
    indicators(IndicatorSeries.IPCA, monthly_series(date(2020, 1, 1), 3, "0.5"))
    asset = _asset(RateIndexType.IPCA, "0")
    # Comprado no 1º dia útil de fevereiro: os ticks até 02/03 rendem as 20 noites
    # dos dias úteis de fevereiro
    position = FixedIncomePosition(asset, Decimal("1000"), date(2020, 2, 3))

    _tick_until(position, date(2020, 2, 3), date(2020, 3, 2))

    assert abs(position.current_value - Decimal("1005")) < Decimal("1e-20")


def test_cdb_100_cdi_over_2020_yields_the_published_cdi(indicators: SetIndicator):
    """
    Aceite da F20: CDB 100% do CDI do primeiro ao último dia útil de 2020 rende,
    antes do IR, o que a Calculadora do Cidadão do Banco Central dá para o mesmo
    período (índice 1,02750141 de 02/01/2020 a 31/12/2020).
    """
    cdi_2020 = json.loads(CDI_2020.read_text())
    indicators(
        IndicatorSeries.CDI,
        {date.fromisoformat(d): Decimal(v) for d, v in cdi_2020.items()},
    )
    asset = _asset(RateIndexType.CDI, "1", maturity=date(2020, 12, 31))
    position = FixedIncomePosition(asset, Decimal("1000"), date(2020, 1, 2))

    _tick_until(position, date(2020, 1, 2), position.redemption_date)

    assert (position.current_value / 1000).quantize(Decimal("1e-8")) == Decimal(
        "1.02750141"
    )
