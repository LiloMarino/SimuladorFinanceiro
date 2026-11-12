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
    GovernmentEventType,
    GovernmentNoticeKind,
    NewsType,
    PendingType,
    VoterGroup,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import required
from backend.features.economy.layer import months_to_days
from backend.features.government import approval as approval_rules
from backend.features.government import base_panel, deals, house, sector_boost
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
    assert deal.end == book.term_end() == date(2025, 12, 31)
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


def test_a_deal_in_force_blocks_a_new_one_until_the_end_of_the_term(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    bloc = book.state.house_on(NEXT_DAY).bloc(MNV)
    assert bloc is not None
    assert deal.end is not None

    assert book.deal_blocker(bloc, NEXT_DAY) is not None
    assert book.deal_blocker(bloc, deal.end) is not None
    with pytest.raises(ConflictError, match="já está na base"):
        book.propose_deal(ALICE, NEXT_DAY + timedelta(days=200), MNV)


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


# Cobrança da base

# O 1º ano do mandato é carência: a primeira cobrança possível vem no fechamento de janeiro do 2º
FIRST_DEMAND_CLOSING = date(2023, 1, 31)
FEBRUARY_CLOSING = date(2023, 2, 28)
AFTER_DEMAND = FIRST_DEMAND_CLOSING + timedelta(days=1)


def aim_approval(monkeypatch: pytest.MonkeyPatch, target: int) -> None:
    """Todos os grupos passam a mirar o mesmo alvo: a aprovação anda um terço do caminho por mês."""
    monkeypatch.setattr(
        approval_rules,
        "group_target",
        lambda *_: approval_rules.GroupTarget(Decimal(target), []),
    )


def latest_deal(book: GovernmentBook, key: int) -> deals.Deal:
    return max(
        (d for d in book.state.deals.values() if d.bloc_key == key),
        key=lambda d: d.id,
    )


def demands_of(book: GovernmentBook, user, day: date):
    return [i for i in book.pending(user, day) if i.type is PendingType.DEAL_DEMAND]


def weak_deal(book: GovernmentBook, engine) -> deals.Deal:
    """O governo com o acordo do MNV chega ao 1º fechamento fraco depois da carência."""
    govern(book, engine, vice=True)
    deal = ally_deal(book)
    close_months(book, 12)
    assert deal.demand_ratio is None
    close_months(book, 1, FIRST_DEMAND_CLOSING)
    return deal


def test_the_base_charges_half_more_when_a_month_closes_below_thirty_five(
    book: GovernmentBook, engine, market, bleak
):
    deal = weak_deal(book, engine)

    assert deal.demand_ratio == deals.demanded(deal.ratio)
    assert deal.demand_by == FIRST_DEMAND_CLOSING + timedelta(days=deals.ANSWER_DAYS)
    [item] = demands_of(book, ALICE, AFTER_DEMAND)
    assert item.key == f"{PendingType.DEAL_DEMAND.value}:deal-{deal.id}"
    assert "MNV" in item.detail
    assert demands_of(book, BOB, AFTER_DEMAND) == []
    assert deal.in_force(AFTER_DEMAND)


def test_there_is_no_demand_inside_the_first_year_of_the_term(
    book: GovernmentBook, engine, market, bleak
):
    govern(book, engine)
    deal = ally_deal(book)

    close_months(book, 12)

    assert required(book.approval(date(2022, 12, 31))).value < approval_rules.RISK_LIMIT
    assert deal.demand_ratio is None
    assert book.state.demand_armed


def test_accepting_keeps_the_deal_until_the_end_of_the_term_at_the_new_price(
    book: GovernmentBook, engine, market, bleak, notices
):
    old = weak_deal(book, engine)
    end = old.end

    book.answer_demand(ALICE, AFTER_DEMAND, old.id, True)

    renewed = latest_deal(book, MNV)
    assert renewed.id != old.id
    assert old.status is DealStatus.CUT
    assert old.end == AFTER_DEMAND - timedelta(days=1)
    assert renewed.status is DealStatus.ACTIVE
    assert renewed.ratio == deals.demanded(old.ratio)
    assert (renewed.start, renewed.end) == (AFTER_DEMAND, end)
    assert renewed.demand_ratio is None
    assert demands_of(book, ALICE, AFTER_DEMAND) == []


def test_one_demand_per_fall_and_a_new_one_only_after_approval_passes_forty_five(
    book: GovernmentBook, engine, market, bleak, monkeypatch
):
    old = weak_deal(book, engine)
    base_ratio = old.ratio
    book.answer_demand(ALICE, AFTER_DEMAND, old.id, True)

    # Seguir fraco no mês seguinte não cobra de novo
    close_months(book, 1, FEBRUARY_CLOSING)
    assert latest_deal(book, MNV).demand_ratio is None
    assert not book.state.demand_armed

    # Subir sem passar de 45 não rearma; passar de 45 rearma
    aim_approval(monkeypatch, 100)
    close_months(book, 1, date(2023, 3, 31))
    assert not book.state.demand_armed
    close_months(book, 1, date(2023, 4, 30))
    assert required(book.approval(date(2023, 4, 30))).value > deals.RECOVERY_APPROVAL
    assert book.state.demand_armed

    # A nova queda cobra de novo, sobre o preço que já estava valendo
    aim_approval(monkeypatch, 0)
    close_months(book, 3, date(2023, 5, 31))
    current = latest_deal(book, MNV)
    assert current.demand_ratio == deals.demanded(deals.demanded(base_ratio))
    assert not book.state.demand_armed


def test_refusing_removes_the_bloc_without_the_break_rejection(
    book: GovernmentBook, engine, market, bleak, notices, headlines
):
    deal = weak_deal(book, engine)
    party = party_of(book, ALICE)
    before = dict(party.rejection)
    notices.clear()
    headlines.clear()

    book.answer_demand(ALICE, AFTER_DEMAND, deal.id, False)

    assert deal.status is DealStatus.BROKEN
    assert deal.broken_by is DealBreaker.APPROVAL
    assert book.state.deal_of(MNV, AFTER_DEMAND + timedelta(days=1)) is None
    assert party.rejection == before
    assert [n for n in notices if n.get("kind") == GovernmentNoticeKind.DEAL_LEFT.value]
    [left] = [h for _, h in headlines]
    assert left.news_type is NewsType.PARTY_RUPTURE
    assert "MNV" in left.text and "base do governo" in left.text.lower()
    assert demands_of(book, ALICE, AFTER_DEMAND) == []


def test_an_expired_demand_removes_the_bloc_like_a_refusal(
    book: GovernmentBook, engine, market, bleak
):
    deal = weak_deal(book, engine)
    party = party_of(book, ALICE)
    before = dict(party.rejection)
    assert deal.demand_by is not None

    book.on_tick(USERS, deal.demand_by, False)
    assert deal.in_force(deal.demand_by)
    book.on_tick(USERS, deal.demand_by + timedelta(days=1), False)

    assert deal.status is DealStatus.BROKEN
    assert deal.broken_by is DealBreaker.APPROVAL
    assert party.rejection == before


def test_only_the_president_answers_and_only_an_open_demand(
    book: GovernmentBook, engine, market, bleak
):
    govern(book, engine, vice=True)
    deal = ally_deal(book)

    with pytest.raises(ConflictError, match="não está cobrando"):
        book.answer_demand(ALICE, NEXT_DAY, deal.id, True)
    close_months(book, 12)
    close_months(book, 1, FIRST_DEMAND_CLOSING)
    with pytest.raises(ForbiddenError):
        book.answer_demand(BOB, AFTER_DEMAND, deal.id, True)
    late = required(deal.demand_by) + timedelta(days=1)
    with pytest.raises(ConflictError, match="prazo"):
        book.answer_demand(ALICE, late, deal.id, True)


def test_a_bloc_that_left_comes_back_with_the_price_already_raised(
    book: GovernmentBook, engine, market, bleak
):
    deal = weak_deal(book, engine)
    book.answer_demand(ALICE, AFTER_DEMAND, deal.id, False)
    bloc = book.state.house_on(AFTER_DEMAND).bloc(MNV)
    assert bloc is not None
    # Sair por aprovação não é recusa de proposta: não há espera de 30 dias
    assert book.deal_blocker(bloc, AFTER_DEMAND) is None
    day = AFTER_DEMAND + timedelta(days=1)

    book.propose_deal(ALICE, day, MNV)
    book.on_tick(USERS, day + timedelta(days=1), False)

    recalled = latest_deal(book, MNV)
    assert recalled.status is DealStatus.ACTIVE
    assert recalled.ratio == deals.demanded(deals.price("MNV", seats_of(book, MNV)))
    assert recalled.end == book.term_end()


def test_the_base_panel_shows_the_demand_with_the_price_and_the_days_left(
    book: GovernmentBook, engine, market, bleak
):
    deal = weak_deal(book, engine)

    panel = base_panel.build_base(book, USERS, ALICE, AFTER_DEMAND)

    [shown] = [d for d in panel.deals if d.abbr == "MNV"]
    assert shown.demand_monthly == book.monthly(
        required(deal.demand_ratio), AFTER_DEMAND
    )
    assert shown.demand_by == deal.demand_by
    assert shown.demand_days_left == deals.ANSWER_DAYS - 1


def test_the_preview_already_shows_the_raised_price_while_approval_is_below_thirty_five(
    book: GovernmentBook, engine, market, bleak, projection
):
    govern(book, engine)
    assert required(book.approval(TERM_START)).value >= approval_rules.RISK_LIMIT
    normal = base_panel.build_preview(book, USERS, TERM_START, MNV)

    close_months(book, 15)
    later = date(2023, 4, 3)
    assert required(book.approval(later)).value < approval_rules.RISK_LIMIT
    weak = base_panel.build_preview(book, USERS, later, MNV)

    assert normal.ratio == deals.price("MNV", normal.seats)
    assert weak.ratio == deals.demanded(deals.price("MNV", weak.seats))


def test_the_computer_government_never_charges(
    book: GovernmentBook, engine, market, bleak, stored
):
    govern(book, engine)
    book._emit(
        GovernmentEventType.TERM_STARTED,
        TERM_START,
        party_id=next(iter(book.state.computer_parties())).id,
        president_id=None,
        vice_id=None,
        consecutive=1,
    )

    close_months(book, 14)

    assert book.state.approvals
    assert book.state.demand_armed
    measured = [
        e for e in stored if e.event_type is GovernmentEventType.APPROVAL_MEASURED
    ]
    assert measured
    assert all(e.payload.get("demand") is False for e in measured)


# Retomada


def test_a_resumed_game_keeps_the_demand_and_the_renewed_deal(
    book: GovernmentBook, engine, market, bleak, stored
):
    old = weak_deal(book, engine)
    rebuilt = replay(stored)
    assert rebuilt.deals == book.state.deals
    assert rebuilt.demand_armed is False
    assert book.state.demand_armed is False

    book.answer_demand(ALICE, AFTER_DEMAND, old.id, True)
    rebuilt = replay(stored)

    assert rebuilt.deals == book.state.deals
    assert latest_deal_of(rebuilt, MNV).ratio == deals.demanded(old.ratio)


def latest_deal_of(state: government_state.GovernmentState, key: int) -> deals.Deal:
    return max(
        (d for d in state.deals.values() if d.bloc_key == key), key=lambda d: d.id
    )


def test_a_deal_signed_before_keeps_its_own_end_when_the_game_is_resumed(
    book: GovernmentBook, engine, market, stored
):
    govern(book, engine)
    book.propose_deal(ALICE, TERM_START, MNV)
    signed = deal_with(book, MNV)
    book._emit(
        GovernmentEventType.DEAL_ANSWERED,
        NEXT_DAY,
        deal_id=signed.id,
        accepted=True,
        by=None,
        end=date(2022, 7, 2).isoformat(),
    )

    rebuilt = replay(stored)

    old = rebuilt.deals[signed.id]
    assert old.end == date(2022, 7, 2)
    assert old.in_force(date(2022, 7, 2))
    assert not old.in_force(date(2022, 7, 3))


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
    found(book, BOB, "BBB", BLUE, "8000", NICHE)
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
    assert liked.end == book.term_end()
    assert liked.debt_before is not None and liked.debt_after is not None
    assert liked.debt_after > liked.debt_before
    assert liked.ratio == deals.price("MNV", liked.seats)


def test_the_accepted_deal_reaches_the_journal_with_the_size_of_the_base(
    book: GovernmentBook, engine, market, headlines
):
    govern(book, engine)
    headlines.clear()

    ally_deal(book, UPR)

    [made] = [h for _, h in headlines if h.news_type is NewsType.PARTY_LIFE]
    assert "UPR" in made.text and "Alice" in made.text
    assert made.dek is not None
    assert f"São {seats_of(book, UPR)} cadeiras" in made.dek
    assert f"a base vai a {book.base_seats(NEXT_DAY)}" in made.dek


def test_a_declined_deal_is_not_news(book: GovernmentBook, engine, market, headlines):
    govern(book, engine)
    headlines.clear()

    book.propose_deal(ALICE, TERM_START, ACI)
    book.on_tick(USERS, NEXT_DAY, False)

    assert not [h for _, h in headlines if h.news_type is NewsType.PARTY_LIFE]


# Emenda com endereço

FULL_RAMP = timedelta(days=months_to_days(sector_boost.RAMP_MONTHS))


def boost_of(book: GovernmentBook, day: date) -> float:
    return book.sector_boost_on("Energia", "Geração", day)


def test_the_player_leader_addresses_the_amendment_when_accepting(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)

    book.answer_deal(BOB, TERM_START, True, "Energia", "Geração")

    deal = deal_with(book, bloc.key)
    assert (deal.sector, deal.segment) == ("Energia", "Geração")
    assert boost_of(book, TERM_START) == 0
    assert boost_of(book, TERM_START + FULL_RAMP) == pytest.approx(
        sector_boost.amendment_peak(deal.ratio)
    )
    assert book.sector_boost_on("Bancos", "Bancos", TERM_START + FULL_RAMP) == 0


def test_accepting_without_an_address_leaves_the_amendment_with_no_sector(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)

    book.answer_deal(BOB, TERM_START, True)

    deal = deal_with(book, bloc.key)
    assert (deal.sector, deal.segment) == (None, None)
    assert boost_of(book, TERM_START + FULL_RAMP) == 0


def test_a_refusal_with_an_address_is_unprocessable_and_the_proposal_stays_open(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)

    with pytest.raises(UnprocessableEntityError):
        book.answer_deal(BOB, TERM_START, False, "Energia", None)

    assert deal_with(book, bloc.key).status is DealStatus.PENDING


def test_an_address_that_does_not_exist_is_refused_and_the_proposal_stays_open(
    book: GovernmentBook, engine, market
):
    bloc = player_ally(book, engine)
    if bloc is None or bloc.seats == 0:
        pytest.skip("o partido de teste não elegeu cadeiras")
    book.propose_deal(ALICE, TERM_START, bloc.key)

    with pytest.raises(NotFoundError):
        book.answer_deal(BOB, TERM_START, True, "Pesca", None)
    with pytest.raises(NotFoundError):
        book.answer_deal(BOB, TERM_START, True, "Energia", "Varejo")

    assert deal_with(book, bloc.key).status is DealStatus.PENDING


def test_the_computer_party_picks_the_sector_from_its_acronym(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    # M + N + V somam 241; entre Bancos e Energia, 241 % 2 = 1 é Energia
    deal = ally_deal(book)

    assert (deal.sector, deal.segment) == ("Energia", None)
    assert deal.sector == book.computer_sector("MNV")
    assert boost_of(book, NEXT_DAY + FULL_RAMP) == pytest.approx(
        sector_boost.amendment_peak(deal.ratio)
    )


def test_the_panel_and_the_preview_show_the_sector_the_computer_will_pick(
    book: GovernmentBook, engine, market, projection
):
    govern(book, engine)

    preview = base_panel.build_preview(book, USERS, TERM_START, MNV)
    book.propose_deal(ALICE, TERM_START, MNV)
    panel = base_panel.build_base(book, USERS, ALICE, TERM_START)
    [pending] = panel.deals
    bloc = next(b for b in panel.blocs if b.key == MNV)

    assert preview.sector == pending.sector == bloc.sector == "Energia"
    assert preview.sector_boost == pending.sector_boost == bloc.sector_boost
    assert preview.sector_boost == sector_boost.as_fraction(
        sector_boost.amendment_peak(preview.ratio)
    )
    # 1 ponto de apoio por mês custaria 64 ao quadrado, R$ 4.096, de verba de campanha
    assert preview.campaign_equivalent == pending.campaign_equivalent == 4096


def test_the_amendments_of_the_same_sector_add_up(book: GovernmentBook, engine, market):
    govern(book, engine)
    book.propose_deal(ALICE, TERM_START, MNV)
    book.propose_deal(ALICE, TERM_START, UPR)
    book.on_tick(USERS, NEXT_DAY, False)

    first, second = deal_with(book, MNV), deal_with(book, UPR)

    assert (first.sector, second.sector) == ("Energia", "Energia")
    assert boost_of(book, NEXT_DAY + FULL_RAMP) == pytest.approx(
        sector_boost.combined(
            0.0,
            0.0,
            sector_boost.amendment_peak(first.ratio)
            + sector_boost.amendment_peak(second.ratio),
        )
    )


def test_breaking_the_deal_ends_the_boost_and_keeps_the_history(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    breaking = NEXT_DAY + timedelta(days=100)
    before = boost_of(book, breaking)
    assert before > 0

    book.break_deal(ALICE, breaking, deal.id)

    assert boost_of(book, breaking) == pytest.approx(before)
    assert boost_of(book, breaking + timedelta(days=1)) == 0
    assert boost_of(book, breaking + FULL_RAMP) == 0


def test_a_deal_that_ends_with_the_term_ends_the_boost(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    deal = ally_deal(book)
    end = required(deal.end)

    assert boost_of(book, end) > 0
    assert boost_of(book, end + timedelta(days=1)) == 0


def test_the_renegotiated_deal_keeps_the_sector_and_follows_the_new_price(
    book: GovernmentBook, engine, market, bleak
):
    old = weak_deal(book, engine)
    chosen = old.sector
    assert chosen == "Energia"
    started = old.ramp_start

    book.answer_demand(ALICE, AFTER_DEMAND, old.id, True)

    renewed = latest_deal(book, MNV)
    assert (renewed.sector, renewed.segment) == (chosen, None)
    # A rampa segue de onde estava, e a alta cheia passa a ser a do preço novo
    assert renewed.ramp_start == started
    full = AFTER_DEMAND + FULL_RAMP
    assert boost_of(book, full) == pytest.approx(
        sector_boost.amendment_peak(renewed.ratio)
    )
    assert renewed.ratio == deals.demanded(old.ratio)


def test_a_resumed_game_keeps_the_sector_of_the_amendment(
    book: GovernmentBook, engine, market, stored
):
    govern(book, engine)
    deal = ally_deal(book)

    rebuilt = replay(stored)

    again = latest_deal_of(rebuilt, MNV)
    assert (again.sector, again.segment, again.ramp_start) == (
        deal.sector,
        deal.segment,
        deal.ramp_start,
    )


def test_the_deal_headline_cites_the_sector_of_the_amendment(
    book: GovernmentBook, engine, market, headlines
):
    govern(book, engine)
    headlines.clear()

    ally_deal(book)

    [made] = [h for _, h in headlines if h.news_type is NewsType.PARTY_LIFE]
    assert made.dek is not None
    assert "Energia" in made.dek
