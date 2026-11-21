"""Os avisos do governo levam o dado que o toast e o diálogo mostram, e cada um chega só a quem ele interessa."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import pytest

from backend.core.enum import CampaignActionKind, GovernmentNoticeKind
from backend.features.government.government_book import GovernmentBook
from tests.test_government_book import (
    ACTION_DAY,
    ALICE,
    BOB,
    CAMPAIGN_OPEN,
    CARLA,
    RETIREES,
    USERS,
    approval_rules,
    bleak,
    book,
    close_months,
    dice,
    engine,
    found,
    govern,
    headlines,
    market,
    notices,
    office,
    party_of,
    stored,
    two_parties,
)

type Delivered = list[tuple[dict, UUID | None]]


@pytest.fixture
def delivered(monkeypatch: pytest.MonkeyPatch, book: GovernmentBook) -> Delivered:
    """Cada aviso do governo com o destinatário: nulo é a sala inteira."""
    sent: Delivered = []
    monkeypatch.setattr(
        "backend.features.government.government_book.notify",
        lambda _name, payload, to=None: sent.append((payload, to)),
    )
    return sent


def of_kind(delivered: Delivered, kind: GovernmentNoticeKind):
    return [(p, to) for p, to in delivered if p["kind"] == kind.value]


def test_a_campaign_action_reaches_the_other_members_of_the_party(
    book: GovernmentBook, delivered: Delivered, dice
):
    mine, _rival = two_parties(book)
    book.join_party(CARLA, CAMPAIGN_OPEN, mine.id, Decimal(0))
    dice(10)
    # O livro conhece os jogadores da partida a cada dia
    book.on_tick(USERS, ACTION_DAY, False)
    delivered.clear()

    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, None)

    [(payload, to)] = of_kind(delivered, GovernmentNoticeKind.CAMPAIGN_ACTION)
    assert to == CARLA.client_id
    assert payload["actor"] == "Alice"
    assert payload["roll"] == 10
    assert payload["support"] is not None


def test_an_attack_tells_the_rival_party_only_the_support_it_lost(
    book: GovernmentBook, delivered: Delivered, dice
):
    _mine, rival = two_parties(book)
    dice(10)
    # O livro conhece os jogadores da partida a cada dia
    book.on_tick(USERS, ACTION_DAY, False)
    delivered.clear()

    book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, rival.id
    )

    received = [
        (p, to)
        for p, to in of_kind(delivered, GovernmentNoticeKind.CAMPAIGN_ACTION)
        if p["received"]
    ]
    [(payload, to)] = received
    assert to == BOB.client_id
    assert payload["actor"] is None and payload["roll"] is None
    assert payload["rival_abbr"] == "BBB"
    assert payload["support"] is not None


def test_the_month_close_reaches_only_the_members_of_the_governing_party(
    book: GovernmentBook, engine, delivered: Delivered, market, bleak
):
    govern(book, engine)
    delivered.clear()

    close_months(book, 1)

    closed = of_kind(delivered, GovernmentNoticeKind.MONTH_CLOSED)
    assert closed
    assert {to for _payload, to in closed} == {ALICE.client_id}
    assert all(p["approval"] is not None for p, _to in closed)


def test_the_impeachment_notice_carries_the_dialog_data_to_the_whole_room(
    book: GovernmentBook, engine, delivered: Delivered, market, bleak
):
    govern(book, engine)
    delivered.clear()

    close_months(book, 19)

    [(payload, to)] = of_kind(delivered, GovernmentNoticeKind.IMPEACHMENT)
    assert to is None
    assert payload["impeachment"]["president"]
    assert payload["term_end"] is not None
    assert payload["next_election"] is not None


def test_the_round_result_carries_the_vote_to_the_whole_room(
    book: GovernmentBook, engine, delivered: Delivered
):
    govern(book, engine)

    results = of_kind(delivered, GovernmentNoticeKind.ELECTION_RESULT)
    assert results
    assert all(to is None for _payload, to in results)
    last, _to = results[-1]
    assert last["winner_abbr"] == "AAA"
    assert last["winner_share"] is not None
