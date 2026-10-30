"""Preparação do lobby no livro do governo: aplicada na abertura da campanha, só a quem está na partida."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date

from backend.core.enum import GovernmentEventType, VoterValue
from backend.features.government import preparation
from backend.features.government.government_book import GovernmentBook
from backend.features.government.preparation import PartyIdentity, Prepared
from backend.features.government.state import replay
from tests.test_government_book import (
    ALICE,
    BOB,
    CAMPAIGN_OPEN,
    CARLA,
    FLAGS,
    RED,
    SEED,
    USERS,
    book,
    engine,
    headlines,
    notices,
    office,
    party_of,
    settings,
    stored,
)

IDENTITY = PartyIdentity("Partido Alfa", "ALF", RED, tuple(FLAGS))


def prepare(engine, *players: Prepared) -> GovernmentBook:
    """Grava a preparação como o loader faz e reabre o livro, que a lê do replay."""
    preparation.record(1, date(2020, 1, 1), list(players))
    return GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)


def open_campaign(book: GovernmentBook) -> None:
    book.on_tick(USERS, date(2020, 10, 6), False)
    book.on_tick(USERS, CAMPAIGN_OPEN, False)


def test_campaign_opening_founds_joins_and_sets_the_ticket(book, engine, stored):
    prepared = prepare(
        engine,
        Prepared(
            ALICE.id,
            found=IDENTITY,
            candidate_id=BOB.id,
            vice_id=CARLA.id,
            vice_accepted=True,
        ),
        Prepared(BOB.id, join_id=ALICE.id),
    )

    open_campaign(prepared)

    party = party_of(prepared, ALICE)
    assert (party.abbr, party.founder_id) == ("ALF", ALICE.id)
    assert party.color == RED
    assert party.members == {ALICE.id: 0, BOB.id: 0}
    assert party.candidate_id == BOB.id
    assert (party.vice_id, party.vice_accepted) == (CARLA.id, True)
    assert prepared.state.preparations == []


def test_player_absent_from_the_match_is_not_applied(book, engine, stored):
    stranger = Prepared(99, found=PartyIdentity("Fora", "FOR", RED, tuple(FLAGS)))
    prepared = prepare(engine, stranger)

    open_campaign(prepared)

    assert prepared.state.player_parties() == []
    assert prepared.state.preparations == []


def test_refused_request_does_not_block_the_rest(book, engine, stored):
    clash = PartyIdentity("Outro", "ALF", "#2563eb", tuple(FLAGS))
    prepared = prepare(
        engine,
        Prepared(ALICE.id, found=IDENTITY),
        Prepared(BOB.id, found=clash),
        Prepared(CARLA.id, join_id=ALICE.id),
    )

    open_campaign(prepared)

    assert party_of(prepared, ALICE).abbr == "ALF"
    assert party_of(prepared, CARLA).founder_id == ALICE.id
    assert prepared.state.party_of(BOB.id) is None


def test_preparation_waits_for_the_campaign_and_survives_a_resume(book, engine, stored):
    prepared = prepare(engine, Prepared(ALICE.id, found=IDENTITY))

    prepared.on_tick(USERS, date(2020, 5, 4), False)
    assert prepared.state.player_parties() == []
    resumed = GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)
    assert len(resumed.state.preparations) == 1

    open_campaign(resumed)

    assert party_of(resumed, ALICE).abbr == "ALF"
    assert replay(stored).preparations == []


def test_applied_preparation_is_not_replayed_twice(book, engine, stored):
    prepared = prepare(engine, Prepared(ALICE.id, found=IDENTITY))
    open_campaign(prepared)

    kinds = [e.event_type for e in stored]
    assert kinds.count(GovernmentEventType.PARTIES_PREPARED) == 2
    assert kinds.count(GovernmentEventType.PARTY_FOUNDED) == 1
    assert VoterValue.STABILITY in party_of(prepared, ALICE).flags  # type: ignore[operator]
