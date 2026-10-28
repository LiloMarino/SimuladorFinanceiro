"""Eleição da expansão Governo & Política: calendário, intenção de voto pelos grupos, apuração e partidos do computador."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import GameType, PlayerGrouping, VoterGroup, VoterValue
from backend.features.government import election, voters
from backend.features.government.calendar import election_cycle
from backend.features.government.computer_parties import COMPUTER_PARTIES
from backend.features.government.state import GovernmentState, Party, Term
from tests.fakes import simulation_settings

V = VoterValue
MARKET = (V.FREE_MARKET, V.STABILITY, V.SAVER_PROTECTION)
SOCIAL = (V.SOCIAL_JUSTICE, V.STABILITY, V.PUBLIC_SERVICE)
GROWTH = (V.FREE_MARKET, V.DEVELOPMENT, V.PUBLIC_SERVICE)


def party(
    party_id: int,
    flags: tuple[VoterValue, ...] | None = MARKET,
    *,
    members: dict[int, str] | None = None,
    computer: bool = False,
) -> Party:
    return Party(
        id=party_id,
        name=f"Partido {party_id}",
        abbr=f"P{party_id}",
        color=None if computer else "#15803d",
        flags=flags,
        founder_id=None if computer else party_id * 10,
        is_computer=computer,
        founded=date(2020, 10, 7),
        candidate_name="Fulano" if computer else None,
        members={u: Decimal(c) for u, c in (members or {party_id * 10: "0"}).items()}
        if not computer
        else {},
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


def test_spending_early_earns_more_support_than_spending_it_all_at_once():
    early, late = party(1), party(2)
    for _ in range(4):
        early.add_campaign(Decimal(10000))
    late.add_campaign(Decimal(40000))

    group = VoterGroup.FORMAL_WORKERS
    assert early.campaign[group] == 2 * late.campaign[group]


def test_intention_comes_from_the_groups_and_leaves_some_undecided():
    state = state_of(party(1, MARKET), party(2, SOCIAL))

    poll = election.intention(state)

    assert sum(poll.total.values()) + poll.undecided == 100
    assert poll.undecided > 0
    # Investidores preferem o mercado; os assistidos, a justiça social
    investors = poll.groups[VoterGroup.INVESTORS]
    welfare = poll.groups[VoterGroup.WELFARE]
    assert investors.shares[1] > investors.shares[2]
    assert welfare.shares[2] > welfare.shares[1]


def test_party_without_candidate_is_left_out_of_the_intention():
    state = state_of(party(1), party(2, SOCIAL))
    state.term = Term(None, 20, None, date(2022, 1, 1), consecutive=2)

    assert set(election.intention(state).total) == {1}


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


def _first_round(shares: dict[VoterGroup, dict[int, int]]) -> voters.Vote:
    groups = {}
    for group in VoterGroup:
        group_shares = {pid: Decimal(v) for pid, v in shares[group].items()}
        groups[group] = voters.GroupVote(
            group_shares, Decimal(100) - sum(group_shares.values())
        )
    return voters.combine(groups)


def test_eliminated_voters_follow_their_group_and_the_undecided_abstain():
    first_round = _first_round({g: {1: 40, 2: 20, 3: 20} for g in VoterGroup})

    result = election.runoff(first_round, [1, 2])

    assert result.votes == {1: Decimal(50), 2: Decimal(25)}
    assert result.transfers == {3: 1}
    assert result.winner_id == 1
    assert result.shares[1] == Decimal(50) / 75


def test_a_group_starts_satisfied_in_the_share_it_gave_the_winner_of_the_valid_votes():
    shares = {g: {1: 54, 2: 36} for g in VoterGroup}
    shares[VoterGroup.RETIREES] = {1: 20, 2: 60}

    first_round = _first_round(shares)
    start = election.start_satisfaction(first_round, 1)

    # Quem ganhou com 54 de 90 dos votos válidos do grupo começa com 60 nele
    assert start[VoterGroup.WELFARE] == 60
    assert start[VoterGroup.RETIREES] == 25

    # No 2º turno a satisfação sai da divisão entre os dois finalistas
    runoff = election.runoff(first_round, [1, 2])
    assert runoff.satisfaction[VoterGroup.WELFARE] == 60
    assert runoff.satisfaction[VoterGroup.RETIREES] == 25


def test_eliminated_party_transfers_to_the_finalist_that_takes_most_of_its_voters():
    # O partido 3 só tem votos entre os assistidos, onde o 2 é muito mais forte
    shares = {g: {1: 40, 2: 30, 3: 0} for g in VoterGroup}
    shares[VoterGroup.WELFARE] = {1: 10, 2: 50, 3: 30}

    result = election.runoff(_first_round(shares), [1, 2])

    assert result.transfers == {3: 2}


def test_computer_parties_bring_valid_flags_and_fill_the_missing_slots():
    assert all(voters.is_valid_flags(c.flags) for c in COMPUTER_PARTIES)

    state = state_of(party(1, GROWTH))
    first = election.next_computer_party(state)
    assert first is not None and first.abbr == COMPUTER_PARTIES[0].abbr


def test_computer_budget_is_a_multiple_of_the_average_player_party():
    state = state_of(
        party(1, members={10: "6000", 11: "2000"}), party(2, members={20: "8000"})
    )

    assert election.computer_spend(state, Decimal("1.5")) == Decimal(12000)
    assert election.computer_spend(state_of(), Decimal(1)) == Decimal(0)


def test_second_term_president_cannot_run_again():
    state = state_of(party(1))
    state.term = Term(1, 10, None, date(2022, 1, 1), consecutive=2)

    assert not election.is_eligible(state, 10)
    assert election.is_eligible(state, 11)
    assert election.effective_ticket(state, state.parties[1]) == (None, None)


def test_party_without_chosen_ticket_runs_with_the_founder():
    state = state_of(party(1, members={10: "0", 11: "0"}))

    assert election.effective_ticket(state, state.parties[1]) == (10, None)


def test_pending_vice_does_not_run():
    chosen = party(1, members={10: "0", 11: "0"})
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
