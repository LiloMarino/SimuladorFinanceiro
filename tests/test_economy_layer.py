"""A camada da economia sobre as séries guardadas: leitura das séries, nível da bolsa, beta e ligações."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import AssetOrigin, IndicatorSeries, MeasureKind, MeasureStatus
from backend.core.indicators import annualize_daily
from backend.core.rates import Percent
from backend.core.repository.economic import IndicatorHistory
from backend.features.economy import layer
from backend.features.economy.layer import EconomyLayer
from backend.features.economy.links import NO_LINK, LinkMonth
from backend.features.government import spending_effects as fx
from backend.features.government.state import Measure
from tests.fakes import daily_series, monthly_series

AUX = MeasureKind.WELFARE_SPENDING
START = date(2020, 1, 1)
EFFECTIVE = date(2021, 1, 4)


def measure(kind: MeasureKind, value: str, before: str) -> Measure:
    return Measure(
        id=1,
        kind=kind,
        value=Decimal(value),
        before=Decimal(before),
        sector=None,
        segment=None,
        proposer_id=1,
        term_start=START,
        proposed=START,
        status=MeasureStatus.APPROVED,
        effective=EFFECTIVE,
    )


# A leitura das séries


@pytest.fixture
def economy(indicators):
    indicators(IndicatorSeries.IPCA, monthly_series(START, 80, "0.30"))
    indicators(IndicatorSeries.SELIC, daily_series(START, date(2026, 12, 31), "0.05"))
    indicators(IndicatorSeries.CDI, daily_series(START, date(2026, 12, 31), "0.05"))
    indicators(IndicatorSeries.IBOV, daily_series(START, date(2026, 12, 31), "100000"))
    spending = fx.SpendingEconomy()
    spending.update([measure(AUX, "0.02", "0.015")])
    return EconomyLayer(1, START, spending)


def history_of(series: IndicatorSeries) -> IndicatorHistory:
    values = {
        IndicatorSeries.IPCA: monthly_series(START, 80, "0.30"),
        IndicatorSeries.SELIC: daily_series(START, date(2026, 12, 31), "0.05"),
        IndicatorSeries.CDI: daily_series(START, date(2026, 12, 31), "0.05"),
        IndicatorSeries.IBOV: daily_series(START, date(2026, 12, 31), "100000"),
    }[series]
    return IndicatorHistory(sorted(values), values)


def test_the_ipca_gets_the_monthly_share_of_the_points_and_the_past_stays(economy):
    history = history_of(IndicatorSeries.IPCA)
    adjusted = economy.adjust(IndicatorSeries.IPCA, history)
    full = date(2021, 8, 1)

    assert adjusted.values[date(2020, 6, 1)] == Decimal("0.30")
    assert adjusted.values[date(2021, 1, 1)] == Decimal("0.30")
    assert adjusted.values[full] == Decimal("0.30") + Decimal(
        str(round(economy.inflation_points(full) / 12, 6))
    )
    assert adjusted.values[full] > Decimal("0.30")
    # A série guardada não é tocada
    assert history.values[full] == Decimal("0.30")


def test_selic_and_cdi_rise_together_by_the_reaction_of_the_central_bank(economy):
    day = date(2021, 8, 2)
    base = annualize_daily(Percent(Decimal("0.05")))

    for series in (IndicatorSeries.SELIC, IndicatorSeries.CDI):
        adjusted = economy.adjust(series, history_of(series))
        assert adjusted.values[day] > Decimal("0.05")
        assert annualize_daily(Percent(adjusted.values[day])) == pytest.approx(
            base + Decimal(str(economy.selic_points(day) / 100)), abs=Decimal("0.0001")
        )
        assert adjusted.values[date(2020, 6, 1)] == Decimal("0.05")


def test_the_ibovespa_is_scaled_by_the_level_of_the_stocks(economy):
    day = date(2021, 8, 2)
    adjusted = economy.adjust(IndicatorSeries.IBOV, history_of(IndicatorSeries.IBOV))

    assert float(adjusted.values[day]) == pytest.approx(
        100000 * economy.level(day), abs=0.01
    )
    assert adjusted.values[day] < Decimal("100000")


def test_without_measures_the_series_come_back_untouched():
    nothing = EconomyLayer(1, START, fx.SpendingEconomy())
    history = history_of(IndicatorSeries.SELIC)

    assert nothing.adjust(IndicatorSeries.SELIC, history) is history
    assert nothing.stock_factor("AAA", date(2021, 8, 2)) == 1.0


def test_a_stock_follows_the_market_level_raised_to_its_beta(economy, monkeypatch):
    day = date(2021, 8, 2)
    monkeypatch.setattr(economy, "_betas", {"HIGH": 2.0, "LOW": 0.5})

    level = economy.level(day)
    assert economy.stock_factor("HIGH", day) == pytest.approx(level**2)
    assert economy.stock_factor("LOW", day) == pytest.approx(level**0.5)
    # Sem beta medido, o ativo anda como o mercado
    assert economy.stock_factor("NEW", day) == pytest.approx(level)
    assert economy.stock_factor("HIGH", day) < economy.stock_factor("LOW", day)


# A isenção do IR de um setor


def exempt_layer(since: date | None) -> EconomyLayer:
    nothing = EconomyLayer(1, START, fx.SpendingEconomy())
    nothing._classification = {
        "ENER3": StockSegmentDTO(sector="Energia", segment="Transmissão"),
        "BANK3": StockSegmentDTO(sector="Bancos", segment="Bancos"),
    }
    nothing.use_sector_exemption(
        lambda sector, segment, day: since if sector == "Energia" else None
    )
    return nothing


def test_an_exempt_sector_stock_rises_in_a_straight_line_to_the_ceiling():
    since = date(2021, 1, 1)
    economy = exempt_layer(since)
    months = layer.SECTOR_EXEMPT_RAMP_MONTHS

    assert economy.stock_factor("ENER3", since) == pytest.approx(1.0)
    half = since + timedelta(days=layer.months_to_days(months / 2))
    assert economy.stock_factor("ENER3", half) == pytest.approx(
        1 + layer.SECTOR_EXEMPT_BOOST / 2, abs=0.001
    )
    later = since + timedelta(days=layer.months_to_days(months * 3))
    assert economy.stock_factor("ENER3", later) == pytest.approx(
        1 + layer.SECTOR_EXEMPT_BOOST
    )


def test_the_exemption_leaves_other_sectors_and_unclassified_stocks_alone():
    economy = exempt_layer(date(2021, 1, 1))
    day = date(2022, 1, 1)

    assert economy.stock_factor("BANK3", day) == 1.0
    assert economy.stock_factor("NEW3", day) == 1.0


def test_without_an_exemption_the_stock_factor_is_the_market_alone():
    economy = exempt_layer(None)

    assert economy.stock_factor("ENER3", date(2022, 1, 1)) == 1.0


# O beta de cada ativo


def returns(
    factor: float, days: int = 120
) -> tuple[dict[date, float], dict[date, float]]:
    market = {START + timedelta(days=i): math.sin(i / 3) / 100 for i in range(days)}
    return {d: factor * r for d, r in market.items()}, market


def test_beta_is_how_much_the_asset_moves_per_point_of_the_market():
    asset, market = returns(2.0)

    assert layer.beta_of(asset, market) == pytest.approx(2.0)


def test_beta_is_limited_between_zero_and_three():
    assert layer.beta_of(*returns(5.0)) == layer.MAX_BETA
    assert layer.beta_of(*returns(-1.0)) == 0


def test_beta_is_one_when_there_are_too_few_common_days():
    assert layer.beta_of(*returns(2.0, days=layer.MIN_BETA_DAYS - 1)) == 1


# As ligações na camada

LINKED_FROM = date(2021, 2, 1)


class FixedLinks:
    """Uma ligação só, que vale de `LINKED_FROM` em diante."""

    def __init__(self, link: LinkMonth):
        self._link = link

    def first_day(self) -> date | None:
        return LINKED_FROM

    def links_on(self, day: date) -> LinkMonth:
        return self._link if day >= LINKED_FROM else NO_LINK


def linked(**gaps: str) -> EconomyLayer:
    link = LinkMonth(
        date(2021, 1, 31),
        Decimal(gaps.get("unemployment", "0")),
        Decimal(gaps.get("premium", "0")),
        Decimal(gaps.get("gdp", "0")),
        Decimal(gaps.get("primary", "0")),
        Decimal(0),
    )
    return EconomyLayer(1, START, fx.SpendingEconomy(), FixedLinks(link))


def test_the_links_add_their_ipca_points_from_the_day_they_hold(indicators):
    layer = linked(unemployment="-0.02", premium="0.02")
    history = history_of(IndicatorSeries.IPCA)

    adjusted = layer.adjust(IndicatorSeries.IPCA, history)

    # 0,7 ponto da curva de Phillips e o repasse do dólar que o prêmio levanta (2 pontos de
    # prêmio sobem o dólar 8,3%, e cada 1% de alta repassa 0,07 ponto), um doze avos por mês
    passed = 0.07 * math.expm1(0.08) * 100
    assert adjusted.values[date(2021, 1, 1)] == Decimal("0.30")
    assert adjusted.values[date(2021, 3, 1)] == Decimal("0.30") + Decimal(
        str(round((0.7 + passed) / 12, 6))
    )


def test_the_premium_pulls_the_stocks_like_the_selic_over_the_quarter(indicators):
    layer = linked(premium="0.01")
    day = date(2021, 6, 1)

    # 1 ponto de prêmio pesa como 1 ponto de SELIC, e a inflação a mais que ele
    # causa leva a SELIC a reagir também
    selic = layer.selic_points(day)
    assert layer.level(day) == pytest.approx(math.exp(-0.029 * (selic + 1.0)))
    assert layer.level(day) < 1


def test_the_gdp_above_history_lifts_the_stocks(indicators):
    layer = linked(gdp="0.01")
    day = date(2021, 6, 1)

    assert layer.level(day) == pytest.approx(math.exp(0.025))
    assert layer.level(date(2021, 1, 15)) == 1.0


def test_a_foreign_asset_follows_only_the_dollar_and_a_domestic_one_keeps_the_market(
    indicators,
):
    economy = linked(premium="0.02")
    economy._origins = {"AAPL": AssetOrigin.FOREIGN, "PETR4": AssetOrigin.DOMESTIC}
    economy._betas = {"PETR4": 1.0}
    day = date(2021, 6, 1)

    # 2 pontos de prêmio sobem o dólar 8,3% (e^0,08) e derrubam a bolsa daqui
    assert economy.dollar_factor(day) == pytest.approx(math.exp(0.08))
    assert economy.stock_factor("AAPL", day) == pytest.approx(math.exp(0.08))
    assert economy.stock_factor("PETR4", day) == pytest.approx(economy.level(day))
    assert economy.stock_factor("PETR4", day) < 1 < economy.stock_factor("AAPL", day)


def test_a_foreign_asset_is_untouched_before_the_links_and_without_government(
    indicators,
):
    economy = linked(premium="0.02")
    economy._origins = {"AAPL": AssetOrigin.FOREIGN}

    assert economy.stock_factor("AAPL", date(2021, 1, 15)) == 1.0

    nothing = EconomyLayer(1, START, fx.SpendingEconomy())
    nothing._origins = {"AAPL": AssetOrigin.FOREIGN}
    assert nothing.stock_factor("AAPL", date(2021, 8, 2)) == 1.0


class GrowingLinks:
    """As ligações que o coordenador acrescenta mês a mês: cada uma vale do dia dela em diante."""

    def __init__(self):
        self.added: list[tuple[date, LinkMonth]] = []

    def first_day(self) -> date | None:
        return self.added[0][0] if self.added else None

    def links_on(self, day: date) -> LinkMonth:
        held = [link for since, link in self.added if since <= day]
        return held[-1] if held else NO_LINK


def premium_link(premium: str) -> LinkMonth:
    return LinkMonth(
        date(2021, 1, 31),
        Decimal(0),
        Decimal(premium),
        Decimal(0),
        Decimal(0),
        Decimal(0),
    )


def test_a_new_link_redoes_only_the_days_from_it_and_matches_a_fresh_reading(
    indicators,
):
    spending = fx.SpendingEconomy()
    spending.update([measure(AUX, "0.02", "0.015")])
    links = GrowingLinks()
    stepped = EconomyLayer(1, START, spending, links)
    links.added.append((LINKED_FROM, premium_link("0.01")))
    stepped.refresh_from(LINKED_FROM)
    before = {
        series: stepped.adjust(series, history_of(series))
        for series in (IndicatorSeries.IPCA, IndicatorSeries.IBOV)
    }

    june = date(2021, 6, 1)
    links.added.append((june, premium_link("0.03")))
    stepped.refresh_from(june)
    fresh = EconomyLayer(1, START, spending, links)

    # O IPCA tem um valor por mês e o Ibovespa um por pregão
    days = {
        IndicatorSeries.IPCA: (date(2021, 5, 1), date(2021, 7, 1)),
        IndicatorSeries.IBOV: (date(2021, 5, 3), date(2021, 7, 1)),
    }
    for series, old in before.items():
        history = history_of(series)
        again = stepped.adjust(series, history)
        assert again.values == fresh.adjust(series, history).values
        # O dia antes da ligação nova fica como estava; o de depois traz o prêmio maior
        earlier, later = days[series]
        assert again.values[earlier] == old.values[earlier]
        assert again.values[later] != old.values[later]
