"""A camada da economia sobre as séries guardadas: leitura das séries, nível da bolsa, beta e ligações."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import AssetOrigin, IndicatorSeries, MeasureKind, MeasureStatus
from backend.core.indicators import annual_index_rate, annualize_daily
from backend.core.rates import Percent
from backend.core.repository.economic import IndicatorHistory
from backend.features.economy import layer
from backend.features.economy.layer import EconomyLayer
from backend.features.economy.links import NO_LINK, LinkMonth
from backend.features.economy.monetary import SelicBoard, SelicDecision, to_step
from backend.features.government import sector_boost
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


def boosted_layer(boost) -> EconomyLayer:
    nothing = EconomyLayer(1, START, fx.SpendingEconomy())
    nothing._classification = {
        "ENER3": StockSegmentDTO(sector="Energia", segment="Transmissão"),
        "BANK3": StockSegmentDTO(sector="Bancos", segment="Bancos"),
    }
    nothing.use_sector_boost(boost)
    return nothing


def exempt_layer(since: date | None) -> EconomyLayer:
    return boosted_layer(
        lambda sector, segment, day: (
            sector_boost.exemption_boost(since, day) if sector == "Energia" else 0.0
        )
    )


def test_an_exempt_sector_stock_rises_in_a_straight_line_to_the_ceiling():
    since = date(2021, 1, 1)
    economy = exempt_layer(since)
    months = sector_boost.RAMP_MONTHS

    assert economy.stock_factor("ENER3", since) == pytest.approx(1.0)
    half = since + timedelta(days=layer.months_to_days(months / 2))
    assert economy.stock_factor("ENER3", half) == pytest.approx(
        1 + sector_boost.SECTOR_EXEMPT_BOOST / 2, abs=0.001
    )
    later = since + timedelta(days=layer.months_to_days(months * 3))
    assert economy.stock_factor("ENER3", later) == pytest.approx(
        1 + sector_boost.SECTOR_EXEMPT_BOOST
    )


def test_the_exemption_leaves_other_sectors_and_unclassified_stocks_alone():
    economy = exempt_layer(date(2021, 1, 1))
    day = date(2022, 1, 1)

    assert economy.stock_factor("BANK3", day) == 1.0
    assert economy.stock_factor("NEW3", day) == 1.0


def test_without_an_exemption_the_stock_factor_is_the_market_alone():
    economy = exempt_layer(None)

    assert economy.stock_factor("ENER3", date(2022, 1, 1)) == 1.0


def stacked_layer(since: date, works: float, amendments: float) -> EconomyLayer:
    return boosted_layer(
        lambda sector, segment, day: (
            sector_boost.combined(
                sector_boost.exemption_boost(since, day), works, amendments
            )
            if sector == "Energia"
            else 0.0
        )
    )


def test_the_exemption_alone_gives_the_same_factor_through_the_combined_boost():
    since = date(2021, 1, 1)
    day = since + timedelta(days=layer.months_to_days(3))

    assert stacked_layer(since, 0.0, 0.0).stock_factor("ENER3", day) == pytest.approx(
        exempt_layer(since).stock_factor("ENER3", day)
    )


def test_the_exemption_works_and_amendments_add_up():
    since = date(2021, 1, 1)
    later = since + timedelta(days=layer.months_to_days(12))

    economy = stacked_layer(since, 0.0175, 0.03)

    assert economy.stock_factor("ENER3", later) == pytest.approx(1.1475)


def test_the_sum_of_the_boosts_stops_at_the_ceiling():
    since = date(2021, 1, 1)
    later = since + timedelta(days=layer.months_to_days(12))

    economy = stacked_layer(since, 0.075, 0.06)

    assert economy.stock_factor("ENER3", later) == pytest.approx(
        1 + sector_boost.SECTOR_BOOST_CAP
    )


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


# A surpresa do Copom: o esperado se dilui no trimestre e a decisão fora dele entra no dia

# Os pontos de IPCA da pressão são constantes; a regra do Banco Central soma 1,5 por ponto
RULE_PRESSURE = 1.0
RULE = layer.central_bank_reaction(RULE_PRESSURE)
FIRST_MEETING = date(2021, 3, 1)
MEETING_SPACING = timedelta(days=45)


class SteadyPressure:
    """Os pontos de IPCA que uma medida mantém, desde o início da partida."""

    def first_day(self) -> date | None:
        return START

    def inflation_points(self, day: date) -> float:
        return RULE_PRESSURE


def stored_selic(day: date) -> Decimal:
    return annual_index_rate(IndicatorSeries.SELIC, day, stored=True)


def follows_the_rule(day: date) -> SelicDecision:
    """A decisão do bot: a SELIC da história mais a regra, no passo de 0,25."""
    wanted = stored_selic(day) + Decimal(str(RULE / 100))
    return SelicDecision(day, to_step(wanted), 100.0)


def away_from_the_rule(day: date, points: float) -> SelicDecision:
    """A decisão que fica `points` pontos acima (ou abaixo, se negativo) da regra, sem arredondar."""
    selic = stored_selic(day) + Decimal(str((RULE + points) / 100))
    return SelicDecision(day, selic, 100.0)


@pytest.fixture
def board_economy(indicators):
    indicators(IndicatorSeries.SELIC, daily_series(START, date(2026, 12, 31), "0.05"))
    board = SelicBoard()
    economy = EconomyLayer(1, START, SteadyPressure(), monetary=board)
    return economy, board


def jump(economy: EconomyLayer, meeting: date) -> float:
    """Quanto a bolsa muda do dia da reunião para o dia em que a decisão passa a valer."""
    return economy.level(meeting + timedelta(days=1)) / economy.level(meeting) - 1


def test_a_president_who_follows_the_rule_has_a_gap_of_only_the_rounding(
    board_economy,
):
    economy, board = board_economy
    board.record(follows_the_rule(FIRST_MEETING))
    day = FIRST_MEETING + timedelta(days=1)

    assert abs(economy.surprise_points(day)) <= 0.125
    assert economy.expected_selic_points(day) == pytest.approx(RULE, abs=0.125)


def test_a_president_who_follows_the_rule_moves_the_stocks_before_the_meeting(
    board_economy,
):
    economy, board = board_economy
    board.record(follows_the_rule(FIRST_MEETING))
    full_effect = math.exp(-layer.STOCKS_PER_SELIC * RULE) - 1

    # A inflação da regra já pesa na bolsa antes da reunião; no dia dela o salto é menos de 1/4 do efeito
    assert economy.level(FIRST_MEETING) - 1 == pytest.approx(full_effect, abs=1e-9)
    assert abs(jump(economy, FIRST_MEETING)) < abs(full_effect) / 4


def test_a_president_two_points_below_the_rule_hits_the_stocks_in_full_on_the_day_it_holds(
    board_economy,
):
    economy, board = board_economy
    board.record(away_from_the_rule(FIRST_MEETING, -2.0))

    assert economy.surprise_points(FIRST_MEETING) == 0.0
    assert economy.surprise_points(FIRST_MEETING + timedelta(days=1)) == pytest.approx(
        -2.0
    )
    assert jump(economy, FIRST_MEETING) == pytest.approx(
        math.exp(layer.STOCKS_PER_SELIC * 2) - 1
    )


def test_keeping_the_same_gap_does_not_jump_on_the_next_meeting(board_economy):
    economy, board = board_economy
    second = FIRST_MEETING + MEETING_SPACING
    board.record(away_from_the_rule(FIRST_MEETING, -2.0))
    board.record(away_from_the_rule(second, -2.0))

    assert jump(economy, second) == pytest.approx(0.0, abs=1e-9)


def test_a_deviation_held_for_a_year_settles_at_the_level_of_the_deviation(
    board_economy,
):
    economy, board = board_economy
    deviation = 3.0
    meeting = FIRST_MEETING
    while meeting < FIRST_MEETING + timedelta(days=365):
        board.record(away_from_the_rule(meeting, deviation - RULE))
        meeting += MEETING_SPACING
    day = FIRST_MEETING + timedelta(days=365)

    expected = math.exp(-layer.STOCKS_PER_SELIC * deviation)
    assert economy.level(day) == pytest.approx(expected, rel=0.10)


def test_without_a_decision_the_market_expects_the_rule(indicators):
    economy = EconomyLayer(1, START, SteadyPressure())

    assert economy.surprise_points(date(2021, 6, 1)) == 0.0
    assert economy.expected_selic_points(date(2021, 6, 1)) == pytest.approx(RULE)


def test_the_gap_of_a_meeting_survives_the_refresh_it_triggers(board_economy):
    economy, board = board_economy
    board.record(away_from_the_rule(FIRST_MEETING, -2.0))
    economy.surprise_points(FIRST_MEETING + timedelta(days=1))

    economy.refresh_from(FIRST_MEETING + timedelta(days=1))
    assert FIRST_MEETING in economy._gaps

    economy.refresh_from(FIRST_MEETING)
    assert economy._gaps == {}


def test_the_focus_series_come_back_untouched(economy):
    history = history_of(IndicatorSeries.SELIC)

    assert economy.adjust(IndicatorSeries.FOCUS_SELIC, history) is history
