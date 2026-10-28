"""Promessas de campanha: o que rendem, o balanço do mandato, a metade na reeleição e o replay."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.promises import PromiseRequest
from backend.core.enum import (
    GovernmentNoticeKind,
    MeasureKind,
    PauseReason,
    PromiseState,
    VoterGroup,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.government import promises, voters
from backend.features.government.government_book import GovernmentBook
from backend.features.government.promise_panel import (
    build_balances,
    build_preview,
    build_term_promises,
)
from backend.features.government.promises import Promise
from backend.features.government.state import Party, replay
from tests.test_government_book import (
    ALICE,
    BOB,
    CAMPAIGN_OPEN,
    FIRST_ROUND,
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
    market,
    notices,
    office,
    party_of,
    run_campaign,
    stored,
)

ZERO = Decimal(0)
BASELINE = Decimal("0.15")
TARGET = Decimal("0.10")
ANNOUNCED = date(2020, 11, 2)


def promise(
    target: str = "0.10", baseline: str = "0.15", kind=MeasureKind.STOCK_PROFIT_RATE
) -> Promise:
    return Promise(kind, Decimal(target), Decimal(baseline), None, None, ANNOUNCED)


def request(target="0.10", kind=MeasureKind.STOCK_PROFIT_RATE) -> PromiseRequest:
    return PromiseRequest(kind=kind, target=Decimal(target))


# Regras


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        ("0.15", "0"),
        ("0.125", "0.5"),
        ("0.10", "1"),
        ("0.05", "1"),
        ("0.175", "-0.5"),
        ("0.30", "-1"),
    ],
)
def test_progress_is_the_share_of_the_way_from_the_baseline_to_the_target(
    current: str, expected: str
):
    assert promises.progress(promise(), Decimal(current), False) == Decimal(expected)


def test_sector_promise_is_yes_or_no():
    exempt = Promise(MeasureKind.SECTOR_EXEMPT, None, None, "Energia", None, ANNOUNCED)

    assert promises.progress(exempt, None, True) == 1
    assert promises.progress(exempt, None, False) == 0


@pytest.mark.parametrize(
    ("done", "state"),
    [
        ("1", PromiseState.FULFILLED),
        ("0.5", PromiseState.IN_PROGRESS),
        ("0", PromiseState.UNTOUCHED),
        ("-0.5", PromiseState.CONTRARY),
    ],
)
def test_state_names_the_progress(done: str, state: PromiseState):
    assert promises.state_of(Decimal(done)) is state


def test_support_is_discounted_by_the_rejection_only_where_it_pays():
    cut = promise()
    for group in VoterGroup:
        reaction = promises.reaction(group, cut)
        full = promises.yield_of(cut, group, ZERO)
        discounted = promises.yield_of(cut, group, Decimal(40))
        assert full == promises.GAIN * reaction
        if reaction > 0:
            # Com 40 de rejeição a promessa rende 60%
            assert discounted == full * Decimal("0.6")
        else:
            assert discounted == full


def test_a_kept_promise_gains_loyalty_and_repairs_and_a_broken_one_adds_rejection():
    cut = promise()
    kept = promises.settle(cut, Decimal(1))
    broken = promises.settle(cut, ZERO)
    contrary = promises.settle(cut, Decimal(-1))

    for group in VoterGroup:
        want = promises.wanted(group, cut)
        assert kept[group].loyalty == promises.LOYALTY * want
        assert kept[group].rejection == -promises.REPAIR * want
        assert broken[group].loyalty == 0
        assert broken[group].rejection == promises.BREAK * want
        # Andar para trás pesa 1,5 vez o não fazer nada
        assert contrary[group].rejection == broken[group].rejection * Decimal("1.5")
    assert any(effect.loyalty > 0 for effect in kept.values())


def test_half_the_way_settles_in_proportion():
    cut = promise()
    full, half = promises.settle(cut, Decimal(1)), promises.settle(cut, Decimal("0.5"))

    for group in VoterGroup:
        assert half[group].loyalty == full[group].loyalty / 2
    # O que falta do caminho soma metade da rejeição e o que andou repara metade
    wanting = next(g for g in VoterGroup if promises.wanted(g, cut) > 0)
    want = promises.wanted(wanting, cut)
    assert (
        half[wanting].rejection
        == promises.BREAK * want / 2 - promises.REPAIR * want / 2
    )


def test_retreat_costs_half_the_break_of_what_was_dropped():
    cut = promise()
    cost = promises.retreat(cut, None)
    lowered = promises.retreat(cut, promise("0.12"))
    raised = promises.retreat(cut, promise("0.05"))

    wanting = next(g for g in VoterGroup if promises.wanted(g, cut) > 0)
    assert cost[wanting] == promises.RETREAT_SHARE * promises.BREAK * promises.wanted(
        wanting, cut
    )
    assert 0 < lowered[wanting] < cost[wanting]
    assert all(value == 0 for value in raised.values())
    # Trocar de lado é desistir da promessa inteira
    assert promises.retreat(cut, promise("0.20")) == cost


def test_remaining_closes_what_the_half_weight_left():
    full = promises.settle(promise(), Decimal(1))
    half = promises.scaled(full, promises.WEIGHED_SHARE)
    rest = promises.remaining(full, half)

    for group in VoterGroup:
        assert half[group].loyalty + rest[group].loyalty == full[group].loyalty
        assert half[group].rejection + rest[group].rejection == full[group].rejection


def test_computer_promises_move_the_values_of_its_profile():
    radar = voters.initial_radar(
        [VoterValue.FREE_MARKET, VoterValue.STABILITY, VoterValue.DEVELOPMENT]
    )
    baselines = {
        MeasureKind.STOCK_PROFIT_RATE: BASELINE,
        MeasureKind.LCI_LCA_RATE: Decimal("0.05"),
    }

    picks = promises.computer_picks(radar, baselines, ANNOUNCED)

    assert 1 <= len(picks) <= promises.COMPUTER_PROMISES
    stock = next(p for p in picks if p.kind is MeasureKind.STOCK_PROFIT_RATE)
    # Quem defende o mercado livre promete cortar o imposto
    assert stock.target is not None and stock.target < BASELINE


def test_promise_payload_survives_the_round_trip():
    cut = promise()

    assert promises.from_payload(promises.to_payload(cut)) == cut
    effects = promises.settle(cut, Decimal("0.5"))
    assert (
        promises.effects_from_payload(promises.effects_to_payload(effects)) == effects
    )


# Anúncio


def announce(book: GovernmentBook, *items: PromiseRequest, day=CAMPAIGN_OPEN) -> None:
    book.set_promises(ALICE, day, list(items))


def test_the_founder_announces_up_to_three_promises(book: GovernmentBook, notices):
    found(book, ALICE, "AAA", RED)

    announce(book, request("0.10"), request("0.05", MeasureKind.DAY_TRADE_RATE))

    party = party_of(book, ALICE)
    assert [p.kind for p in party.promises] == [
        MeasureKind.STOCK_PROFIT_RATE,
        MeasureKind.DAY_TRADE_RATE,
    ]
    assert party.promises[0].baseline == BASELINE
    assert party.promises[0].announced == CAMPAIGN_OPEN
    assert notices[-1]["kind"] == GovernmentNoticeKind.PROMISES_SET.value
    with pytest.raises(UnprocessableEntityError, match="No máximo 3"):
        announce(book, *[request(f"0.{n}") for n in range(1, 5)])


def test_only_the_founder_announces(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, ALICE).id, Decimal(0))

    with pytest.raises(ForbiddenError):
        book.set_promises(BOB, CAMPAIGN_OPEN, [request()])


@pytest.mark.parametrize(
    ("items", "message"),
    [
        ([request("0.15")], "já é o valor em vigor"),
        ([request("1.5")], "alvo válido"),
        ([request("0.10"), request("0.05")], "mesma medida"),
        (
            [PromiseRequest(kind=MeasureKind.SECTOR_TAX, sector="Energia")],
            "não se promete",
        ),
        (
            [PromiseRequest(kind=MeasureKind.SECTOR_EXEMPT, sector="Inexistente")],
            "Setor não encontrado",
        ),
    ],
)
def test_invalid_promises_are_refused(
    book: GovernmentBook, engine, items: list[PromiseRequest], message: str
):
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED)

    with pytest.raises(
        (ConflictError, UnprocessableEntityError, NotFoundError), match=message
    ):
        book.set_promises(ALICE, CAMPAIGN_OPEN, items)


def test_the_list_locks_when_the_tickets_close(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    announce(book, request())

    with pytest.raises(ConflictError, match="travam"):
        announce(book, request("0.12"), day=date(2021, 10, 1))
    with pytest.raises(ConflictError, match="não mudaram"):
        announce(book, request())


def test_a_promise_pays_support_in_the_groups_that_want_it(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    party = party_of(book, ALICE)
    before = {g: party.standing(g).support for g in VoterGroup}

    announce(book, request())

    cut = party.promises[0]
    for group in VoterGroup:
        gained = party.standing(group).support - before[group]
        assert gained == promises.yield_of(cut, group, party.rejection[group])


def test_retreating_after_the_announcement_adds_rejection_where_it_was_wanted(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED)
    announce(book, request())
    party = party_of(book, ALICE)
    cut = party.promises[0]
    before = dict(party.rejection)

    announce(book)

    assert party.promises == []
    for group in VoterGroup:
        expected = promises.retreat(cut, None)[group]
        assert party.rejection[group] == voters.add_rejection(before[group], expected)


def test_raising_the_target_costs_nothing(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    announce(book, request("0.12"))
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    announce(book, request("0.05"))

    assert party.rejection == before
    # O "era" e o dia do anúncio ficam: só o alvo anda
    assert party.promises[0].baseline == BASELINE
    assert party.promises[0].announced == CAMPAIGN_OPEN


def test_preview_lists_each_promise_and_the_cost_of_withdrawing(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    announce(book, request())
    party = party_of(book, ALICE)

    drafts = book.draft_promises(ALICE, CAMPAIGN_OPEN, [])
    preview = build_preview(book, ALICE, CAMPAIGN_OPEN, drafts)

    assert preview.items == []
    wanting = next(g for g in VoterGroup if promises.wanted(g, party.promises[0]) > 0)
    cost = next(t.retreat for t in preview.totals if t.group is wanting)
    assert cost == promises.retreat(party.promises[0], None)[wanting]


# Mandato


def govern_promising(book: GovernmentBook, engine, *items: PromiseRequest, vice=False):
    """Alice anuncia as promessas, vence a eleição e toma posse; com `vice`, Bob é o vice."""
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    if vice:
        book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, ALICE).id, Decimal(0))
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)
        book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    announce(book, *items)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)


def test_the_elected_ticket_takes_its_promises_to_the_term(
    book: GovernmentBook, engine
):
    govern_promising(book, engine, request())

    term = book.state.term
    assert term is not None
    assert [p.kind for p in term.promises] == [MeasureKind.STOCK_PROFIT_RATE]
    party = party_of(book, ALICE)
    # A lista da campanha vai para o histórico, sem efeito
    assert party.promises == []
    [record] = party.past_promises
    assert record.elected is True and record.year == 2021
    # O resultado guarda as promessas que a chapa levou à urna
    first = book.state.results[0]
    assert [p.kind for p in first.tickets[party.id].promises] == [
        MeasureKind.STOCK_PROFIT_RATE
    ]


def test_the_losing_party_keeps_its_promises_in_the_history_without_effect(
    book: GovernmentBook, engine
):
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    # Sem verba e sem votos: o computador ganha
    found(book, BOB, "BBB", "#2563eb", "0")
    book.set_promises(BOB, CAMPAIGN_OPEN, [request("0.12")])
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)

    bob = party_of(book, BOB)
    assert bob.promises == []
    assert len(bob.past_promises) == 1
    pending = book.state.pending_term
    assert pending is not None and pending.party_id != bob.id
    assert pending.promises == ()


def propose_cut(book: GovernmentBook, value="0.10") -> None:
    book.propose(
        ALICE, TERM_START, MeasureKind.STOCK_PROFIT_RATE, Decimal(value), None, None
    )


def test_term_end_settles_a_kept_promise_with_loyalty_and_repair(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern_promising(book, engine, request())
    party = party_of(book, ALICE)
    rejection = dict(party.rejection)
    propose_cut(book)
    congress_says(monkeypatch, True)
    close_months(book, 1)

    book.on_tick(USERS, date(2025, 12, 31), False)

    [balance] = book.state.balances
    [item] = balance.items
    assert item.done == 1
    assert balance.impeached is False
    kept = promises.settle(item.promise, Decimal(1))
    for group in VoterGroup:
        assert party.loyalty[group] == kept[group].loyalty
        assert party.rejection[group] == voters.clamp(
            rejection[group] + kept[group].rejection
        )
    term = book.state.term
    assert term is not None and term.settled


def test_term_end_charges_a_broken_promise(book: GovernmentBook, engine, market):
    govern_promising(book, engine, request())
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    book.on_tick(USERS, date(2025, 12, 31), False)

    [balance] = book.state.balances
    assert balance.items[0].done == 0
    broken = promises.settle(balance.items[0].promise, ZERO)
    for group in VoterGroup:
        assert party.loyalty[group] == 0
        # O fechamento do mês de 31 dez, no mesmo dia, pode reparar até um quarto de ponto
        expected = voters.clamp(before[group] + broken[group].rejection)
        assert abs(party.rejection[group] - expected) <= voters.APPROVED_REPAIR


def test_the_settlement_runs_once(book: GovernmentBook, engine, market, notices):
    govern_promising(book, engine, request())

    book.on_tick(USERS, date(2025, 12, 31), False)
    book.on_tick(USERS, date(2026, 1, 2), False)

    assert len(book.state.balances) == 1
    kinds = [n["kind"] for n in notices]
    assert kinds.count(GovernmentNoticeKind.PROMISES_SETTLED.value) == 1


def test_half_of_the_balance_weighs_on_the_vote_and_the_settlement_closes_the_rest(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern_promising(book, engine, request())
    propose_cut(book)
    congress_says(monkeypatch, True)
    close_months(book, 1)
    party = party_of(book, ALICE)

    # Pula para o ciclo da reeleição: as chapas fecham em 30 set 2025
    book.state.cycle = 1
    book.on_tick(USERS, date(2025, 10, 1), False)

    term = book.state.term
    assert term is not None and term.weighed
    kept = promises.settle(term.promises[0], Decimal(1))
    for group in VoterGroup:
        assert term.applied[group].loyalty == kept[group].loyalty / 2
        assert party.loyalty[group] == kept[group].loyalty / 2

    book.on_tick(USERS, date(2025, 12, 31), False)

    # Metade antes e metade no balanço: o total é uma vez só
    for group in VoterGroup:
        assert party.loyalty[group] == kept[group].loyalty


def test_replay_rebuilds_the_promises_loyalty_and_balances(
    book: GovernmentBook, engine, market, stored, monkeypatch
):
    govern_promising(book, engine, request())
    propose_cut(book)
    congress_says(monkeypatch, True)
    close_months(book, 1)
    book.on_tick(USERS, date(2025, 12, 31), False)

    state = replay(stored)

    original = party_of(book, ALICE)
    rebuilt: Party = state.parties[original.id]
    assert rebuilt.loyalty == original.loyalty
    assert rebuilt.rejection == original.rejection
    assert rebuilt.past_promises == original.past_promises
    assert state.balances == book.state.balances


def test_the_term_card_shows_the_state_of_each_promise(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern_promising(book, engine, request())

    card = build_term_promises(book, ALICE, TERM_START)
    assert card is not None
    assert [(i.state, i.done) for i in card.items] == [(PromiseState.UNTOUCHED, 0)]
    assert card.items[0].current == BASELINE
    assert len(card.projection) == len(VoterGroup)
    # Quem não é do partido vê o estado, sem os números por grupo
    outsider = build_term_promises(book, BOB, TERM_START)
    assert outsider is not None and outsider.projection == []

    propose_cut(book)
    congress_says(monkeypatch, True)
    close_months(book, 1)
    card = build_term_promises(book, ALICE, date(2022, 6, 1))
    assert card is not None
    assert card.items[0].state is PromiseState.FULFILLED
    assert card.items[0].current == TARGET
    # O último voto que ainda vale: 90 dias antes do fim do mandato
    assert card.last_vote == date(2025, 9, 30)


def test_balance_hides_the_group_numbers_from_outsiders(
    book: GovernmentBook, engine, market
):
    govern_promising(book, engine, request())
    book.on_tick(USERS, date(2025, 12, 31), False)

    [mine] = build_balances(book, ALICE)
    [theirs] = build_balances(book, BOB)

    assert mine.totals and mine.items[0].effects
    assert theirs.totals == [] and theirs.items[0].effects == []
    assert theirs.items[0].state is PromiseState.UNTOUCHED


def test_impeachment_without_a_vice_closes_the_balance_with_the_party(
    book: GovernmentBook, engine, market, bleak
):
    govern_promising(book, engine, request())
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    assert close_months(book, 18) == PauseReason.IMPEACHMENT

    [balance] = book.state.balances
    assert balance.impeached is True
    assert any(party.rejection[g] > before[g] for g in VoterGroup)
    term = book.state.term
    assert term is not None and term.promises == ()


def test_the_vice_inherits_the_promises_after_an_impeachment(
    book: GovernmentBook, engine, market, bleak
):
    govern_promising(book, engine, request(), vice=True)

    assert close_months(book, 18) == PauseReason.IMPEACHMENT

    term = book.state.term
    assert term is not None and term.president_id == BOB.id
    assert [p.kind for p in term.promises] == [MeasureKind.STOCK_PROFIT_RATE]
    assert book.state.balances == []

    book.on_tick(USERS, date(2025, 12, 31), False)
    [balance] = book.state.balances
    assert balance.party_id == party_of(book, ALICE).id


def test_computer_parties_promise_by_rule_and_are_not_charged(
    book: GovernmentBook, engine
):
    found(book, ALICE, "AAA", RED, "10000")

    run_campaign(book)

    computers = book.state.computer_parties()
    assert computers
    for computer in computers:
        assert 0 < len(computer.promises) <= promises.COMPUTER_PROMISES
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)
    term = book.state.term
    if term is not None and term.party_id in {c.id for c in computers}:
        book.on_tick(USERS, date(2025, 12, 31), False)
        assert book.state.balances == []
