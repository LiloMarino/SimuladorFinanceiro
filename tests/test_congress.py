"""O Congresso no livro do governo: a casa eleita, a orientação do líder, a votação e o impeachment votado."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.enum import PauseReason, PendingType, VoterValue
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.government import governance, house
from backend.features.government.governance import build_governance
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from tests.test_government_book import (
    ALICE,
    BOB,
    CAMPAIGN_OPEN,
    FIRST_VOTE,
    RED,
    TERM_START,
    USERS,
    bleak,
    book,
    close_months,
    engine,
    found,
    govern,
    headlines,
    market,
    notices,
    office,
    party_of,
    propose,
    settings,
    stored,
)

QUEUED_DAY = date(2022, 1, 20)


def votes_say(monkeypatch: pytest.MonkeyPatch, yes: int) -> None:
    """A casa conta `yes` votos Sim em toda votação, sem detalhar as bancadas."""
    monkeypatch.setattr(
        house,
        "count",
        lambda *_: house.Tally(yes, house.SEATS - yes, {}),
    )


def alice_bloc(book: GovernmentBook) -> house.Bloc:
    bloc = book.state.house_on(TERM_START).of_party(party_of(book, ALICE).id)
    assert bloc is not None
    return bloc


# A casa eleita


def test_the_first_round_elects_a_house_that_takes_office_with_the_president(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    elected = book.state.elected_house()
    assert elected is not None
    assert sum(b.seats for b in elected.house.blocs) == house.SEATS
    assert elected.takes_office <= TERM_START
    # Antes da posse vale a casa do computador; depois, a eleita
    assert all(b.is_computer for b in book.state.house_on(elected.day).blocs)
    assert book.state.house_on(TERM_START) == elected.house
    assert alice_bloc(book).seats > 0


def test_the_three_computer_parties_always_sit_in_the_house(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    keys = {b.key for b in book.state.house_on(TERM_START).blocs}
    assert set(house.COMPUTER_KEYS.values()) <= keys


def test_a_resumed_game_rebuilds_the_same_house_and_guidance(
    book: GovernmentBook, engine, market, stored
):
    govern(book, engine)
    propose(book)
    book.guide(ALICE, QUEUED_DAY, 1, False)

    rebuilt = replay(stored)

    assert rebuilt.houses == book.state.houses
    assert rebuilt.orientations == book.state.orientations


# Orientação do líder


def test_only_the_leader_guides_the_bloc_until_the_eve_of_the_vote(
    book: GovernmentBook, engine, market
):
    govern(book, engine, vice=True)
    propose(book)

    with pytest.raises(ForbiddenError):
        book.guide(BOB, QUEUED_DAY, 1, True)
    book.guide(ALICE, QUEUED_DAY, 1, True)
    with pytest.raises(ConflictError, match="véspera"):
        book.guide(ALICE, FIRST_VOTE, 1, True)


def test_a_guided_bloc_follows_the_leader_and_an_unguided_one_follows_the_default(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book)
    measure = book.state.measures[1]
    key = alice_bloc(book).key

    _, guided, _ = book.measure_orientations(measure, QUEUED_DAY)
    assert guided[key] is False

    book.guide(ALICE, QUEUED_DAY, 1, False)
    orientations, guided, _ = book.measure_orientations(measure, QUEUED_DAY)
    assert (orientations[key], guided[key]) == (False, True)
    book.guide(ALICE, QUEUED_DAY, 1, True)
    orientations, _, _ = book.measure_orientations(measure, QUEUED_DAY)
    assert orientations[key] is True


def test_the_computer_blocs_vote_by_their_own_flags_without_a_leader(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book)

    _, guided, _ = book.measure_orientations(book.state.measures[1], QUEUED_DAY)

    computers = [k for k in guided if k < 0]
    assert computers
    assert not any(guided[k] for k in computers)


def test_the_leader_changes_the_default_guidance_by_value(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    party = party_of(book, ALICE)
    assert party.rules[VoterValue.FREE_MARKET] is False

    book.set_guidance_rule(ALICE, TERM_START, VoterValue.FREE_MARKET, True)

    assert party.rules[VoterValue.FREE_MARKET] is True
    assert party.rules[VoterValue.STABILITY] is True


def test_a_member_who_is_not_the_leader_cannot_change_the_default_guidance(
    book: GovernmentBook, engine, market
):
    govern(book, engine, vice=True)

    with pytest.raises(ForbiddenError):
        book.set_guidance_rule(BOB, TERM_START, VoterValue.FREE_MARKET, True)


def test_the_unguided_vote_is_a_pending_for_the_leader_until_the_bloc_is_guided(
    book: GovernmentBook, engine, market
):
    govern(book, engine, vice=True)
    propose(book)

    def types(user, day=QUEUED_DAY):
        return [p.type for p in book.pending(user, day)]

    assert PendingType.UNGUIDED_VOTE in types(ALICE)
    assert PendingType.UNGUIDED_VOTE not in types(BOB)

    book.guide(ALICE, QUEUED_DAY, 1, True)

    assert PendingType.UNGUIDED_VOTE not in types(ALICE)


# Votação


def test_the_house_votes_the_queue_by_seats_and_a_majority_of_51_passes(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    votes_say(monkeypatch, house.MAJORITY)

    book.on_tick(USERS, FIRST_VOTE, False)

    measure = book.state.measures[1]
    assert measure.tally is not None
    assert (measure.tally.yes, measure.tally.no) == (51, 50)
    assert measure.status.value == "APPROVED"


def test_fifty_votes_do_not_pass_the_measure(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    votes_say(monkeypatch, house.MAJORITY - 1)

    book.on_tick(USERS, FIRST_VOTE, False)

    assert book.state.measures[1].status.value == "REJECTED"


def test_a_real_vote_is_the_same_after_a_resume(
    book: GovernmentBook, engine, market, stored
):
    govern(book, engine)
    propose(book)
    book.on_tick(USERS, FIRST_VOTE, False)

    rebuilt = replay(stored)

    assert rebuilt.measures[1].tally == book.state.measures[1].tally
    assert rebuilt.measures[1].status == book.state.measures[1].status


# Impeachment votado


def test_the_sixth_closing_opens_the_request_and_the_house_votes_it_next_month(
    book: GovernmentBook, engine, market, bleak, monkeypatch
):
    govern(book, engine)
    votes_say(monkeypatch, house.IMPEACHMENT_VOTES)

    assert close_months(book, 12) is None
    assert close_months(book, 5, date(2023, 1, 31)) is None
    assert book.state.request is None

    assert close_months(book, 1, date(2023, 6, 30)) is None
    request = book.state.request
    assert request is not None
    assert request.vote_day == date(2023, 7, 31)

    assert close_months(book, 1, date(2023, 7, 31)) == PauseReason.IMPEACHMENT
    assert book.state.request is None
    assert book.state.impeachment_votes[-1].approved is True


def test_sixty_seven_votes_keep_the_president_and_restart_the_count(
    book: GovernmentBook, engine, market, bleak, monkeypatch
):
    govern(book, engine)
    votes_say(monkeypatch, house.IMPEACHMENT_VOTES - 1)

    close_months(book, 18)
    assert book.state.request is not None

    assert close_months(book, 1, date(2023, 7, 31)) is None

    assert book.state.request is None
    assert book.state.impeachment_votes[-1].approved is False
    assert book.state.low_streak < 6
    assert book.state.term is not None
    assert book.state.term.president_id == ALICE.id


def test_the_impeachment_request_waits_for_the_house_without_removing_anyone(
    book: GovernmentBook, engine, market, bleak, office
):
    govern(book, engine)

    close_months(book, 18)

    assert book.state.request is not None
    assert book.state.term is not None
    assert book.state.term.president_id == ALICE.id


# Contribuição dividida


def test_the_contribution_splits_between_the_presidency_and_the_congress(
    book: GovernmentBook, engine
):
    book.found_party(
        ALICE,
        CAMPAIGN_OPEN,
        name="Partido AAA",
        abbr="AAA",
        color=RED,
        flags=[VoterValue.STABILITY, VoterValue.DEVELOPMENT, VoterValue.FREE_MARKET],
        contribution=Decimal(10000),
        congress=Decimal(4000),
    )
    party = party_of(book, ALICE)

    book.on_tick(USERS, date(2020, 11, 3), True)

    assert party.spent == Decimal(10000)
    assert sum(party.house_campaign.values()) > 0
    assert sum(party.campaign.values()) > 0


def test_a_party_without_congress_money_has_no_house_campaign(
    book: GovernmentBook, engine
):
    found(book, ALICE, "AAA", RED, "10000")
    party = party_of(book, ALICE)

    book.on_tick(USERS, date(2020, 11, 3), True)

    assert sum(party.house_campaign.values()) == 0


def test_the_congress_share_cannot_exceed_the_contribution(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "10000")

    with pytest.raises(UnprocessableEntityError, match="Congresso"):
        book.set_contribution(ALICE, CAMPAIGN_OPEN, Decimal(1000), Decimal(2000))

    book.set_contribution(ALICE, CAMPAIGN_OPEN, Decimal(1000), Decimal(1000))
    assert party_of(book, ALICE).congress[ALICE.id] == Decimal(1000)


# Painel


def test_the_panel_shows_the_house_the_queue_vote_and_the_leaders_guide(
    book: GovernmentBook, engine, market, monkeypatch
):
    monkeypatch.setattr(governance, "_portfolio", lambda *_: None)
    govern(book, engine, vice=True)
    propose(book)

    leader = build_governance(book, engine, USERS, ALICE, QUEUED_DAY)
    member = build_governance(book, engine, USERS, BOB, QUEUED_DAY)

    assert sum(b.seats for b in leader.congress.house.blocs) == house.SEATS
    vote = leader.queue[0].vote
    assert vote is not None
    assert vote.low is not None and vote.low <= (vote.high or 0)
    assert vote.guide is not None
    assert {s.orientation for s in vote.guide.scenarios} == {True, False}
    # Quem não lidera vê a votação, sem poder orientar
    member_vote = member.queue[0].vote
    assert member_vote is not None and member_vote.guide is None

    book.on_tick(USERS, FIRST_VOTE, False)
    voted = build_governance(book, engine, USERS, ALICE, FIRST_VOTE)
    closed = voted.queue[0].vote if voted.queue else None
    assert closed is None or closed.yes is not None
    assert voted.congress.history[0].yes + voted.congress.history[0].no == house.SEATS
