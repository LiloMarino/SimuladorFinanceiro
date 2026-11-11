from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import (
    CampaignActionKind,
    DiceBand,
    MeasureKind,
    NewsType,
    VoterGroup,
)
from backend.features.government import headlines

SEEDS = [(1, date(2020, 1, 1), n) for n in range(60)]
SEED = SEEDS[0]


def across(build):
    """O mesmo fato lido com várias sementes: as redações que o jornal pode usar."""
    return [build(seed) for seed in SEEDS]


def variants(build):
    return {h.text for h in across(build)}


def test_the_closed_tickets_name_who_runs_without_a_vice():
    closed = across(
        lambda seed: headlines.tickets_closed(
            [("AAA", "Alice", "Bob"), ("NOVO", "Dr. Paulo", None)], 63, seed=seed
        )
    )

    for headline in closed:
        assert "Alice e Bob" in headline.text and "Dr. Paulo" in headline.text
        assert headline.dek is not None
        assert "NOVO concorre sem vice" in headline.dek
        assert "63 dias" in headline.dek


def test_a_headline_carries_the_parties_it_cites_in_the_order_of_the_text():
    runoff = headlines.runoff_called(
        [("AAA", Decimal("0.41")), ("NOVO", Decimal("0.33"))],
        date(2021, 10, 31),
        seed=SEED,
    )
    turned = headlines.round_won(2, "Bia", "FDS", Decimal("0.52"), "AAA", seed=SEED)
    attack = headlines.campaign_action(
        CampaignActionKind.ATTACK,
        DiceBand.VIRAL,
        "AAA",
        VoterGroup.RETIREES,
        "NOVO",
        seed=SEED,
    )
    closed = headlines.tickets_closed(
        [("AAA", "Alice", "Bob"), ("NOVO", "Dr. Paulo", None)], 63, seed=SEED
    )
    requested = headlines.impeachment_requested(
        "Bia", "FDS", date(2021, 5, 3), "AAA", seed=SEED
    )
    floor = headlines.impeachment_requested("Bia", "FDS", date(2021, 5, 3), seed=SEED)

    assert runoff.party_abbrs == ("AAA", "NOVO")
    assert turned.party_abbrs == ("FDS", "AAA")
    assert attack is not None and attack.party_abbrs == ("AAA", "NOVO")
    assert closed.party_abbrs == ("AAA", "NOVO")
    assert requested.party_abbrs == ("AAA", "FDS")
    assert floor.party_abbrs == ("FDS",)
    opened = headlines.campaign_opened(date(2021, 10, 3), date(2021, 8, 1), seed=SEED)
    assert opened.party_abbrs == ()


def test_the_round_result_carries_the_share_of_the_valid_votes():
    won = across(
        lambda seed: headlines.round_won(
            1, "Alice", "AAA", Decimal("0.5234"), seed=seed
        )
    )
    runoff = across(
        lambda seed: headlines.runoff_called(
            [("AAA", Decimal("0.41")), ("NOVO", Decimal("0.33"))],
            date(2021, 10, 31),
            seed=seed,
        )
    )

    for headline in won:
        assert "Alice" in headline.text and "AAA" in headline.text
        assert "52,3%" in headline.text
        assert headline.news_type is NewsType.ELECTION_RESULT
    for headline in runoff:
        assert "AAA" in headline.text and "NOVO" in headline.text
        assert "2º turno" in headline.text
        assert headline.dek is not None
        assert "31/10" in headline.dek


@pytest.mark.parametrize(
    ("kind", "band", "group", "rival", "tokens"),
    [
        (CampaignActionKind.RALLY, DiceBand.GOOD, VoterGroup.RETIREES, None, None),
        (
            CampaignActionKind.RALLY,
            DiceBand.VIRAL,
            VoterGroup.RETIREES,
            None,
            ("AAA", "aposentados"),
        ),
        (CampaignActionKind.TV, DiceBand.DISASTER, None, None, ("AAA", "TV")),
        (
            CampaignActionKind.ATTACK,
            DiceBand.GOOD,
            VoterGroup.WELFARE,
            "NOVO",
            ("AAA", "NOVO", "auxílio"),
        ),
        (
            CampaignActionKind.ATTACK,
            DiceBand.DISASTER,
            VoterGroup.INVESTORS,
            "NOVO",
            ("AAA", "NOVO", "investidores"),
        ),
    ],
)
def test_the_journal_gets_the_action_that_stands_out_and_every_attack(
    kind, band, group, rival, tokens
):
    built = across(
        lambda seed: headlines.campaign_action(
            kind, band, "AAA", group, rival, seed=seed
        )
    )

    if tokens is None:
        assert built == [None] * len(SEEDS)
        return
    for headline in built:
        assert headline is not None
        assert headline.news_type is NewsType.CAMPAIGN_ACTION
        assert all(token in headline.text for token in tokens)


