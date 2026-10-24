"""Eleição da expansão Governo & Política: calendário, apoio pela raiz quadrada, apuração e partidos do computador."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping
from backend.features.government import election
from backend.features.government.calendar import election_cycle
from backend.features.government.state import GovernmentState, Party, Term, vote_points
from tests.fakes import simulation_settings


def party(
    party_id: int,
    promise: int,
    points: str = "0",
    *,
    members: dict[int, str] | None = None,
    computer: bool = False,
) -> Party:
    return Party(
        id=party_id,
        name=f"Partido {party_id}",
        abbr=f"P{party_id}",
        color=None if computer else "#15803d",
        promise=promise,
        founder_id=None if computer else party_id * 10,
        is_computer=computer,
        founded=date(2020, 10, 7),
        candidate_name="Fulano" if computer else None,
        members={u: Decimal(c) for u, c in (members or {party_id * 10: "0"}).items()}
        if not computer
        else {},
        points=Decimal(points),
    )


def state_of(*parties: Party) -> GovernmentState:
    return GovernmentState(
        parties={p.id: p for p in parties}, next_party_id=len(parties) + 1
    )


def test_cycle_moves_a_non_business_first_round_to_the_next_business_day():
    cycle = election_cycle(date(2018, 10, 7), 0, date(2016, 1, 4))

    assert cycle.first_round == date(2018, 10, 8)  # 7/out/2018 é domingo
    assert cycle.runoff == date(2018, 10, 29)
    assert cycle.ticket_deadline == date(2018, 9, 30)
    assert cycle.campaign_start == date(2017, 10, 8)
    assert cycle.inauguration == date(2019, 1, 1)
    assert cycle.donation_deadline == date(2018, 10, 28)


def test_next_election_is_four_years_later():
    cycle = election_cycle(date(2018, 10, 7), 1, date(2016, 1, 4))

    assert cycle.first_round == date(2022, 10, 7)
    assert cycle.runoff == date(2022, 10, 28)


def test_campaign_never_opens_before_the_match_starts():
    cycle = election_cycle(date(2021, 3, 10), 0, date(2020, 6, 1))

    assert cycle.campaign_start == date(2020, 6, 1)


def test_spending_early_earns_more_votes_than_spending_it_all_at_once():
    four_months = 4 * vote_points(Decimal(10000))
    one_month = vote_points(Decimal(40000))

    assert four_months == Decimal("6.25")
    assert one_month == Decimal("3.125")


def test_doubling_the_budget_does_not_double_the_points():
    assert vote_points(Decimal(8000)).quantize(Decimal("0.1")) == Decimal("1.4")
    assert vote_points(Decimal(16000)).quantize(Decimal("0.1")) == Decimal("2.0")


def test_valid_votes_leave_out_the_undecided():
    state = state_of(party(1, 5, "33"), party(2, 3, "32"), party(3, 2, "23"))

    poll = election.intention(state)

    assert poll.undecided == Decimal(12)
    assert poll.valid_shares[1] == Decimal("0.375")


def test_points_beyond_the_electorate_are_scaled_down():
    state = state_of(party(1, 1, "120"), party(2, 5, "80"))

    poll = election.intention(state)

    assert sum(poll.points.values()) == Decimal(100)
    assert poll.undecided == Decimal(0)


def test_first_round_needs_more_than_half_of_the_valid_votes():
    assert (
        election.first_round_winner(
            election.valid_shares({1: Decimal(51), 2: Decimal(49)})
        )
        == 1
    )
    assert (
        election.first_round_winner(
            election.valid_shares({1: Decimal(50), 2: Decimal(50)})
        )
        is None
    )


def test_voters_of_the_eliminated_party_go_to_the_closest_promise():
    # PRL (promessa 2) saiu: o FDS (3) está mais perto que o UPR (5)
    state = state_of(party(1, 5), party(2, 3), party(3, 2))
    points = {1: Decimal(33), 2: Decimal(32), 3: Decimal(23)}

    result = election.runoff(state, points, [1, 2])

    assert result.transfers == {3: 2}
    assert result.votes == {1: Decimal(33), 2: Decimal(55)}
    assert result.winner_id == 2


def test_runoff_tie_in_distance_goes_to_the_party_with_more_votes():
    state = state_of(party(1, 1), party(2, 5), party(3, 3))
    points = {1: Decimal(30), 2: Decimal(35), 3: Decimal(10)}

    assert election.runoff(state, points, [1, 2]).transfers == {3: 2}


def test_computer_takes_the_band_farthest_from_every_party():
    existing = [party(1, 3, members={10: "0"})]

    assert election.pick_promise(existing) == 1

    existing.append(party(2, 1, computer=True))
    assert election.pick_promise(existing) == 5


def test_computer_budget_is_a_multiple_of_the_average_player_party():
    state = state_of(
        party(1, 1, members={10: "6000", 11: "2000"}), party(2, 2, members={20: "8000"})
    )

    assert election.computer_spend(state, Decimal("1.5")) == Decimal(12000)
    assert election.computer_spend(state_of(), Decimal(1)) == Decimal(0)


def test_second_term_president_cannot_run_again():
    state = state_of(party(1, 3))
    state.term = Term(1, 10, None, date(2022, 1, 1), consecutive=2)

    assert not election.is_eligible(state, 10)
    assert election.is_eligible(state, 11)
    assert election.effective_ticket(state, state.parties[1]) == (None, None)


def test_party_without_chosen_ticket_runs_with_the_founder():
    state = state_of(party(1, 3, members={10: "0", 11: "0"}))

    assert election.effective_ticket(state, state.parties[1]) == (10, None)


def test_pending_vice_does_not_run():
    chosen = party(1, 3, members={10: "0", 11: "0"})
    chosen.candidate_id, chosen.vice_id = 10, 11

    state = state_of(chosen)
    assert election.effective_ticket(state, chosen) == (10, None)

    chosen.vice_accepted = True
    assert election.effective_ticket(state, chosen) == (10, 11)


def _rules(**overrides) -> SimulationSettingsDTO:
    base = simulation_settings().model_dump()
    base.update(
        start_date=date(2020, 1, 1),
        end_date=date(2025, 12, 31),
        government_enabled=True,
        first_election=date(2021, 10, 7),
    )
    base.update(overrides)
    return SimulationSettingsDTO(**base)


def test_expansion_needs_five_years_or_more():
    _rules()
    with pytest.raises(ValidationError, match="5 anos"):
        _rules(end_date=date(2024, 12, 31))


def test_first_election_must_fall_inside_the_match():
    with pytest.raises(ValidationError, match="primeira eleição"):
        _rules(first_election=date(2026, 10, 7))
    with pytest.raises(ValidationError, match="primeira eleição"):
        _rules(first_election=None)


def test_political_victory_needs_the_expansion_and_individual_mode():
    with pytest.raises(ValidationError, match="exige a expansão"):
        _rules(game_type=GameType.POLITICAL, government_enabled=False)
    with pytest.raises(ValidationError, match="individual"):
        _rules(game_type=GameType.POLITICAL, player_grouping=PlayerGrouping.TEAMS)
    assert _rules(game_type=GameType.POLITICAL).game_type is GameType.POLITICAL
