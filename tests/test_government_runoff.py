"""Segundo turno com disputa: transferência por grupo, declaração, contribuição, pesquisa semanal e votação."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.dto.promises import PromiseRequest
from backend.core.enum import (
    CampaignActionKind,
    GovernmentNoticeKind,
    MeasureKind,
    PauseReason,
    VoterGroup,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.government import second_round, voters
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_panel
from backend.features.government.state import replay
from tests.test_government_book import (
    ALICE,
    BLUE,
    BOB,
    FIRST_ROUND,
    NICHE,
    RED,
    RUNOFF,
    USERS,
    WORKERS,
    book,
    engine,
    found,
    notices,
    office,
    party_of,
    run_campaign,
    settings,
    stored,
)

GAP = date(2021, 10, 11)
AFTER_FIRST_ROUND = date(2021, 10, 8)


def to_the_gap(book: GovernmentBook) -> None:
    """Alice e o computador vão ao 2º turno; o partido do Bob e um do computador ficam de fora."""
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    assert book.on_tick(USERS, FIRST_ROUND, False) == PauseReason.FIRST_ROUND_RESULT


def request(target: str, kind=MeasureKind.STOCK_PROFIT_RATE) -> PromiseRequest:
    return PromiseRequest(kind=kind, target=Decimal(target))


# Regras


def test_undecided_share_is_half_at_the_half_point_and_falls_with_affinity():
    assert second_round.undecided_share(Decimal(0)) == 1
    assert second_round.undecided_share(Decimal(20)) == Decimal("0.5")
    assert second_round.undecided_share(Decimal(60)) == Decimal(1) / 10


def test_trust_is_affinity_minus_rejection_over_fifty_between_zero_and_one():
    assert second_round.trust(Decimal(70), Decimal(20)) == 1
    assert second_round.trust(Decimal(40), Decimal(15)) == Decimal("0.5")
    assert second_round.trust(Decimal(10), Decimal(30)) == 0


def test_a_contribution_pays_the_difference_of_the_square_root_of_the_party_total():
    first = second_round.contribution_points(Decimal(10000), Decimal(0))
    second = second_round.contribution_points(Decimal(40000), Decimal(10000))

    assert first == voters.campaign_points(Decimal(10000))
    assert first + second == voters.campaign_points(Decimal(40000))


def test_polls_come_the_day_after_the_first_round_and_every_seven_days():
    days = second_round.poll_days(date(2021, 10, 7), date(2021, 10, 27))

    assert days == [date(2021, 10, 8), date(2021, 10, 15), date(2021, 10, 22)]


def test_a_gain_comes_from_the_undecided_first_and_then_from_the_rival():
    race = second_round.GroupRace(
        votes={1: Decimal(40), 2: Decimal(40)},
        undecided=Decimal(20),
        pools={3: Decimal(20)},
        unit=Decimal(1),
    )

    race.shift(1, Decimal(25))

    assert race.votes == {1: Decimal(65), 2: Decimal(35)}
    assert race.undecided == 0

    # Perder apoio devolve os votos aos indecisos
    race.shift(1, Decimal(-10))
    assert race.votes[1] == Decimal(55)
    assert race.undecided == Decimal(10)


# Transferência e disputa


def test_every_group_still_adds_up_to_one_hundred_after_the_transfer(
    book: GovernmentBook,
):
    to_the_gap(book)

    race = book.state.race
    assert race is not None
    for group in VoterGroup:
        disputed = race.groups[group]
        total = sum(disputed.votes.values()) + disputed.undecided
        assert total == pytest.approx(Decimal(100))
        # O indeciso é a soma do que cada eliminado deixou sem dono
        assert disputed.undecided >= sum(disputed.pools.values()) - Decimal("0.0001")


def test_a_first_round_victory_has_no_race(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    assert book.state.race is None


# Declaração de apoio


def test_the_leader_of_an_eliminated_party_endorses_once_and_the_undecided_follow(
    book: GovernmentBook, notices
):
    to_the_gap(book)
    finalist = party_of(book, ALICE).id
    race = book.state.race
    assert race is not None
    votes = {g: race.groups[g].votes[finalist] for g in VoterGroup}
    undecided = {g: race.groups[g].undecided for g in VoterGroup}

    book.endorse(BOB, GAP, finalist)

    assert race.endorsements[party_of(book, BOB).id] == finalist
    assert any(race.groups[g].votes[finalist] > votes[g] for g in VoterGroup)
    assert all(race.groups[g].undecided <= undecided[g] for g in VoterGroup)
    assert notices[-1]["kind"] == GovernmentNoticeKind.ENDORSEMENT.value
    with pytest.raises(ConflictError, match="uma só"):
        book.endorse(BOB, GAP, finalist)


def test_neutrality_leaves_the_undecided_where_they_are(book: GovernmentBook):
    to_the_gap(book)
    race = book.state.race
    assert race is not None
    before = {g: race.groups[g].undecided for g in VoterGroup}

    book.endorse(BOB, GAP, None)

    assert {g: race.groups[g].undecided for g in VoterGroup} == before
    assert book.state.declarations[-1].endorsed_id is None


def test_only_the_leader_of_an_eliminated_party_declares(book: GovernmentBook):
    to_the_gap(book)
    finalist = party_of(book, ALICE).id

    with pytest.raises(ConflictError, match="ficou de fora"):
        book.endorse(ALICE, GAP, finalist)
    with pytest.raises(UnprocessableEntityError, match="finalistas"):
        book.endorse(BOB, GAP, party_of(book, BOB).id)
    with pytest.raises(ConflictError, match=r"véspera|acabou"):
        book.endorse(BOB, RUNOFF, finalist)


def test_the_eliminated_computer_party_declares_on_its_own_the_next_day(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "8000")
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    race = book.state.race
    assert race is not None
    computer = next(
        p for p in book.state.computer_parties() if p.id not in race.finalists
    )

    book.on_tick(USERS, AFTER_FIRST_ROUND, False)

    assert race.endorsements[computer.id] in race.finalists


# Contribuição única


def test_each_member_of_a_finalist_contributes_once(book: GovernmentBook, engine):
    to_the_gap(book)
    mine = party_of(book, ALICE)
    race = book.state.race
    assert race is not None
    cash = engine.get_cash(ALICE.client_id)
    before = race.groups[WORKERS].votes[mine.id]

    book.contribute_runoff(ALICE, GAP, Decimal(9000))

    assert engine.get_cash(ALICE.client_id) == cash - 9000
    assert race.groups[WORKERS].votes[mine.id] > before
    assert book.state.runoff_total(mine.id) == 9000
    with pytest.raises(ConflictError, match="uma só"):
        book.contribute_runoff(ALICE, GAP, Decimal(1))
    with pytest.raises(ConflictError, match="finalista"):
        book.contribute_runoff(BOB, GAP, Decimal(1000))


# Promessas e ações


def test_the_finalist_adds_promises_up_to_four_and_never_takes_them_back(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    book.set_promises(ALICE, date(2020, 11, 2), [request("0.10")])
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    race = book.state.race
    assert race is not None
    kept = request("0.10")
    added = request("0.05", MeasureKind.DAY_TRADE_RATE)

    with pytest.raises(ConflictError, match="só se acrescentam"):
        book.set_promises(ALICE, GAP, [added])

    mine = party_of(book, ALICE)
    before = {g: race.groups[g].votes[mine.id] for g in VoterGroup}
    book.set_promises(ALICE, GAP, [kept, added])

    assert len(mine.promises) == 2
    # A promessa acrescentada rende na hora, para cima ou para baixo conforme o grupo
    assert any(race.groups[g].votes[mine.id] != before[g] for g in VoterGroup)
    with pytest.raises(UnprocessableEntityError, match="No máximo 4"):
        book.set_promises(
            ALICE,
            GAP,
            [kept]
            + [request(f"0.0{n}", MeasureKind.DAY_TRADE_RATE) for n in range(1, 5)],
        )
    with pytest.raises(ConflictError, match="só os finalistas"):
        book.set_promises(BOB, GAP, [kept])


def test_the_attack_in_the_runoff_goes_to_the_other_finalist(book: GovernmentBook):
    to_the_gap(book)
    other = next(f for f in book.state.runoff or [] if f != party_of(book, ALICE).id)

    book.campaign_action(ALICE, GAP, CampaignActionKind.ATTACK, WORKERS, other)
    with pytest.raises(ConflictError, match="outro finalista"):
        book.campaign_action(
            ALICE, GAP, CampaignActionKind.ATTACK, WORKERS, party_of(book, BOB).id
        )


def test_repeating_an_action_counts_again_from_the_day_after_the_first_round(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    book.campaign_action(
        ALICE, FIRST_ROUND - timedelta(days=2), CampaignActionKind.EVENT, WORKERS, None
    )
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)

    mine = party_of(book, ALICE)

    assert book.state.uses(mine.id, CampaignActionKind.EVENT, WORKERS, GAP) == 0


# Calendário entre os turnos


def test_the_poll_comes_every_week_and_the_computer_finalist_campaigns_once(
    book: GovernmentBook,
):
    to_the_gap(book)
    race = book.state.race
    assert race is not None
    computer = next(f for f in race.finalists if book.state.parties[f].is_computer)

    book.on_tick(USERS, AFTER_FIRST_ROUND, False)
    assert len(book.state.race_polls) == 1
    assert book.state.runoff_total(computer) > 0
    spent = book.state.runoff_total(computer)

    book.on_tick(USERS, date(2021, 10, 12), False)
    book.on_tick(USERS, date(2021, 10, 15), False)
    book.on_tick(USERS, date(2021, 10, 22), False)

    assert [p.day for p in book.state.race_polls] == [
        date(2021, 10, 8),
        date(2021, 10, 15),
        date(2021, 10, 22),
    ]
    assert book.state.runoff_total(computer) == spent


# Votação


def test_the_vote_counts_each_group_and_the_undecided_do_not_vote(
    book: GovernmentBook,
):
    to_the_gap(book)
    book.endorse(BOB, GAP, party_of(book, ALICE).id)

    assert book.on_tick(USERS, RUNOFF, False) == PauseReason.RUNOFF_RESULT

    result = book.state.results[-1]
    assert result.round == 2
    assert set(result.groups) == set(VoterGroup)
    assert result.winner_id in result.finalists
    assert result.not_voted == pytest.approx(
        sum(
            (voters.WEIGHTS[g] * gv.undecided for g, gv in result.groups.items()),
            Decimal(0),
        )
    )
    assert book.state.race is None
    assert book.state.declarations == []


def test_replay_rebuilds_the_race_with_declarations_and_contributions(
    book: GovernmentBook, stored
):
    to_the_gap(book)
    book.endorse(BOB, GAP, party_of(book, ALICE).id)
    book.contribute_runoff(ALICE, GAP, Decimal(5000))
    book.campaign_action(ALICE, GAP, CampaignActionKind.EVENT, WORKERS, None)
    book.on_tick(USERS, AFTER_FIRST_ROUND, False)

    again = replay(stored)

    live = book.state.race
    rebuilt = again.race
    assert live is not None and rebuilt is not None
    for group in VoterGroup:
        assert rebuilt.groups[group].votes == live.groups[group].votes
        assert rebuilt.groups[group].undecided == live.groups[group].undecided
    assert rebuilt.endorsements == live.endorsements
    assert len(again.race_polls) == len(book.state.race_polls)


def test_the_panel_shows_the_race_and_what_the_viewer_can_do(book: GovernmentBook):
    to_the_gap(book)
    book.on_tick(USERS, AFTER_FIRST_ROUND, False)

    def panel(user):
        return build_panel(book, settings(), USERS, user, GAP, {})

    race = panel(BOB).runoff_race
    assert race is not None
    assert (race.can_declare, race.can_contribute) == (True, False)
    assert len(race.polls) == 1
    assert race.next_poll == date(2021, 10, 15)
    assert race.transfers
    assert {t.party_id for t in race.transfers}.isdisjoint(race.finalists)

    mine = panel(ALICE).runoff_race
    assert mine is not None
    assert (mine.can_declare, mine.can_contribute, mine.can_add_promise) == (
        False,
        True,
        True,
    )
    assert mine.promise_limit == 4
    assert panel(ALICE).can_donate is False
    assert panel(BOB).can_donate is True