def test_the_promises_headline_follows_the_list():
    withdrawn = across(lambda seed: headlines.promises_set("AAA", 0, True, seed=seed))
    revised = across(lambda seed: headlines.promises_set("AAA", 1, True, seed=seed))

    for headline in withdrawn:
        assert "AAA" in headline.text and "promessas" in headline.text
    for headline in revised:
        assert "AAA" in headline.text
        assert headline.dek is not None and "1 promessa" in headline.dek


def test_impeachment_without_a_vice_names_the_computer_party_that_takes_office():
    for ousted in across(
        lambda seed: headlines.impeachment("Bia", "FDS", None, 70, 31, "UPR", seed=seed)
    ):
        assert "Bia" in ousted.text and "FDS" in ousted.text
        assert "70 a 31" in ousted.text and "UPR" in ousted.text
        assert ousted.dek is not None and "UPR" in ousted.dek


def test_the_turnaround_names_who_led_the_first_round_and_lost():
    turned = across(
        lambda seed: headlines.round_won(
            2, "Bia", "FDS", Decimal("0.52"), "AAA", seed=seed
        )
    )
    plain = across(
        lambda seed: headlines.round_won(2, "Bia", "FDS", Decimal("0.52"), seed=seed)
    )

    for headline in turned:
        assert "Bia" in headline.text and "52%" in headline.text
        assert headline.dek is not None and "AAA" in headline.dek
    for headline in plain:
        assert "Bia" in headline.text


def test_the_house_taking_office_names_the_biggest_bloc_and_the_government_bench():
    seated = across(
        lambda seed: headlines.house_seated(
            ("MRC", 38), 101, ("AAA", 21), 51, seed=seed
        )
    )
    neutral = across(
        lambda seed: headlines.house_seated(("MRC", 38), 101, None, 51, seed=seed)
    )

    for headline in seated:
        assert headline.news_type is NewsType.TERM_STARTED
        assert "MRC" in headline.text and "38" in headline.text
        assert headline.dek is not None
        assert "AAA" in headline.dek and "21" in headline.dek and "51" in headline.dek
    assert all(headline.dek is None for headline in neutral)


def test_a_deal_made_tells_where_the_base_stands():
    for made in across(
        lambda seed: headlines.deal_made(
            "Alice", "UPR", 16, 40, 51, date(2025, 12, 31), seed=seed
        )
    ):
        assert made.news_type is NewsType.PARTY_LIFE
        assert "UPR" in made.text and "Alice" in made.text
        assert made.dek is not None
        assert "40" in made.dek and "abaixo da maioria de 51" in made.dek
        assert "até 31/12/2025" in made.dek


def test_a_bloc_leaving_for_approval_has_no_culprit_and_tells_where_the_base_stands():
    for left in across(
        lambda seed: headlines.deal_left("Alice", "PP", 12, 38, 51, seed=seed)
    ):
        assert left.news_type is NewsType.PARTY_RUPTURE
        assert "PP" in left.text
        assert left.dek is not None
        assert "38" in left.dek and "abaixo da maioria de 51" in left.dek


def test_a_spending_vote_says_whether_spending_rises_and_what_inflation_does():
    def vote(kind, title, approved, effective, peak, yes, no, defected):
        return across(
            lambda seed: headlines.spending_voted(
                kind, title, approved, effective, peak, 6, yes, no, defected, seed=seed
            )
        )

    approved = vote(
        MeasureKind.WELFARE_SPENDING,
        "Auxílio: 2% do PIB",
        True,
        date(2022, 2, 1),
        Decimal("0.5"),
        60,
        41,
        2,
    )
    cut = vote(
        MeasureKind.PUBLIC_WORKS,
        "Obras: 1% do PIB",
        True,
        None,
        Decimal("-0.15"),
        55,
        46,
        0,
    )
    barred = vote(
        MeasureKind.SERVANT_RAISE,
        "Servidores: reajuste de 1% acima da inflação",
        False,
        None,
        Decimal("0.2"),
        40,
        61,
        0,
    )

    for headline in approved:
        assert "60 a 41" in headline.text and "Auxílio: 2% do PIB" in headline.text
        assert headline.dek is not None
        assert "Vale a partir de 01/02/2022." in headline.dek
        assert "0,5 ponto" in headline.dek and "6 meses" in headline.dek
    for headline in cut:
        assert "55 a 46" in headline.text
        assert headline.dek is not None
        assert "0,15 ponto" in headline.dek and "6 meses" in headline.dek
    for headline in barred:
        assert "61 a 40" in headline.text
        assert headline.dek is not None and "40 a 61" in headline.dek


