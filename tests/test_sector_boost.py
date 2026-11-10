"""A alta das ações de um setor: isenção, obra e emenda com endereço, a rampa de 6 meses, o teto do conjunto e a carteira do presidente."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.sector import SectorAllocationDTO, SegmentAllocationDTO
from backend.core.enum import DealStatus
from backend.features.economy.layer import months_to_days
from backend.features.government import sector_boost
from tests.test_deals import make_deal

SINCE = date(2022, 1, 1)


def after(months: float) -> date:
    return SINCE + timedelta(days=months_to_days(months))


def amendment(ratio: str, sector: str | None, segment: str | None = None):
    return make_deal(
        ratio=Decimal(ratio),
        sector=sector,
        segment=segment,
        status=DealStatus.ACTIVE,
        start=SINCE,
        end=date(2025, 12, 31),
        ramp_start=SINCE,
    )


# A rampa


@pytest.mark.parametrize(("months", "share"), [(0, 0.0), (3, 0.5), (6, 1.0), (24, 1.0)])
def test_each_boost_climbs_in_a_straight_line_for_six_months_and_stays(
    months: float, share: float
):
    assert sector_boost.ramp(SINCE, after(months)) == pytest.approx(share, abs=0.01)


def test_the_ramp_is_zero_before_it_starts():
    assert sector_boost.ramp(SINCE, SINCE - timedelta(days=10)) == 0


def test_the_exemption_gives_ten_percent_at_the_end_of_the_ramp():
    assert sector_boost.exemption_boost(SINCE, after(6)) == pytest.approx(0.10)
    assert sector_boost.exemption_boost(None, after(6)) == 0


# A obra com endereço


@pytest.mark.parametrize(
    ("value", "peak"),
    [("0.007", 0.0175), ("0.012", 0.03), ("0.03", 0.075), ("0.05", 0.075)],
)
def test_works_scale_by_two_and_a_half_with_the_ceiling_at_seven_and_a_half_percent(
    value: str, peak: float
):
    assert sector_boost.works_peak(Decimal(value)) == pytest.approx(peak)


def test_works_climb_with_the_ramp_from_the_day_they_pointed_at_the_target():
    works = (SINCE, Decimal("0.012"))

    assert sector_boost.works_boost(works, SINCE) == 0
    assert sector_boost.works_boost(works, after(3)) == pytest.approx(0.015, abs=1e-3)
    assert sector_boost.works_boost(works, after(8)) == pytest.approx(0.03)
    assert sector_boost.works_boost(None, after(8)) == 0


# A emenda com endereço


@pytest.mark.parametrize(
    ("ratio", "peak"), [("0.001", 0.03), ("0.0005", 0.015), ("0.003", 0.06)]
)
def test_an_amendment_scales_by_thirty_with_the_ceiling_at_six_percent(
    ratio: str, peak: float
):
    assert sector_boost.amendment_peak(Decimal(ratio)) == pytest.approx(peak)


def test_an_amendment_counts_only_in_its_sector_and_while_the_deal_covers_the_day():
    deal = amendment("0.001", "Energia")

    full = after(6)
    assert sector_boost.amendment_boost([deal], "Energia", "Geração", full) == (
        pytest.approx(0.03)
    )
    assert sector_boost.amendment_boost([deal], "Bancos", "Bancos", full) == 0
    assert sector_boost.amendment_boost([deal], "Energia", "Geração", SINCE) == 0
    deal.status, deal.end = DealStatus.BROKEN, after(2)
    assert sector_boost.amendment_boost([deal], "Energia", "Geração", full) == 0


def test_an_amendment_with_a_segment_does_not_reach_the_other_segments():
    deal = amendment("0.001", "Energia", "Geração")

    assert sector_boost.amendment_boost([deal], "Energia", "Geração", after(6)) > 0
    assert sector_boost.amendment_boost([deal], "Energia", "Transmissão", after(6)) == 0


def test_several_amendments_in_the_same_sector_add_up():
    deals = [amendment("0.0005", "Energia"), amendment("0.001", "Energia")]

    assert sector_boost.amendment_boost(deals, "Energia", "Geração", after(6)) == (
        pytest.approx(0.045)
    )


# O conjunto


def test_the_three_sources_add_up_and_the_sum_stops_at_twenty_percent():
    assert sector_boost.combined(0.10, 0.03, 0.03) == pytest.approx(0.16)
    assert sector_boost.combined(0.10, 0.075, 0.06) == pytest.approx(0.20)


def test_the_exemption_alone_is_not_changed_by_the_combination():
    assert sector_boost.combined(0.07, 0.0, 0.0) == pytest.approx(0.07)


# O favorecimento


def test_the_favoritism_takes_six_points_per_whole_share_of_the_portfolio():
    assert sector_boost.favoritism_points(Decimal("0.4")) == Decimal("2.4")
    assert sector_boost.favoritism_points(Decimal(0)) == 0


def portfolio() -> PortfolioDTO:
    return PortfolioDTO.model_construct(
        cash=Decimal(500),
        variable_income_value=Decimal(400),
        fixed_income_value=Decimal(100),
        sectors=[
            SectorAllocationDTO(
                sector="Energia",
                value=Decimal(300),
                fraction=Decimal("0.75"),
                segments=[
                    SegmentAllocationDTO(
                        segment="Geração", value=Decimal(200), fraction=Decimal("0.5")
                    ),
                    SegmentAllocationDTO(
                        segment="Transmissão",
                        value=Decimal(100),
                        fraction=Decimal("0.25"),
                    ),
                ],
            ),
            SectorAllocationDTO(
                sector="Bancos",
                value=Decimal(100),
                fraction=Decimal("0.25"),
                segments=[],
            ),
        ],
    )


def test_the_share_is_the_sector_value_over_the_portfolio_at_market_value():
    assert sector_boost.portfolio_share(portfolio(), "Energia", None) == Decimal("0.3")
    assert sector_boost.portfolio_share(portfolio(), "Energia", "Geração") == Decimal(
        "0.2"
    )
    assert sector_boost.portfolio_share(portfolio(), "Mineração", None) == 0


def test_an_empty_portfolio_has_no_share():
    empty = PortfolioDTO.model_construct(
        cash=Decimal(0),
        variable_income_value=Decimal(0),
        fixed_income_value=Decimal(0),
        sectors=[],
    )

    assert sector_boost.portfolio_share(empty, "Energia", None) == 0


# O setor do computador


def test_the_computer_picks_the_sector_from_the_sum_of_the_codes_of_the_acronym():
    sectors = ["Energia", "Bancos", "Varejo"]

    # M(77) + N(78) + V(86) = 241; 241 % 3 = 1, o segundo setor em ordem alfabética
    assert sector_boost.computer_sector("MNV", sectors) == "Energia"
    assert sector_boost.computer_sector("MNV", reversed(sectors)) == "Energia"
    assert sector_boost.computer_sector("MNV", []) is None


def test_the_fraction_for_the_panel_has_four_places():
    assert sector_boost.as_fraction(0.030000000000000002) == Decimal("0.03")
