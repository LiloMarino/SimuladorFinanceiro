"""Os acordos de apoio por emenda: preço da cadeira, resposta do computador, grupos atingidos e prazo."""

from datetime import date
from decimal import Decimal

from backend.core.enum import DealStatus, VoterGroup, VoterValue
from backend.features.government import deals

STABILITY, DEVELOPMENT, PUBLIC_SERVICE = (
    VoterValue.STABILITY,
    VoterValue.DEVELOPMENT,
    VoterValue.PUBLIC_SERVICE,
)


def make_deal(**fields) -> deals.Deal:
    base = dict(
        id=1,
        bloc_key=-1,
        party_id=None,
        abbr="ACI",
        seats=10,
        ratio=Decimal("0.0005"),
        proposed=date(2022, 3, 1),
        proposer_id=1,
    )
    return deals.Deal(**{**base, **fields})


def test_a_seat_costs_five_thousandths_of_a_percent_of_gdp_a_year():
    assert deals.price("ACI", 10) == Decimal("0.0005")
    assert deals.price("ACI", 0) == 0


def test_the_centrao_charges_one_and_a_half_times():
    assert deals.price(deals.CENTRAO, 10) == Decimal("0.00075")


def test_the_centrao_always_accepts_and_the_others_need_two_shared_flags():
    government = (STABILITY, DEVELOPMENT, PUBLIC_SERVICE)
    assert deals.computer_accepts(deals.CENTRAO, (), government)
    assert deals.computer_accepts("MNV", (DEVELOPMENT, PUBLIC_SERVICE), government)
    assert not deals.computer_accepts("ACI", (STABILITY,), government)
    assert not deals.computer_accepts("ACI", None, government)


def test_the_strongest_group_takes_the_full_weight_and_the_others_a_share():
    mix = {g: Decimal(0) for g in VoterGroup}
    mix[VoterGroup.RETIREES] = Decimal("0.4")
    mix[VoterGroup.PUBLIC_SERVANTS] = Decimal("0.2")

    weights = deals.group_weights(mix)

    assert weights[VoterGroup.RETIREES] == 1
    assert weights[VoterGroup.PUBLIC_SERVANTS] == Decimal("0.5")
    assert weights[VoterGroup.INVESTORS] == 0
    assert deals.strongest_groups(mix) == [
        VoterGroup.RETIREES,
        VoterGroup.PUBLIC_SERVANTS,
    ]
    assert deals.break_rejection(mix)[VoterGroup.RETIREES] == deals.BREAK_REJECTION
    assert deals.month_support(mix)[VoterGroup.PUBLIC_SERVANTS] == Decimal("0.5")


def test_a_bloc_without_a_mix_weighs_every_group_the_same():
    weights = deals.group_weights({})

    assert set(weights.values()) == {Decimal(1)}


def test_the_deal_lasts_six_months_or_until_the_eve_of_the_new_congress():
    assert deals.last_day(date(2022, 3, 15), None) == date(2022, 9, 14)
    assert deals.last_day(date(2022, 8, 31), None) == date(2023, 2, 27)
    assert deals.last_day(date(2022, 3, 15), date(2022, 6, 30)) == date(2022, 6, 30)


def test_a_declined_proposal_waits_thirty_days():
    assert deals.retry_from(date(2022, 3, 1)) == date(2022, 3, 31)


def test_the_deal_covers_its_term_and_only_the_active_one_is_in_force():
    deal = make_deal(
        status=DealStatus.ACTIVE, start=date(2022, 3, 2), end=date(2022, 9, 1)
    )

    assert deal.covers(date(2022, 3, 2)) and deal.covers(date(2022, 9, 1))
    assert not deal.covers(date(2022, 9, 2))
    assert deal.in_force(date(2022, 5, 1))

    deal.status = DealStatus.BROKEN
    assert deal.covers(date(2022, 5, 1))
    assert not deal.in_force(date(2022, 5, 1))


def test_a_proposal_that_was_not_answered_pays_nothing():
    pending = make_deal()

    assert not pending.covers(date(2022, 4, 1))
    assert deals.amendments([pending], date(2022, 4, 1)) == 0


def test_amendments_add_up_the_deals_that_covered_the_reference_day():
    first = make_deal(
        status=DealStatus.ACTIVE, start=date(2022, 3, 2), end=date(2022, 9, 1)
    )
    second = make_deal(
        id=2,
        ratio=Decimal("0.001"),
        status=DealStatus.ACTIVE,
        start=date(2022, 5, 1),
        end=date(2022, 10, 31),
    )

    assert deals.amendments([first, second], date(2022, 4, 1)) == Decimal("0.0005")
    assert deals.amendments([first, second], date(2022, 6, 1)) == Decimal("0.0015")
    assert deals.amendments([first, second], date(2022, 12, 1)) == 0


def test_a_deal_with_no_answer_deadline_is_the_computers():
    assert make_deal().is_computer
    assert not make_deal(answer_by=date(2022, 3, 16)).is_computer
