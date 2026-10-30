"""Os acordos de apoio por emenda no livro do governo: proposta, resposta, orientação, orçamento, quebra e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from backend.core.enum import (
    DealBreaker,
    DealStatus,
    GovernmentNoticeKind,
    PendingType,
    VoterGroup,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from backend.features.government import base_panel, deals, house
from backend.features.government import state as government_state
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import replay
from tests.test_government_book import (
    ALICE,
    BLUE,
    BOB,
    CAMPAIGN_OPEN,
    FIRST_VOTE,
    NICHE,
    TERM_START,
    USERS,
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

MNV = house.COMPUTER_KEYS["MNV"]
ACI = house.COMPUTER_KEYS["ACI"]
UPR = house.COMPUTER_KEYS["UPR"]
NEXT_DAY = TERM_START + timedelta(days=1)


def deal_with(book: GovernmentBook, key: int) -> deals.Deal:
    return next(d for d in book.state.deals.values() if d.bloc_key == key)


def seats_of(book: GovernmentBook, key: int) -> int:
    bloc = book.state.house_on(TERM_START).bloc(key)
    assert bloc is not None
    return bloc.seats


def ally_deal(book: GovernmentBook, key: int = MNV) -> deals.Deal:
    """O computador aceita a proposta no pregão seguinte: devolve o acordo em vigor."""
    book.propose_deal(ALICE, TERM_START, key)
    book.on_tick(USERS, NEXT_DAY, False)
    return deal_with(book, key)


# Proposta e resposta do computador


def test_the_computer_answers_in_the_next_session_and_accepts_with_two_shared_flags(
    book: GovernmentBook, engine, market, notices
):
    govern(book, engine)

    book.propose_deal(ALICE, TERM_START, MNV)

    deal = deal_with(book, MNV)
    assert deal.status is DealStatus.PENDING
    assert deal.answer_by is None
    book.on_tick(USERS, NEXT_DAY, False)
    assert deal.status is DealStatus.ACTIVE
    assert deal.start == NEXT_DAY
    assert deal.end == deals.last_day(NEXT_DAY, book.term_end())
    assert deal.ratio == deals.price("MNV", seats_of(book, MNV))
    answered = [
        n for n in notices if n.get("kind") == GovernmentNoticeKind.DEAL_ANSWERED.value
    ]
    assert answered and answered[-1]["accepted"] is True


def test_the_computer_declines_when_it_shares_fewer_than_two_flags(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    book.propose_deal(ALICE, TERM_START, ACI)
    book.on_tick(USERS, NEXT_DAY, False)

    assert deal_with(book, ACI).status is DealStatus.DECLINED
    assert book.state.deals_in_force(NEXT_DAY) == []


def test_the_centrao_always_accepts_and_pays_one_and_a_half_times(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    deal = ally_deal(book, UPR)

    assert deal.status is DealStatus.ACTIVE
    assert deal.ratio == deals.price("UPR", seats_of(book, UPR))
    assert deal.ratio == deals.SEAT_PRICE * seats_of(book, UPR) * Decimal("1.5")


def test_a_refusal_closes_the_door_for_thirty_days(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    book.propose_deal(ALICE, TERM_START, ACI)
    book.on_tick(USERS, NEXT_DAY, False)
    bloc = book.state.house_on(NEXT_DAY).bloc(ACI)
    assert bloc is not None

    blocker = book.deal_blocker(bloc, NEXT_DAY)
    assert blocker is not None
    assert blocker[1] == NEXT_DAY + timedelta(days=30)
    with pytest.raises(ConflictError, match="recusou"):
        book.propose_deal(ALICE, NEXT_DAY, ACI)
    assert book.deal_blocker(bloc, NEXT_DAY + timedelta(days=30)) is None


def test_only_the_president_proposes_and_never_to_the_own_party(
    book: GovernmentBook, engine, market
):
    govern(book, engine, vice=True)
    own = book.state.house_on(TERM_START).of_party(party_of(book, ALICE).id)
    assert own is not None

    with pytest.raises(ForbiddenError):
        book.propose_deal(BOB, TERM_START, MNV)
    with pytest.raises(ConflictError, match="já é a base"):
        book.propose_deal(ALICE, TERM_START, own.key)
    with pytest.raises(NotFoundError):
        book.propose_deal(ALICE, TERM_START, 9999)


def test_a_pending_proposal_blocks_another_to_the_same_bloc_and_can_be_withdrawn(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    book.propose_deal(ALICE, TERM_START, MNV)

    with pytest.raises(ConflictError, match="espera"):
        book.propose_deal(ALICE, TERM_START, MNV)
    book.withdraw_deal(ALICE, TERM_START, deal_with(book, MNV).id)
    book.on_tick(USERS, NEXT_DAY, False)

    assert deal_with(book, MNV).status is DealStatus.WITHDRAWN
    assert book.state.deals_in_force(NEXT_DAY) == []


def test_a_deal_in_force_blocks_a_new_one_until_the_last_month(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    bloc = book.state.house_on(NEXT_DAY).bloc(MNV)
    assert bloc is not None
    assert deal.end is not None

    assert book.deal_blocker(bloc, NEXT_DAY) is not None
    renewal = deal.end - timedelta(days=deals.RENEW_DAYS)
    assert book.deal_blocker(bloc, renewal) is None


# Base, orientação e votação


def test_the_base_adds_the_deal_seats_to_the_government_bloc(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    own = book.governing_bloc(TERM_START)
    assert own is not None
    assert book.base_seats(NEXT_DAY) == own.seats

    ally_deal(book)

    assert book.base_seats(NEXT_DAY) == own.seats + seats_of(book, MNV)


def test_the_bloc_with_a_deal_is_guided_yes_on_every_government_measure(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    ally_deal(book)
    propose(book)
    measure = book.state.measures[1]

    orientations, guided, _ = book.measure_orientations(measure, NEXT_DAY)

    assert (orientations[MNV], guided[MNV]) == (True, True)
    assert guided[ACI] is False


def test_a_computer_bloc_without_a_deal_keeps_its_own_orientation(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book)

    _, guided, _ = book.measure_orientations(book.state.measures[1], NEXT_DAY)

    assert guided[MNV] is False


# Orçamento


def test_the_amendment_is_spending_from_the_closing_after_the_deal_started(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    closing = date(2022, 1, 31)

    assert book.state.amendments_on(closing) == deal.ratio
    assert book.spending_on(closing) == book.spending_timeline().spending_on(
        closing
    ) + Decimal(deal.ratio)
    # O fechamento do dia da proposta ainda não conta o acordo
    assert book.state.amendments_on(TERM_START) == 0


def test_the_amendment_stops_after_the_last_day_of_the_deal(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    assert deal.end is not None

    assert book.state.amendments_on(deal.end + timedelta(days=1)) == deal.ratio
    assert book.state.amendments_on(deal.end + timedelta(days=2)) == 0


def test_the_budget_lists_the_amendments_the_last_closing_counted(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    book.on_tick(USERS, FIRST_VOTE, True)

    lines = book.amendment_lines(FIRST_VOTE + timedelta(days=1))

    assert lines == [("MNV", deal.ratio)]


CLOSINGS = [date(2022, 2, 28), date(2022, 3, 31)]


@pytest.fixture
def projection(book: GovernmentBook, monkeypatch: pytest.MonkeyPatch) -> None:
    """A dívida projetada vira a soma do gasto dos dois fechamentos: o teste lê só o que o acordo soma."""

    def project(_start, _end, *_, spending_on=None, **__):
        spending = spending_on or book.spending_on
        return [SimpleNamespace(debt=sum((spending(d) for d in CLOSINGS), Decimal(0)))]

    monkeypatch.setattr(book.budget(), "project", project)


def test_the_debt_projection_counts_the_deal_spending_inside_its_term(
    book: GovernmentBook, engine, market, projection
):
    govern(book, engine)
    ratio = deals.price("MNV", seats_of(book, MNV))

    debt = book.deal_debt(ratio, TERM_START)

    assert debt is not None
    before, after, _ = debt
    assert after - before == ratio * len(CLOSINGS)


# Quebra


def test_the_government_breaking_the_deal_ends_it_and_the_ally_groups_blame_the_government(
    book: GovernmentBook, engine, market, notices, headlines
):
    govern(book, engine)
    deal = ally_deal(book)
    bloc = book.state.house_on(NEXT_DAY).bloc(MNV)
    assert bloc is not None
    party = party_of(book, ALICE)
    before = dict(party.rejection)
    day = NEXT_DAY + timedelta(days=10)

    book.break_deal(ALICE, day, deal.id)

    assert deal.status is DealStatus.BROKEN
    assert deal.broken_by is DealBreaker.GOVERNMENT
    assert deal.end == day
    assert book.state.deal_of(MNV, day + timedelta(days=1)) is None
    top = deals.strongest_groups(bloc.mix, 1)[0]
    assert party.rejection[top] > before[top]
    assert any(n.get("kind") == GovernmentNoticeKind.DEAL_BROKEN.value for n in notices)
    assert headlines


def test_only_a_deal_in_force_can_be_broken_and_only_by_the_president(
    book: GovernmentBook, engine, market
):
    govern(book, engine, vice=True)
    deal = ally_deal(book)

    with pytest.raises(ForbiddenError):
        book.break_deal(BOB, NEXT_DAY, deal.id)
    book.break_deal(ALICE, NEXT_DAY, deal.id)
    with pytest.raises(ConflictError, match="vigor"):
        book.break_deal(ALICE, NEXT_DAY, deal.id)


def test_the_deal_ends_without_a_break_when_its_term_runs_out(
    book: GovernmentBook, engine, market, notices, headlines
):
    govern(book, engine)
    deal = ally_deal(book)
    assert deal.end is not None
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    book.on_tick(USERS, deal.end, False)
    book.on_tick(USERS, deal.end + timedelta(days=1), False)

    assert deal.status is DealStatus.ACTIVE
    assert book.state.deal_of(MNV, deal.end + timedelta(days=1)) is None
    assert party.rejection == before
    ended = [
        n for n in notices if n.get("kind") == GovernmentNoticeKind.DEAL_ENDED.value
    ]
    assert len(ended) == 1


def test_a_new_government_inherits_an_empty_base(book: GovernmentBook, engine, market):
    govern(book, engine)
    deal = ally_deal(book)
    book.propose_deal(ALICE, NEXT_DAY, UPR)
    pending = deal_with(book, UPR)

    government_state._cut_deals(book.state, NEXT_DAY + timedelta(days=5))

    assert deal.status is DealStatus.CUT
    assert deal.end == NEXT_DAY + timedelta(days=4)
    assert pending.status is DealStatus.WITHDRAWN


# Retomada


def test_a_resumed_game_rebuilds_the_deals_and_the_spending(
    book: GovernmentBook, engine, market, stored
):
    govern(book, engine)
    deal = ally_deal(book)
    book.propose_deal(ALICE, NEXT_DAY, ACI)
    book.break_deal(ALICE, NEXT_DAY + timedelta(days=3), deal.id)

    rebuilt = replay(stored)

    assert rebuilt.deals == book.state.deals
    assert rebuilt.next_deal_id == book.state.next_deal_id
    day = date(2022, 2, 28)
    assert rebuilt.amendments_on(day) == book.state.amendments_on(day)


# Aliado de jogador


def player_ally(book: GovernmentBook, engine):
    """Bob lidera um segundo partido de jogador com bancada na casa."""
    found(book, BOB, "BBB", BLUE, "10000", NICHE)
    govern(book, engine)
    bloc = book.state.house_on(TERM_START).of_party(party_of(book, BOB).id)
    return bloc


def test_the_player_party_has_fifteen_days_to_answer_and_silence_is_a_refusal(
    book: GovernmentBook, engine, market, notices
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")

    book.propose_deal(ALICE, TERM_START, bloc.key)

    deal = deal_with(book, bloc.key)
    answer_by = TERM_START + timedelta(days=deals.ANSWER_DAYS)
    assert deal.answer_by == answer_by
    pending = [i.type for i in book.pending(BOB, TERM_START)]
    assert PendingType.DEAL_PROPOSAL in pending
    after = answer_by + timedelta(days=1)
    book.on_tick(USERS, after, False)
    assert deal.status is DealStatus.DECLINED
    assert PendingType.DEAL_PROPOSAL not in [i.type for i in book.pending(BOB, after)]


def test_the_player_leader_accepts_and_then_must_confirm_a_no_vote(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    propose(book)
    book.propose_deal(ALICE, TERM_START, bloc.key)

    book.answer_deal(BOB, TERM_START, True)
    deal = deal_with(book, bloc.key)

    assert deal.status is DealStatus.ACTIVE
    orientations, guided, _ = book.measure_orientations(
        book.state.measures[1], TERM_START
    )
    assert (orientations[bloc.key], guided[bloc.key]) == (True, True)
    with pytest.raises(ConflictError, match="rompe o acordo"):
        book.guide(BOB, TERM_START, 1, False)
    book.guide(BOB, TERM_START, 1, False, breaks_deal=True)
    assert deal.status is DealStatus.BROKEN
    assert deal.broken_by is DealBreaker.ALLY
    orientations, _, _ = book.measure_orientations(book.state.measures[1], TERM_START)
    assert orientations[bloc.key] is False


def test_the_player_ally_leaves_the_base_and_the_government_groups_blame_the_ally(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)
    book.answer_deal(BOB, TERM_START, True)
    ally = party_of(book, BOB)
    before = dict(ally.rejection)

    with pytest.raises(ConflictError, match="não está na base"):
        book.leave_base(ALICE, TERM_START)
    book.leave_base(BOB, TERM_START + timedelta(days=2))

    assert deal_with(book, bloc.key).broken_by is DealBreaker.ALLY
    assert any(ally.rejection[g] > before[g] for g in VoterGroup)


def test_only_the_leader_of_the_proposed_party_answers(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)

    with pytest.raises(NotFoundError):
        book.answer_deal(ALICE, TERM_START, True)


# Painel


def test_the_base_panel_shows_the_blocs_the_deals_and_the_amendments(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    ally_deal(book)
    book.propose_deal(ALICE, NEXT_DAY, UPR)

    panel = base_panel.build_base(book, USERS, ALICE, NEXT_DAY)

    assert panel.is_president
    assert panel.seats == book.base_seats(NEXT_DAY)
    assert panel.majority == house.MAJORITY
    assert {d.abbr for d in panel.deals} == {"MNV", "UPR"}
    in_base = {b.abbr for b in panel.blocs if b.in_base}
    assert in_base == {"MNV"}
    assert next(b for b in panel.blocs if b.abbr == "UPR").pending
    assert panel.amendments.ratio == deal_with(book, MNV).ratio


def test_the_preview_prices_the_proposal_and_tells_whether_the_computer_accepts(
    book: GovernmentBook, engine, market, projection
):
    govern(book, engine)

    liked = base_panel.build_preview(book, USERS, TERM_START, MNV)
    refused = base_panel.build_preview(book, USERS, TERM_START, ACI)

    assert liked.likely is True and liked.shared_flags == 2
    assert refused.likely is False and refused.shared_flags == 1
    assert liked.base_after == liked.base_before + liked.seats
    assert liked.end == deals.last_day(TERM_START, book.term_end())
    assert liked.debt_before is not None and liked.debt_after is not None
    assert liked.debt_after > liked.debt_before
    assert liked.ratio == deals.price("MNV", liked.seats)


def test_the_accepted_deal_reaches_the_journal_with_the_size_of_the_base(
    book: GovernmentBook, engine, market, headlines
):
    govern(book, engine)
    headlines.clear()

    ally_deal(book, UPR)

    [made] = [h for _, h in headlines if h.text.startswith("UPR entra na base")]
    assert made.text == "UPR entra na base do governo de Alice"
    assert made.dek is not None
    assert f"São {seats_of(book, UPR)} cadeiras" in made.dek
    assert f"a base vai a {book.base_seats(NEXT_DAY)}" in made.dek


def test_a_declined_deal_is_not_news(book: GovernmentBook, engine, market, headlines):
    govern(book, engine)
    headlines.clear()

    book.propose_deal(ALICE, TERM_START, ACI)
    book.on_tick(USERS, NEXT_DAY, False)

    assert not [h for _, h in headlines if "entra na base" in h.text]
