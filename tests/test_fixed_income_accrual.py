from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest

import backend.features.fixed_income.fixed_broker as fixed_broker
from backend.core.dto.economic_indicators import EconomicIndicatorsDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType, RateIndexType
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import (
    effective_annual_rate,
    income_tax_rate,
    project,
)
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)

CLIENT_ID = uuid.uuid4()
BUY_DATE = date(2020, 1, 6)  # segunda-feira


def make_asset(
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


def tick_until(position: FixedIncomePosition, start: date, end: date) -> None:
    """Simula o loop: um `accrue` por dia útil depois de `start`, até `end`."""
    day = start
    while day < end:
        day = next_business_day(day)
        position.accrue(day)


def buy_event(asset_id: int, amount: str, on: date) -> FixedIncomeEventDTO:
    return FixedIncomeEventDTO(
        simulation_id=1,
        user_id=1,
        asset_id=asset_id,
        event_type=FixedIncomeEventType.BUY,
        amount=Decimal(amount),
        event_date=on,
    )


@pytest.fixture
def replay_events(monkeypatch):
    """Faz `load_fixed_assets` ler os eventos informados no lugar do banco."""

    def _set(events: list[tuple[FixedIncomeAssetDTO, FixedIncomeEventDTO]]):
        monkeypatch.setattr(fixed_broker.UserManager, "get_user_id", lambda _: 1)
        monkeypatch.setattr(
            fixed_broker.repository.fixed_income,
            "get_events",
            lambda simulation_id, user_id: events,
        )

    return _set


def test_prefixado_credita_o_mesmo_valor_direto_retomado_e_projetado(replay_events):
    asset = make_asset()
    amount = Decimal("10000")

    projection = project(asset, amount, BUY_DATE, Decimal(0))

    # (a) rodando direto
    live = FixedIncomePosition(asset, amount, BUY_DATE)
    tick_until(live, BUY_DATE, live.redemption_date)

    # (b) pausando no meio: reconstrói dos eventos e segue tick a tick
    resume_from = date(2020, 7, 15)
    replay_events([(asset, buy_event(1, "10000", BUY_DATE))])
    resumed = fixed_broker.load_fixed_assets(1, CLIENT_ID, resume_from)[asset.asset_uuid]
    tick_until(resumed, resume_from, resumed.redemption_date)

    assert live.net_redemption_value() == projection.net_amount
    assert resumed.net_redemption_value() == projection.net_amount
    assert resumed.current_value == live.current_value
    assert projection.redemption_date == date(2021, 3, 15)


def test_reconstrucao_com_aportes_em_dias_diferentes_bate_com_o_jogo_ao_vivo(
    replay_events,
):
    asset = make_asset(RateIndexType.CDI, "1.05")
    second_buy = date(2020, 3, 11)
    until = date(2020, 9, 30)

    live = FixedIncomePosition(asset, Decimal("5000"), BUY_DATE)
    tick_until(live, BUY_DATE, second_buy)
    live.invest(Decimal("2500.50"))
    tick_until(live, second_buy, until)

    replay_events(
        [
            (asset, buy_event(1, "5000", BUY_DATE)),
            (asset, buy_event(1, "2500.50", second_buy)),
        ]
    )
    rebuilt = fixed_broker.load_fixed_assets(1, CLIENT_ID, until)[asset.asset_uuid]

    assert rebuilt.current_value == live.current_value
    assert rebuilt.total_applied == Decimal("7500.50")


def test_resgatado_nao_volta_na_reconstrucao(replay_events):
    asset = make_asset()
    redeem = FixedIncomeEventDTO(
        simulation_id=1,
        user_id=1,
        asset_id=1,
        event_type=FixedIncomeEventType.REDEEM,
        amount=Decimal("12000"),
        event_date=date(2021, 3, 15),
    )
    replay_events([(asset, buy_event(1, "10000", BUY_DATE)), (asset, redeem)])

    assert fixed_broker.load_fixed_assets(1, CLIENT_ID, date(2021, 4, 1)) == {}


def test_mesmo_dia_rende_uma_vez_e_nada_rende_depois_do_resgate():
    position = FixedIncomePosition(make_asset(), Decimal("1000"), BUY_DATE)
    day = next_business_day(BUY_DATE)

    position.accrue(day)
    after_first = position.current_value
    position.accrue(day)

    assert after_first > Decimal("1000")
    assert position.current_value == after_first

    tick_until(position, day, position.redemption_date)
    at_redemption = position.current_value
    position.accrue(next_business_day(position.redemption_date))
    assert position.current_value == at_redemption


def test_cdi_rende_o_percentual_do_cdi():
    asset = make_asset(RateIndexType.CDI, "1.05")
    assert effective_annual_rate(asset, Decimal("0.10")) == Decimal("0.1050")


def test_ipca_e_selic_compoem_o_spread_sobre_o_indice():
    ipca = make_asset(RateIndexType.IPCA, "0.06")
    selic = make_asset(RateIndexType.SELIC, "0.001")

    # (1 + 4,68%) * (1 + 6%) - 1 = 10,9608%
    assert effective_annual_rate(ipca, Decimal("0.0468")) == Decimal("0.109608")
    assert effective_annual_rate(selic, Decimal("0.15")) == Decimal("0.15115")


def test_tabela_regressiva_de_ir_e_isencao_de_lci_lca():
    assert income_tax_rate(FixedIncomeType.CDB, 180) == Decimal("0.225")
    assert income_tax_rate(FixedIncomeType.CDB, 181) == Decimal("0.20")
    assert income_tax_rate(FixedIncomeType.CDB, 720) == Decimal("0.175")
    assert income_tax_rate(FixedIncomeType.CDB, 721) == Decimal("0.15")
    assert income_tax_rate(FixedIncomeType.LCI, 10) == Decimal(0)
    assert income_tax_rate(FixedIncomeType.LCA, 10) == Decimal(0)


def test_projecao_com_valor_zero_tem_percentuais():
    projection = project(make_asset(), Decimal(0), BUY_DATE, Decimal(0))

    assert projection.net_amount == Decimal("0.00")
    assert projection.gross_return_pct > 0
    assert projection.net_return_pct == projection.gross_return_pct * (
        1 - projection.income_tax_rate
    )


def test_decimal_serializa_como_string_exata():
    payload = EconomicIndicatorsDTO(
        ipca=Decimal("1234.567891"), selic=Decimal("0.15"), cdi=Decimal("0.149")
    ).to_json()

    assert payload["ipca"] == "1234.567891"