def test_a_spending_measure_in_force_tells_when_the_inflation_effect_peaks():
    for in_force in across(
        lambda seed: headlines.spending_in_force(
            "Auxílio: 2% do PIB", Decimal("0.5"), 6, seed=seed
        )
    ):
        assert "Auxílio: 2% do PIB" in in_force.text
        assert in_force.dek is not None
        assert "6 meses" in in_force.dek
        assert "0,5 ponto" in in_force.dek


def test_going_back_on_a_promise_names_what_was_given_up():
    def promises(count, retreated):
        return across(
            lambda seed: headlines.promises_set(
                "AAA", count, True, retreated, seed=seed
            )
        )

    for one in promises(1, ["Ações: IR das vendas com lucro em 10%"]):
        assert "AAA" in one.text and "uma promessa" in one.text
        assert one.dek is not None
        assert "Ações: IR das vendas com lucro em 10%" in one.dek
    for none in promises(0, ["Obras: 1% do PIB"]):
        assert none.dek is not None and "Obras: 1% do PIB" in none.dek
    for two in promises(1, ["A", "B"]):
        assert "2 promessas" in two.text


def test_the_campaign_opening_has_its_own_window_type_and_the_rest_of_the_calendar_is_configurable():
    opened = headlines.campaign_opened(date(2022, 10, 2), date(2022, 9, 30), seed=SEED)
    closing = headlines.tickets_closing(date(2022, 9, 30), seed=SEED)
    eve = headlines.election_eve(date(2022, 10, 2), seed=SEED)

    assert opened.news_type is NewsType.CAMPAIGN_OPENED
    assert closing.news_type is NewsType.ELECTION_CALENDAR
    assert eve.news_type is NewsType.ELECTION_CALENDAR


def test_the_rare_events_have_their_own_types():
    attack = headlines.campaign_action(
        CampaignActionKind.ATTACK,
        DiceBand.DISASTER,
        "AAA",
        VoterGroup.INVESTORS,
        "NOVO",
        seed=SEED,
    )
    named = headlines.spending_in_force(
        "Auxílio: 2% do PIB", Decimal("0.5"), 6, "Bolsa Família", seed=SEED
    )
    plain = headlines.spending_in_force(
        "Auxílio: 2% do PIB", Decimal("0.5"), 6, seed=SEED
    )

    assert attack is not None and attack.news_type is NewsType.CAMPAIGN_ACTION
    assert named.news_type is NewsType.NAMED_PROGRAM
    assert plain.news_type is not NewsType.NAMED_PROGRAM
    expelled = headlines.expelled("Alice", "AAA", seed=SEED)
    left = headlines.federation_left("AAA", "NOVO", seed=SEED)
    founded = headlines.party_founded("Alice", "AAA", "Partido A", seed=SEED)
    assert expelled.news_type is NewsType.PARTY_RUPTURE
    assert left.news_type is NewsType.PARTY_RUPTURE
    assert founded.news_type is NewsType.PARTY_LIFE


