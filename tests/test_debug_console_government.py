"""Os comandos de governo do console do modo debug no livro: filiação, posse, impeachment e SELIC, com a retomada pelo histórico de eventos."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.copom import meeting_days
from backend.core.enum import SelicControl
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from tests.test_government_book import (
    ALICE,
    BOB,
    CAMPAIGN_OPEN,
    CARLA,
    SEED,
    TERM_START,
    USERS,
    book,
    engine,
    found,
    govern,
    headlines,
    notices,
    office,
    party_of,
    settings,
    stored,
)

MEETING = meeting_days(2022)[0]
FIRST_ROUND_DEADLINE = date(2021, 4, 7)
ALICE_PARTY = "AAA"


@pytest.fixture
def selic_book(
    engine, stored, notices, captured_events, office, headlines
) -> GovernmentBook:
    rules = settings().model_copy(update={"selic_control": SelicControl.GOVERNMENT})
    return GovernmentBook(
        rules,
        engine,
        lambda user, _day: office.append(user.id),
        lambda *_: Decimal(0),
        lambda day, headline: headlines.append((day, headline)),
        SEED,
    )


# Filiação


def test_the_joiner_runs_in_the_next_election_even_after_the_deadline(
    book: GovernmentBook,
):
    found(book, ALICE, ALICE_PARTY, "#dc2626")
    late = date(2021, 8, 1)

    book.join_for_next_election(BOB, late, ALICE_PARTY)

    assert party_of(book, ALICE).joined[BOB.id] == FIRST_ROUND_DEADLINE
    book.set_ticket(ALICE, late, "Bob", USERS)


def test_the_joiner_before_the_deadline_keeps_the_day_of_the_command(
    book: GovernmentBook,
):
    found(book, ALICE, ALICE_PARTY, "#dc2626")

    book.join_for_next_election(BOB, CAMPAIGN_OPEN, ALICE_PARTY)

    assert party_of(book, ALICE).joined[BOB.id] == CAMPAIGN_OPEN


def test_the_unknown_party_is_refused(book: GovernmentBook):
    found(book, ALICE, ALICE_PARTY, "#dc2626")

    with pytest.raises(NotFoundError, match="XYZ"):
        book.join_for_next_election(BOB, CAMPAIGN_OPEN, "XYZ")


def test_the_computer_party_does_not_take_members(book: GovernmentBook):
    found(book, ALICE, ALICE_PARTY, "#dc2626")
    computer = book.state.computer_parties()[0]

    with pytest.raises(ConflictError, match="computador"):
        book.join_for_next_election(BOB, CAMPAIGN_OPEN, computer.abbr)


def test_the_member_of_a_party_cannot_join_another(book: GovernmentBook):
    found(book, ALICE, ALICE_PARTY, "#dc2626")
    found(book, BOB, "BBB", "#2563eb")

    with pytest.raises(ConflictError):
        book.join_for_next_election(BOB, CAMPAIGN_OPEN, ALICE_PARTY)


# Posse


def test_the_player_of_a_party_takes_the_office_today(
    book: GovernmentBook, engine, office, stored
):
    govern(book, engine)
    book.join_for_next_election(BOB, TERM_START, ALICE_PARTY)
    today = TERM_START + timedelta(days=10)
    office.clear()

    book.assume_presidency(BOB, today)

    president = book.president()
    assert president is not None and president.id == BOB.id
    assert office == [BOB.id]
    term = book.state.term
    assert term is not None
    assert term.party_id == party_of(book, ALICE).id
    assert term.start == today


def test_the_takeover_survives_the_replay_and_keeps_the_end_of_the_term(
    book: GovernmentBook, engine, stored
):
    govern(book, engine)
    end = book.term_end()
    book.join_for_next_election(BOB, TERM_START, ALICE_PARTY)
    book.assume_presidency(BOB, TERM_START + timedelta(days=10))

    rebuilt = replay(stored)

    assert rebuilt.term == book.state.term
    assert rebuilt.pending_term is None
    assert book.term_end() == end


def test_the_takeover_without_a_party_points_to_join_party(
    book: GovernmentBook, engine
):
    govern(book, engine)

    with pytest.raises(ConflictError, match="join_party"):
        book.assume_presidency(CARLA, TERM_START)


def test_the_sitting_president_cannot_take_the_office_again(
    book: GovernmentBook, engine
):
    govern(book, engine)

    with pytest.raises(ConflictError, match="já é o presidente"):
        book.assume_presidency(ALICE, TERM_START)


def test_the_takeover_waits_for_the_elected_successor(book: GovernmentBook, engine):
    govern(book, engine)
    book.join_for_next_election(BOB, TERM_START, ALICE_PARTY)
    book.state.pending_term = book.state.term

    with pytest.raises(ConflictError, match="sucessor"):
        book.assume_presidency(BOB, TERM_START + timedelta(days=1))


# Impeachment


def test_the_impeachment_opens_for_the_sitting_president(book: GovernmentBook, engine):
    govern(book, engine)
    assert book.state.request is None

    book.open_impeachment(TERM_START + timedelta(days=5))

    assert book.state.request is not None


def test_the_impeachment_needs_a_president(book: GovernmentBook):
    with pytest.raises(ConflictError, match="presidente"):
        book.open_impeachment(CAMPAIGN_OPEN)


def test_a_second_impeachment_request_is_refused(book: GovernmentBook, engine):
    govern(book, engine)
    book.open_impeachment(TERM_START + timedelta(days=5))

    with pytest.raises(ConflictError, match="aberto"):
        book.open_impeachment(TERM_START + timedelta(days=6))


# SELIC


def test_the_forced_selic_applies_from_tomorrow_and_keeps_the_meeting_calendar(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)
    today = TERM_START + timedelta(days=3)
    expected_meeting = selic_book.next_selic_meeting(today + timedelta(days=1))

    selic_book.force_selic(today, Decimal("0.1375"))

    tomorrow = today + timedelta(days=1)
    assert selic_book.state.selic_board.selic_on(today) != Decimal("0.1375")
    assert selic_book.state.selic_board.selic_on(tomorrow) == Decimal("0.1375")
    assert selic_book.next_selic_meeting(tomorrow) == expected_meeting


def test_the_forced_selic_survives_the_replay(
    selic_book: GovernmentBook, engine, stored
):
    govern(selic_book, engine)
    today = TERM_START + timedelta(days=3)
    selic_book.force_selic(today, Decimal("0.1375"))

    state = replay(stored)

    assert state.selic_board.decisions() == selic_book.state.selic_board.decisions()
    assert state.last_meeting == selic_book.state.last_meeting


def test_the_forced_selic_keeps_the_mark_of_the_president(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)
    selic_book.set_selic(ALICE, TERM_START, Decimal("0.01"))

    selic_book.force_selic(TERM_START + timedelta(days=3), Decimal("0.0125"))

    assert selic_book.state.selic_plan == Decimal("0.01")


def test_the_forced_selic_refuses_a_rate_off_the_step(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)

    with pytest.raises(UnprocessableEntityError, match="0,25"):
        selic_book.force_selic(TERM_START, Decimal("0.1301"))


def test_the_forced_selic_refuses_a_rate_below_the_floor(
    selic_book: GovernmentBook, engine
):
    govern(selic_book, engine)

    with pytest.raises(UnprocessableEntityError, match="não desce"):
        selic_book.force_selic(TERM_START, Decimal("-0.0075"))


def test_the_autonomous_central_bank_refuses_the_forced_selic(
    book: GovernmentBook, engine
):
    govern(book, engine)

    with pytest.raises(ConflictError, match="autônomo"):
        book.force_selic(TERM_START, Decimal("0.1375"))
