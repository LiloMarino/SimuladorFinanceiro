"""Federações partidárias: regras puras, proposta e resposta no livro, saída com impedimento, computador e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core.enum import (
    FederationProposalStatus,
    FederationStatus,
    GovernmentNoticeKind,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.government import federations, house
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_panel
from tests.test_government_book import (
    ALICE,
    BLUE,
    BOB,
    CAMPAIGN_OPEN,
    CARLA,
    GREEN,
    RED,
    SEED,
    USERS,
    book,
    engine,
    found,
    headlines,
    notices,
    office,
    party_of,
    settings,
    stored,
)

TODAY = CAMPAIGN_OPEN
LATER = TODAY + timedelta(days=1)

# Regras puras


def test_default_name_joins_the_abbreviations_with_a_dash():
    assert federations.default_name("AAA", "BBB") == "Federação AAA–BBB"  # noqa: RUF001


def test_proposal_lasts_seven_days():
    assert federations.expires_on(date(2020, 10, 7)) == date(2020, 10, 14)


def test_orientation_goes_to_the_party_with_more_seats_and_otherwise_to_the_proposer():
    assert federations.orientation_party((1, 2), {1: 10, 2: 30}) == 2
    assert federations.orientation_party((1, 2), {1: 30, 2: 10}) == 1
    # Empate e ausência de cadeira ficam com quem propôs
    assert federations.orientation_party((1, 2), {1: 20, 2: 20}) == 1
    assert federations.orientation_party((1, 2), {}) == 1


def test_each_party_feels_half_of_the_partner_rejection_up_to_one_hundred():
    assert federations.effective_rejection(Decimal(20), [Decimal(40)]) == 40
    assert federations.effective_rejection(Decimal(90), [Decimal(80)]) == 100


def test_flags_are_compatible_with_one_in_common_and_none_opposed():
    free, social = VoterValue.FREE_MARKET, VoterValue.SOCIAL_JUSTICE
    stability = VoterValue.STABILITY

    assert federations.compatible([free, stability], [stability])
    assert not federations.compatible([free], [stability])
    assert federations.opposed([free, stability], [social, stability])
    assert not federations.compatible([free, stability], [social, stability])


def test_computer_accepts_only_below_the_barrier_with_compatible_flags():
    mine = [VoterValue.STABILITY, VoterValue.DEVELOPMENT]
    proposer = [VoterValue.STABILITY]

    assert federations.computer_accepts(True, mine, proposer)
    assert not federations.computer_accepts(False, mine, proposer)
    assert not federations.computer_accepts(True, mine, [VoterValue.FREE_MARKET])


def test_computer_picks_the_most_flags_in_common_and_then_the_most_votes():
    flags = [VoterValue.STABILITY, VoterValue.DEVELOPMENT, VoterValue.FREE_MARKET]
    options = [
        (1, [VoterValue.STABILITY], Decimal("0.30")),
        (2, [VoterValue.STABILITY, VoterValue.DEVELOPMENT], Decimal("0.05")),
        (3, [VoterValue.STABILITY, VoterValue.DEVELOPMENT], Decimal("0.10")),
        (4, [VoterValue.SOCIAL_JUSTICE, VoterValue.STABILITY], Decimal("0.50")),
    ]

    assert federations.computer_partner(flags, options) == 3
    assert (
        federations.computer_partner(
            flags, [(9, [VoterValue.SOCIAL_JUSTICE], Decimal(1))]
        )
        is None
    )


# Proposta e resposta


def pair(book: GovernmentBook):
    """Alice (AAA) e Bob (BBB) fundam; devolve os dois partidos."""
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    return party_of(book, ALICE), party_of(book, BOB)


def last_id(book: GovernmentBook) -> int:
    """A proposta mais recente da partida."""
    return max(book.state.proposals)


def propose(book: GovernmentBook, alice, bob, day=TODAY, candidate_party=None):
    book.propose_federation(
        ALICE,
        day,
        bob.id,
        "Frente",
        (candidate_party or alice).id,
        "Alice" if (candidate_party or alice) is alice else "Bob",
        USERS,
    )


def test_an_accepted_proposal_forms_the_federation_for_the_current_election(
    book: GovernmentBook, headlines
):
    alice, bob = pair(book)
    propose(book, alice, bob)

    assert book.sent_federation(alice, TODAY) is not None
    assert len(book.received_federations(bob, TODAY)) == 1

    book.answer_federation(BOB, LATER, True, last_id(book))

    federation = book.state.federation_of(alice.id, book.state.cycle)
    assert federation is not None
    assert federation is book.state.federation_of(bob.id, book.state.cycle)
    assert federation.parties == (alice.id, bob.id)
    assert (federation.name, federation.candidate_party_id) == ("Frente", alice.id)
    assert federation.in_force_from == LATER
    # Vale até a véspera da posse depois da eleição seguinte
    assert federation.ends_on == book.cycle(
        book.state.cycle + 1
    ).inauguration - timedelta(days=1)
    assert book.sent_federation(alice, LATER) is None
    # A manchete tem duas redações, sorteadas pela semente
    assert any(
        w in headlines[-1][1].text for w in ("formam federação", "Federação nova")
    )


def test_the_proposal_notice_goes_to_the_founder_of_the_guest(
    book: GovernmentBook, notices
):
    alice, bob = pair(book)
    notices.clear()
    propose(book, alice, bob)

    assert [(n["kind"], n["party_abbr"], n["partner_abbr"]) for n in notices] == [
        (GovernmentNoticeKind.FEDERATION_PROPOSED.value, "AAA", "BBB")
    ]


def test_the_candidate_party_leads_and_the_candidate_is_one_of_its_members(
    book: GovernmentBook,
):
    alice, bob = pair(book)

    propose(book, alice, bob, candidate_party=bob)
    proposal = book.sent_federation(alice, TODAY)
    assert proposal is not None
    assert (proposal.candidate_party_id, proposal.candidate_id) == (bob.id, BOB.id)

    book.withdraw_federation(ALICE, TODAY)
    with pytest.raises(NotFoundError, match="filiado"):
        book.propose_federation(ALICE, TODAY, bob.id, "Frente", bob.id, "Alice", USERS)


def test_proposal_rules(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)
    alice, bob, carla = (party_of(book, u) for u in (ALICE, BOB, CARLA))

    with pytest.raises(ConflictError, match="com ele mesmo"):
        book.propose_federation(
            ALICE, TODAY, alice.id, "Frente", alice.id, "Alice", USERS
        )
    with pytest.raises(UnprocessableEntityError, match="dos dois partidos"):
        book.propose_federation(
            ALICE, TODAY, bob.id, "Frente", carla.id, "Carla", USERS
        )
    with pytest.raises(UnprocessableEntityError, match="nome"):
        book.propose_federation(ALICE, TODAY, bob.id, "  ", alice.id, "Alice", USERS)

    propose(book, alice, bob)
    # Quem envia tem uma proposta aberta por vez; quem recebe pode ter várias
    with pytest.raises(ConflictError, match="proposta"):
        book.propose_federation(
            ALICE, TODAY, carla.id, "Outra", alice.id, "Alice", USERS
        )
    book.propose_federation(CARLA, TODAY, bob.id, "Outra", carla.id, "Carla", USERS)
    assert len(book.received_federations(bob, TODAY)) == 2


def test_accepting_one_proposal_declines_the_other_and_withdraws_the_one_sent(
    book: GovernmentBook, notices
):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)
    alice, bob, carla = (party_of(book, u) for u in (ALICE, BOB, CARLA))
    book.on_tick(USERS, TODAY, False)
    propose(book, alice, bob)
    first = last_id(book)
    book.propose_federation(CARLA, TODAY, bob.id, "Outra", carla.id, "Carla", USERS)
    second = last_id(book)
    # Bob também envia uma proposta, que cai quando ele aceitar outra
    book.propose_federation(BOB, TODAY, alice.id, "Dele", bob.id, "Bob", USERS)
    sent = last_id(book)

    book.answer_federation(BOB, LATER, True, first)

    proposals = book.state.proposals
    assert proposals[first].status is FederationProposalStatus.ACCEPTED
    assert proposals[second].status is FederationProposalStatus.DECLINED
    assert proposals[sent].status is FederationProposalStatus.WITHDRAWN
    assert book.received_federations(bob, LATER) == []
    taken = [
        n for n in notices if n["kind"] == GovernmentNoticeKind.FEDERATION_TAKEN.value
    ]
    assert [n["target"] for n in taken] == ["Carla"]


def test_only_the_founder_proposes_and_answers(book: GovernmentBook):
    alice, bob = pair(book)
    book.join_party(CARLA, TODAY, alice.id, Decimal(0))

    with pytest.raises(ForbiddenError):
        book.propose_federation(
            CARLA, TODAY, bob.id, "Frente", alice.id, "Carla", USERS
        )

    propose(book, alice, bob)
    with pytest.raises(NotFoundError, match="proposta"):
        book.answer_federation(ALICE, LATER, True, last_id(book))


def test_a_proposal_expires_after_seven_days(book: GovernmentBook):
    alice, bob = pair(book)
    propose(book, alice, bob)

    with pytest.raises(NotFoundError, match="proposta"):
        book.answer_federation(BOB, TODAY + timedelta(days=8), True, last_id(book))
    assert book.state.federation_of(alice.id, book.state.cycle) is None


def test_declining_costs_nothing_and_frees_both_to_propose_again(book: GovernmentBook):
    alice, bob = pair(book)
    propose(book, alice, bob)

    book.answer_federation(BOB, LATER, False, last_id(book))

    assert book.state.federation_of(alice.id, book.state.cycle) is None
    proposal = next(iter(book.state.proposals.values()))
    assert proposal.status is FederationProposalStatus.DECLINED
    propose(book, alice, bob, day=LATER)


def test_withdrawing_closes_the_sent_proposal(book: GovernmentBook):
    alice, bob = pair(book)
    propose(book, alice, bob)

    book.withdraw_federation(ALICE, TODAY)

    assert book.sent_federation(alice, TODAY) is None
    with pytest.raises(ConflictError, match="retirar"):
        book.withdraw_federation(ALICE, TODAY)


def test_a_second_federation_is_scheduled_for_the_next_election(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)
    alice, bob, carla = (party_of(book, u) for u in (ALICE, BOB, CARLA))
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))

    # Alice já tem federação nesta eleição: a nova vale para a seguinte
    book.propose_federation(ALICE, LATER, carla.id, "Depois", alice.id, "Alice", USERS)
    book.answer_federation(CARLA, LATER + timedelta(days=1), True, last_id(book))

    now, next_one = (
        book.state.federation_of(alice.id, c)
        for c in (book.state.cycle, book.state.cycle + 1)
    )
    assert now is not None and next_one is not None
    assert next_one.cycle == book.state.cycle + 1
    # A agendada só entra no Congresso na posse em que a atual acaba
    assert next_one.in_force_from == now.ends_on + timedelta(days=1)
    assert not next_one.in_congress(LATER)
    # Um terceiro pedido, com as duas eleições preenchidas, não cabe
    with pytest.raises(ConflictError, match="esta eleição e para a seguinte"):
        book.propose_federation(ALICE, LATER, bob.id, "Mais", alice.id, "Alice", USERS)


# Sair, impedimento e dissolução


def test_leaving_undoes_it_for_both_and_bans_the_one_who_left(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)
    alice, bob, carla = (party_of(book, u) for u in (ALICE, BOB, CARLA))
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))
    federation = book.state.federation_of(alice.id, book.state.cycle)
    assert federation is not None

    book.leave_federation(BOB, LATER)

    assert federation.status is FederationStatus.LEFT
    assert book.federation_in_effect(alice.id, LATER) is None
    assert book.federation_in_effect(bob.id, LATER) is None
    # Quem saiu não se federa na eleição seguinte; quem ficou segue livre
    with pytest.raises(ConflictError, match="saiu de uma federação"):
        book.propose_federation(BOB, LATER, carla.id, "Frente", bob.id, "Bob", USERS)
    with pytest.raises(ConflictError, match="saiu de uma federação"):
        propose(book, alice, bob, day=LATER)
    book.propose_federation(ALICE, LATER, carla.id, "Outra", alice.id, "Alice", USERS)


def test_leaving_also_voids_the_scheduled_federation_and_open_proposals(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)
    alice, bob, carla = (party_of(book, u) for u in (ALICE, BOB, CARLA))
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))
    book.propose_federation(ALICE, LATER, carla.id, "Depois", alice.id, "Alice", USERS)
    book.answer_federation(CARLA, LATER + timedelta(days=1), True, last_id(book))

    book.leave_federation(BOB, LATER + timedelta(days=2))

    assert book.state.federation_of(alice.id, book.state.cycle + 1) is None
    assert book.state.federation_of(carla.id, book.state.cycle + 1) is None


def test_leaving_without_a_federation_is_refused(book: GovernmentBook):
    pair(book)

    with pytest.raises(NotFoundError, match="não está em nenhuma federação"):
        book.leave_federation(ALICE, TODAY)


def test_the_federation_dissolves_when_a_party_dissolves(book: GovernmentBook):
    alice, bob = pair(book)
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))

    book.leave_party(BOB, LATER)

    assert book.federation_in_effect(alice.id, LATER) is None


# Retomada


def test_resumed_game_has_the_same_federations_and_ban(
    book: GovernmentBook, engine, stored, notices, captured_events
):
    alice, bob = pair(book)
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))
    book.leave_federation(BOB, LATER)

    resumed = GovernmentBook(
        settings(),
        engine,
        lambda *_: None,
        lambda *_: Decimal(0),
        lambda *_: None,
        SEED,
    )

    assert resumed.state.federations == book.state.federations
    assert resumed.state.proposals == book.state.proposals
    assert resumed.state.blocked == book.state.blocked


# Computador


def test_computer_answers_the_day_after_and_accepts_when_it_fits(
    book: GovernmentBook, monkeypatch: pytest.MonkeyPatch
):
    found(book, ALICE, "AAA", RED)
    alice = party_of(book, ALICE)
    computer = next(
        p
        for p in book.state.computer_parties()
        if federations.compatible(p.flags, alice.flags)
    )
    # Todos ficam abaixo da barreira
    monkeypatch.setattr(house, "BARRIER", Decimal("0.99"))
    book.propose_federation(
        ALICE, TODAY, computer.id, "Frente", alice.id, "Alice", USERS
    )

    # No mesmo dia nada muda; no seguinte o computador responde
    book.on_tick(USERS, TODAY, False)
    assert book.state.federation_of(alice.id, book.state.cycle) is None
    book.on_tick(USERS, LATER, False)

    federation = book.state.federation_of(alice.id, book.state.cycle)
    assert federation is not None and federation.includes(computer.id)


def test_computer_declines_when_it_would_pass_the_barrier_alone(
    book: GovernmentBook, monkeypatch: pytest.MonkeyPatch
):
    found(book, ALICE, "AAA", RED)
    alice = party_of(book, ALICE)
    computer = book.state.computer_parties()[0]
    monkeypatch.setattr(house, "BARRIER", Decimal(0))
    book.propose_federation(
        ALICE, TODAY, computer.id, "Frente", alice.id, "Alice", USERS
    )

    book.on_tick(USERS, LATER, False)

    assert book.state.federation_of(alice.id, book.state.cycle) is None
    proposal = next(iter(book.state.proposals.values()))
    assert proposal.status is FederationProposalStatus.DECLINED


def test_computer_below_the_barrier_proposes_at_the_month_close(
    book: GovernmentBook, monkeypatch: pytest.MonkeyPatch
):
    found(book, ALICE, "AAA", RED)
    monkeypatch.setattr(house, "BARRIER", Decimal("0.99"))

    book._propose_computer_federations(TODAY)

    proposals = [p for p in book.state.proposals.values() if p.is_open(TODAY)]
    assert proposals
    for proposal in proposals:
        sender = book.state.parties[proposal.from_party_id]
        receiver = book.state.parties[proposal.to_party_id]
        assert sender.is_computer
        assert federations.compatible(sender.flags, receiver.flags)
        # A chapa é do parceiro que o computador procurou
        assert proposal.candidate_party_id == receiver.id
    # Cada partido do computador envia uma proposta por vez
    senders = [p.from_party_id for p in proposals]
    assert len(senders) == len(set(senders))


def test_computer_above_the_barrier_does_not_propose(
    book: GovernmentBook, monkeypatch: pytest.MonkeyPatch
):
    found(book, ALICE, "AAA", RED)
    monkeypatch.setattr(house, "BARRIER", Decimal(0))

    book._propose_computer_federations(TODAY)

    assert book.state.proposals == {}


# Painel


def test_panel_carries_the_proposal_end_and_the_orienting_party(book: GovernmentBook):
    alice, bob = pair(book)
    propose(book, alice, bob)
    networths = {u.id: Decimal(0) for u in USERS}

    sent = build_panel(book, settings(), USERS, ALICE, TODAY, networths).sent_proposal
    [received] = build_panel(
        book, settings(), USERS, BOB, TODAY, networths
    ).received_proposals

    assert sent is not None
    assert sent.id == received.id
    assert sent.ends_on == book.cycle(book.state.cycle + 1).inauguration - timedelta(
        days=1
    )
    assert sent.orienting_party_id == alice.id


def test_only_the_leader_party_edits_the_ticket_of_the_federation(
    book: GovernmentBook,
):
    alice, bob = pair(book)
    propose(book, alice, bob)
    book.answer_federation(BOB, LATER, True, last_id(book))
    networths = {u.id: Decimal(0) for u in USERS}

    leader = build_panel(book, settings(), USERS, ALICE, CAMPAIGN_OPEN, networths)
    partner = build_panel(book, settings(), USERS, BOB, CAMPAIGN_OPEN, networths)

    assert leader.can_edit_ticket
    assert not partner.can_edit_ticket
