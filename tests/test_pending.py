"""Pendências do jogador: o registro, a ordem e as de governo (risco de impeachment, convite de vice e campanha sem filiação)."""


# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.enum import PendingSeverity, PendingType
from backend.features.government import approval as approval_rules
from backend.features.government.government_book import GovernmentBook
from backend.features.notifications import registry
from tests.test_government_book import (
    ALICE,
    BOB,
    BOT,
    CAMPAIGN_OPEN,
    CARLA,
    RED,
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
    stored,
)


def types(items) -> list[PendingType]:
    return [item.type for item in items]


def test_every_pending_type_is_registered_once():
    assert [spec.type for spec in registry.PENDING] == list(PendingType)
    assert set(registry.PENDING_BY_TYPE) == set(PendingType)


def test_every_pending_carries_when_it_goes_away():
    for spec in registry.PENDING:
        item = registry.pending(spec.type, "x")

        assert item.resolves == spec.resolves
        assert item.resolves.startswith(("Some ", "Só para"))


def test_severe_ones_come_before_the_warnings_in_the_registry_order():
    severities = [spec.severity for spec in registry.PENDING]

    assert severities == sorted(severities, key=lambda s: s is PendingSeverity.WARNING)


def test_sort_puts_the_severe_first_whatever_the_order_it_was_built():
    items = [
        registry.pending(PendingType.CAMPAIGN_OPEN, "x"),
        registry.pending(PendingType.NEGATIVE_CASH, "x"),
        registry.pending(PendingType.STRATEGY_ERROR, "x"),
        registry.pending(PendingType.OVERDUE_INSTALLMENT, "x", ref="b"),
        registry.pending(PendingType.OVERDUE_INSTALLMENT, "x", ref="a"),
    ]

    ordered = registry.sort_pending(items)

    assert [item.key for item in ordered] == [
        "OVERDUE_INSTALLMENT:a",
        "OVERDUE_INSTALLMENT:b",
        "NEGATIVE_CASH",
        "STRATEGY_ERROR",
        "CAMPAIGN_OPEN",
    ]


def test_the_campaign_asks_the_player_without_a_party_to_join(book: GovernmentBook):
    [pending] = book.pending(BOB, CAMPAIGN_OPEN)

    assert pending.type is PendingType.CAMPAIGN_OPEN
    assert pending.severity is PendingSeverity.WARNING
    assert pending.title == "Campanha aberta sem filiação"
    assert book.pending(BOT, CAMPAIGN_OPEN) == []


def test_the_campaign_pending_goes_away_with_the_party(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    assert book.pending(ALICE, CAMPAIGN_OPEN) == []
    assert types(book.pending(BOB, CAMPAIGN_OPEN)) == [PendingType.CAMPAIGN_OPEN]


def test_no_pending_before_the_campaign_or_after_the_tickets_close(
    book: GovernmentBook,
):
    deadline = book.cycle().ticket_deadline

    assert book.pending(BOB, date(2020, 6, 1)) == []
    assert types(book.pending(BOB, deadline)) == [PendingType.CAMPAIGN_OPEN]
    assert book.pending(BOB, deadline + timedelta(days=1)) == []


def test_the_vice_invite_is_a_pending_until_the_answer(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, ALICE).id, Decimal(0))
    book.on_tick(USERS, CAMPAIGN_OPEN, False)
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)

    [pending] = book.pending(BOB, CAMPAIGN_OPEN)
    assert pending.type is PendingType.VICE_INVITE
    assert pending.detail == "Alice quer você na chapa do AAA"
    assert book.pending(ALICE, CAMPAIGN_OPEN) == []

    book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    assert book.pending(BOB, CAMPAIGN_OPEN) == []


def test_a_player_in_another_party_still_gets_the_vice_invite(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, CARLA, "CCC", "#2563eb")
    book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, CARLA).id, Decimal(0))
    book.on_tick(USERS, CAMPAIGN_OPEN, False)
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)

    assert types(book.pending(BOB, CAMPAIGN_OPEN)) == [PendingType.VICE_INVITE]


def test_impeachment_risk_starts_after_the_grace_and_only_for_the_president(
    book: GovernmentBook, engine, market, bleak
):
    govern(book, engine)

    # Na carência o piso não conta: nem a aprovação no chão dá risco
    close_months(book, 12)
    assert book.pending(ALICE, date(2022, 12, 31)) == []

    close_months(book, 1, date(2023, 1, 31))
    [risk] = book.pending(ALICE, date(2023, 1, 31))
    assert risk.type is PendingType.IMPEACHMENT_RISK
    assert risk.severity is PendingSeverity.SEVERE
    assert "1 de 6 fechamentos abaixo de 25%" in risk.detail
    assert types(book.pending(BOB, date(2023, 1, 31))) == []


def test_impeachment_risk_follows_the_approval_band_without_a_streak(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    after_grace = date(2023, 2, 28)
    value = required_value(book, after_grace)

    risky = value < approval_rules.FLOOR + approval_rules.RISK_MARGIN
    assert (
        types(book.pending(ALICE, after_grace)) == [PendingType.IMPEACHMENT_RISK]
    ) == risky


def required_value(book: GovernmentBook, day: date) -> int:
    current = book.approval(day)
    assert current is not None
    return current.value
