"""Capital político: cadeiras por mês, presidência pela aprovação, promessas, impeachment e o desempate."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.enum import PauseReason, VoterGroup
from backend.core.utils import required
from backend.features.government import approval as approval_rules
from backend.features.government import congress, house
from backend.features.government.capital import (
    IMPEACHMENT_LOSS,
    PROMISE_POINTS,
    party_capital,
)
from backend.features.government.government_book import GovernmentBook
from backend.features.government.standings import party_ranking
from backend.features.government.state import (
    Balance,
    BalanceItem,
    ElectedHouse,
    GovernedMonth,
    GovernmentState,
    Impeachment,
    Party,
    replay,
)
from tests.test_government_book import (
    ALICE,
    BLUE,
    BOB,
    CAMPAIGN_OPEN,
    FIRST_ROUND,
    NICHE,
    RED,
    RUNOFF,
    SECTORS,
    TERM_START,
    USERS,
    bleak,
    book,
    close_months,
    congress_says,
    engine,
    found,
    govern,
    headlines,
    market,
    notices,
    office,
    party_of,
    run_campaign,
    stored,
)
from tests.test_government_promises import (
    govern_promising,
    promise,
    propose_cut,
    request,
    silent_computers,
)

TAKES_OFFICE = date(2022, 1, 1)
JANUARY = congress.last_business_day(2022, 1)
MARCH = congress.last_business_day(2022, 3)
APRIL = congress.last_business_day(2022, 4)


def party(party_id: int, computer: bool = False) -> Party:
    return Party(
        id=party_id,
        name=f"Partido {party_id}",
        abbr=f"P{party_id}",
        color=None if computer else RED,
        flags=None,
        founder_id=None if computer else party_id,
        is_computer=computer,
        founded=date(2020, 1, 1),
    )


def bloc(party_id: int, seats: int) -> house.Bloc:
    return house.Bloc(
        key=party_id,
        party_id=party_id,
        abbr=f"P{party_id}",
        name=f"Partido {party_id}",
        color=None,
        is_computer=False,
        votes=Decimal(seats),
        seats=seats,
        mix=dict.fromkeys(VoterGroup, Decimal(1) / len(VoterGroup)),
    )


def elected(takes_office: date, seats: dict[int, int], cycle: int = 0) -> ElectedHouse:
    return ElectedHouse(
        day=takes_office,
        takes_office=takes_office,
        cycle=cycle,
        house=house.House(blocs=tuple(bloc(p, n) for p, n in seats.items())),
    )


def drafted(today: date, *parties: Party) -> GovernmentState:
    """Um estado montado à mão: os partidos, sem casa nem governo, no dia `today`."""
    state = GovernmentState(parties={p.id: p for p in parties})
    state.today = today
    return state


def settled(party_id: int, *done: str) -> Balance:
    return Balance(
        day=date(2025, 12, 31),
        party_id=party_id,
        term_start=TAKES_OFFICE,
        items=tuple(BalanceItem(promise(), Decimal(d), {}) for d in done),
        impeached=False,
    )


def ranked(state: GovernmentState):
    return {p.id: c for p, c in party_capital(state)}


def test_seats_pay_one_point_each_at_every_month_closing():
    state = drafted(MARCH, party(1), party(2))
    state.houses.append(elected(TAKES_OFFICE, {1: 28, 2: 20}))

    capital = ranked(state)

    # Janeiro, fevereiro e março fecham até o fim de março
    assert capital[1].seats == 28 * 3
    assert capital[2].seats == 20 * 3
    assert capital[1].total == 84


def test_a_closing_counts_only_once_its_day_has_arrived():
    state = drafted(date(2022, 3, 30), party(1))
    state.houses.append(elected(TAKES_OFFICE, {1: 10}))

    assert ranked(state)[1].seats == 10 * 2


def test_a_new_house_pays_from_the_closing_after_it_takes_office():
    state = drafted(APRIL, party(1))
    state.houses.append(elected(TAKES_OFFICE, {1: 10}))
    state.houses.append(elected(date(2022, 3, 15), {1: 20}, cycle=1))

    # Janeiro e fevereiro pela primeira casa; março e abril pela segunda
    assert ranked(state)[1].seats == 10 * 2 + 20 * 2


def test_without_an_elected_house_nobody_scores_seats():
    state = drafted(APRIL, party(1))

    assert ranked(state)[1].total == 0


def test_a_party_without_a_bloc_scores_no_seats():
    state = drafted(MARCH, party(1), party(2))
    state.houses.append(elected(TAKES_OFFICE, {1: 40}))

    assert ranked(state)[2].seats == 0


def test_the_computer_party_never_scores():
    state = drafted(MARCH, party(1), party(2, computer=True))
    state.houses.append(elected(TAKES_OFFICE, {1: 10, 2: 50}))
    state.governed_months.append(GovernedMonth(JANUARY, 2, TAKES_OFFICE, 90))

    assert list(ranked(state)) == [1]


def test_each_promise_pays_in_proportion_to_the_share_kept():
    state = drafted(APRIL, party(1))
    state.balances.append(settled(1, "1", "1", "0.5"))

    capital = ranked(state)[1]

    # Duas inteiras e uma pela metade: 2,5 promessas
    assert capital.promises == PROMISE_POINTS * 5 // 2
    assert capital.total == 250


def test_a_promise_broken_the_other_way_pays_nothing_and_takes_nothing():
    state = drafted(APRIL, party(1))
    state.balances.append(settled(1, "1", "-1"))

    assert ranked(state)[1].promises == PROMISE_POINTS


def test_the_balance_of_another_party_does_not_count():
    state = drafted(APRIL, party(1), party(2))
    state.balances.append(settled(2, "1"))

    capital = ranked(state)

    assert capital[1].promises == 0
    assert capital[2].promises == PROMISE_POINTS


def test_an_impeachment_takes_half_of_what_the_presidency_paid_in_that_term():
    state = drafted(APRIL, party(1))
    for day, approval in [(date(2022, 1, 28), 40), (date(2022, 2, 28), 41)]:
        state.governed_months.append(GovernedMonth(day, 1, TAKES_OFFICE, approval))
    # O mandato do sucessor, que começa no impeachment, fica de fora da perda
    state.governed_months.append(GovernedMonth(APRIL, 1, date(2022, 3, 15), 50))
    state.impeachments.append(Impeachment(date(2022, 3, 15), 1, 1, 2, TAKES_OFFICE))

    capital = ranked(state)[1]

    assert capital.presidency == 40 + 41 + 50
    # Metade de 81, arredondada para cima
    assert capital.impeachment == -41
    assert capital.total == capital.presidency + capital.impeachment


def test_ties_break_by_the_seats_of_the_current_house():
    state = drafted(JANUARY, party(1), party(2))
    state.houses.append(elected(TAKES_OFFICE, {1: 10, 2: 20}))
    # 10 cadeiras e uma promessa inteira empatam com 20 cadeiras e nove décimos
    state.balances.append(settled(1, "1"))
    state.balances.append(settled(2, "0.9"))

    ordered = party_capital(state)

    assert ordered[0][1].total == ordered[1][1].total == 110
    assert [p.id for p, _ in ordered] == [2, 1]


def test_ties_without_seats_break_by_the_party_id():
    state = drafted(APRIL, party(2), party(1))
    state.balances.append(settled(1, "1"))
    state.balances.append(settled(2, "1"))

    assert [p.id for p, _ in party_capital(state)] == [1, 2]


def test_the_closing_months_of_a_player_government_pay_the_approval_of_each_one(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    alice = party_of(book, ALICE)

    close_months(book, 3)

    measured = [
        approval_rules.rounded(approval_rules.overall(a.satisfaction))
        for a in book.state.approvals
    ]
    [(listed, capital)] = party_capital(book.state)
    bench = required(book.state.house_on(TERM_START).of_party(alice.id))
    assert listed.id == alice.id
    assert len(measured) == 3
    assert capital.presidency == sum(measured)
    assert capital.seats == 3 * bench.seats
    assert (capital.promises, capital.impeachment) == (0, 0)
    assert capital.total == capital.seats + capital.presidency


def test_a_kept_promise_pays_at_the_term_settlement(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern_promising(book, engine, request())
    propose_cut(book)
    congress_says(monkeypatch, True)
    close_months(book, 1)

    before = party_capital(book.state)[0][1]
    book.on_tick(USERS, date(2025, 12, 31), False)

    [balance] = book.state.balances
    after = party_capital(book.state)[0][1]
    assert before.promises == 0
    assert balance.items[0].done == 1
    assert after.promises == PROMISE_POINTS


def test_an_impeachment_takes_points_from_the_party_and_the_vice_keeps_scoring(
    book: GovernmentBook, engine, market, bleak
):
    govern(book, engine, vice=True)
    assert close_months(book, 19) == PauseReason.IMPEACHMENT
    close_months(book, 2, date(2023, 8, 31))

    state = book.state
    [impeachment] = state.impeachments
    capital = party_capital(state)[0][1]
    dropped = sum(
        m.approval for m in state.governed_months if m.term_start == TAKES_OFFICE
    )
    successor = [m for m in state.governed_months if m.term_start == impeachment.day]
    assert impeachment.term_start == TAKES_OFFICE
    assert dropped > 0
    assert len(successor) == 2
    assert capital.presidency == dropped + sum(m.approval for m in successor)
    assert capital.impeachment == -int(
        Decimal(dropped) * IMPEACHMENT_LOSS + Decimal("0.5")
    )
    assert capital.total == capital.seats + capital.presidency + capital.impeachment


def test_a_computer_government_after_an_impeachment_scores_for_nobody(
    book: GovernmentBook, engine, market, bleak
):
    govern(book, engine)
    assert close_months(book, 19) == PauseReason.IMPEACHMENT
    [impeachment] = book.state.impeachments
    scored = len(book.state.governed_months)

    close_months(book, 2, date(2023, 8, 31))

    assert len(book.state.approvals) == 2
    assert len(book.state.governed_months) == scored
    assert all(m.day <= impeachment.day for m in book.state.governed_months)
    assert [p.abbr for p, _ in party_capital(book.state)] == ["AAA"]


def test_the_opposition_scores_only_with_its_seats(
    book: GovernmentBook, engine, market
):
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    found(book, BOB, "BBB", BLUE, "10000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)
    assert required(book.state.term).president_id == ALICE.id
    bob = party_of(book, BOB)
    bench = required(book.state.house_on(TERM_START).of_party(bob.id))
    assert bench.seats > 0

    close_months(book, 3)

    capital = ranked(book.state)[bob.id]
    assert capital.seats == 3 * bench.seats
    assert (capital.presidency, capital.promises, capital.impeachment) == (0, 0, 0)
    assert capital.total == capital.seats


def test_the_ranking_of_a_match_lists_the_gap_to_the_leader_in_points(
    book: GovernmentBook, engine, market, monkeypatch
):
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    found(book, BOB, "BBB", BLUE, "10000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)
    close_months(book, 3)
    monkeypatch.setattr(
        repository.simulation_player, "participants", lambda _simulation_id: USERS
    )

    first, second = party_ranking(1)

    assert (first.position, second.position) == (1, 2)
    assert first.leader_gap == 0
    assert second.leader_gap == first.capital.total - second.capital.total
    assert first.members == ["Alice"]
    assert second.members == ["Bob"]
    assert first.color == RED


def test_the_ranking_of_a_match_without_players_is_empty(
    book: GovernmentBook, monkeypatch
):
    monkeypatch.setattr(
        repository.simulation_player, "participants", lambda _simulation_id: USERS
    )

    assert party_ranking(1) == []


def test_the_live_capital_is_the_one_the_replay_of_the_events_rebuilds(
    book: GovernmentBook, engine, market, bleak, stored
):
    govern(book, engine, vice=True)
    assert close_months(book, 19) == PauseReason.IMPEACHMENT
    close_months(book, 2, date(2023, 8, 31))

    live = party_capital(book.state)
    replayed = party_capital(replay(stored))

    assert live[0][1].impeachment < 0
    assert [(p.id, c) for p, c in replayed] == [(p.id, c) for p, c in live]