FACTS = {
    "campaign_opened": lambda seed: headlines.campaign_opened(
        date(2022, 10, 2), date(2022, 9, 30), seed=seed
    ),
    "tickets_closing": lambda seed: headlines.tickets_closing(
        date(2022, 9, 30), seed=seed
    ),
    "tickets_closed": lambda seed: headlines.tickets_closed(
        [("AAA", "Alice", "Bob"), ("NOVO", "Dr. Paulo", None)], 63, seed=seed
    ),
    "election_eve": lambda seed: headlines.election_eve(date(2022, 10, 2), seed=seed),
    "round_won": lambda seed: headlines.round_won(
        1, "Alice", "AAA", Decimal("0.52"), seed=seed
    ),
    "round_won_turned": lambda seed: headlines.round_won(
        2, "Alice", "AAA", Decimal("0.52"), "NOVO", seed=seed
    ),
    "runoff_called": lambda seed: headlines.runoff_called(
        [("AAA", Decimal("0.41")), ("NOVO", Decimal("0.33"))],
        date(2021, 10, 31),
        seed=seed,
    ),
    "impeachment_requested": lambda seed: headlines.impeachment_requested(
        "Bia", "FDS", date(2021, 5, 3), "AAA", seed=seed
    ),
    "impeachment_rejected": lambda seed: headlines.impeachment_rejected(
        "Bia", "FDS", 30, 60, "AAA", seed=seed
    ),
    "impeachment": lambda seed: headlines.impeachment(
        "Bia", "FDS", "Caio", 70, 31, None, seed=seed
    ),
    "term_started": lambda seed: headlines.term_started(
        "Bia", "FDS", date(2026, 1, 1), seed=seed
    ),
    "legacy_paid": lambda seed: headlines.legacy_paid(
        "Bia", "FDS", Decimal("1000"), 60, seed=seed
    ),
    "house_seated": lambda seed: headlines.house_seated(
        ("MRC", 38), 101, ("AAA", 21), 51, seed=seed
    ),
    "measure_proposed": lambda seed: headlines.measure_proposed(
        "Bia", "Ações: IR em 10%", seed=seed
    ),
    "measure_withdrawn": lambda seed: headlines.measure_withdrawn(
        "Bia", "Ações: IR em 10%", seed=seed
    ),
    "measure_voted": lambda seed: headlines.measure_voted(
        "Ações: IR em 10%", True, date(2022, 2, 1), ["WEGE3"], 60, 41, 2, seed=seed
    ),
    "spending_voted": lambda seed: headlines.spending_voted(
        MeasureKind.WELFARE_SPENDING,
        "Auxílio: 2% do PIB",
        True,
        date(2022, 2, 1),
        Decimal("0.5"),
        6,
        60,
        41,
        2,
        seed=seed,
    ),
    "spending_in_force": lambda seed: headlines.spending_in_force(
        "Auxílio: 2% do PIB", Decimal("0.5"), 6, seed=seed
    ),
    "measure_in_force": lambda seed: headlines.measure_in_force(
        "Ações: IR em 10%", ["WEGE3"], seed=seed
    ),
    "party_founded": lambda seed: headlines.party_founded(
        "Alice", "AAA", "Partido A", seed=seed
    ),
    "donation": lambda seed: headlines.donation(
        "Alice", "AAA", Decimal("500"), seed=seed
    ),
    "expelled": lambda seed: headlines.expelled("Alice", "AAA", seed=seed),
    "federation_formed": lambda seed: headlines.federation_formed(
        "AAA", "NOVO", "Alice", date(2026, 1, 1), seed=seed
    ),
    "federation_left": lambda seed: headlines.federation_left("AAA", "NOVO", seed=seed),
    "deal_made": lambda seed: headlines.deal_made(
        "Alice", "UPR", 16, 40, 51, date(2025, 12, 31), seed=seed
    ),
    "deal_broken": lambda seed: headlines.deal_broken(
        "Alice",
        "AAA",
        "UPR",
        True,
        False,
        16,
        40,
        51,
        [VoterGroup.RETIREES],
        seed=seed,
    ),
    "deal_left": lambda seed: headlines.deal_left("Alice", "PP", 12, 38, 51, seed=seed),
    "deals_ended": lambda seed: headlines.deals_ended(["AAA", "NOVO"], True, seed=seed),
    "campaign_action": lambda seed: headlines.campaign_action(
        CampaignActionKind.ATTACK,
        DiceBand.VIRAL,
        "AAA",
        VoterGroup.RETIREES,
        "NOVO",
        seed=seed,
    ),
    "promises_set": lambda seed: headlines.promises_set("AAA", 2, False, seed=seed),
    "promises_settled": lambda seed: headlines.promises_settled("AAA", 2, 3, seed=seed),
    "endorsement": lambda seed: headlines.endorsement("AAA", "NOVO", seed=seed),
}


@pytest.mark.parametrize("name", FACTS)
def test_each_headline_has_three_wordings_chosen_by_the_seed(name):
    build = FACTS[name]

    assert len(variants(build)) == 3
    assert build(SEED) == build(SEED)


def test_program_event_has_three_wordings_per_case():
    for before, after in (
        (None, "Bolsa Família"),
        ("Bolsa Família", "Auxílio Brasil"),
        ("Bolsa Família", None),
    ):
        texts = {headlines.program_event(before, after, seed=seed) for seed in SEEDS}
        assert len(texts) == 3
        assert None not in texts
    assert headlines.program_event("Bolsa Família", "Bolsa Família", seed=SEED) is None
