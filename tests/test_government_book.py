"""Livro do governo: partidos, contribuição mensal, apuração dos dois turnos, doação e retomada."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CashflowEventType,
    ComputerDifficulty,
    ElectionPhase,
    GovernmentNoticeKind,
    MeasureKind,
    MeasureStatus,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.government import approval as approval_rules
from backend.features.government import congress, election
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_panel
from backend.features.government.state import Party, replay, vote_points
from backend.features.tax_policy import LossPool
from tests.fakes import FakeSimulationEngine, client, simulation_settings

ALICE = UserDTO(id=1, client_id=client("alice"), nickname="Alice")
BOB = UserDTO(id=2, client_id=client("bob"), nickname="Bob")
CARLA = UserDTO(id=3, client_id=client("carla"), nickname="Carla")
BOT = UserDTO(id=4, client_id=client("bot"), nickname="Robo", is_bot=True)
USERS = [ALICE, BOB, CARLA, BOT]

CAMPAIGN_OPEN = date(2020, 10, 7)
FIRST_ROUND = date(2021, 10, 7)
RUNOFF = date(2021, 10, 28)
TERM_START = date(2022, 1, 3)
SEED = 7
RED = "#dc2626"
BLUE = "#2563eb"
GREEN = "#15803d"


class PoliticalEngine(FakeSimulationEngine):
    """Motor em memória com o débito de campanha que o livro usa."""

    def pay_campaign(
        self, client_id: uuid.UUID, amount: Decimal, event_type: CashflowEventType
    ) -> None:
        self.add_cash(client_id, -amount)


@pytest.fixture
def stored(monkeypatch: pytest.MonkeyPatch) -> list[GovernmentEventDTO]:
    """O repositório em memória: o que o livro grava é o que a retomada devolve."""
    events: list[GovernmentEventDTO] = []
    monkeypatch.setattr(repository.government, "insert", events.append)
    monkeypatch.setattr(
        repository.government, "get_events", lambda _simulation_id: list(events)
    )
    return events


@pytest.fixture
def notices(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    sent: list[dict[str, object]] = []
    monkeypatch.setattr(
        "backend.features.government.government_book.notify",
        lambda name, payload, **_: sent.append(payload),
    )
    return sent


def settings() -> SimulationDTO:
    rules = simulation_settings().model_dump()
    rules.update(
        start_date=date(2020, 1, 1),
        end_date=date(2025, 12, 31),
        government_enabled=True,
        first_election=FIRST_ROUND,
        computer_difficulty=ComputerDifficulty.EASY,
    )
    return SimulationDTO(id=1, **rules)


@pytest.fixture
def engine() -> PoliticalEngine:
    return PoliticalEngine(
        cash={u.client_id: Decimal(100000) for u in USERS}, current_date=CAMPAIGN_OPEN
    )


@pytest.fixture
def office() -> list[int]:
    """Quem tomou posse: o livro avisa a partida a cada presidente jogador."""
    return []


@pytest.fixture
def book(engine, stored, notices, captured_events, office) -> GovernmentBook:
    return GovernmentBook(
        settings(), engine, lambda user, _day: office.append(user.id), SEED
    )


def found(book: GovernmentBook, user: UserDTO, abbr: str, color: str, amount="10000"):
    book.found_party(
        user,
        CAMPAIGN_OPEN,
        name=f"Partido {abbr}",
        abbr=abbr,
        color=color,
        promise=3,
        contribution=Decimal(amount),
    )


def party_of(book: GovernmentBook, user: UserDTO) -> Party:
    """O partido de quem já se filiou; o teste falha aqui se a filiação não existe."""
    party = book.state.party_of(user.id)
    assert party is not None
    return party


def test_computer_fills_the_race_up_to_three_parties(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    assert len(book.state.computer_parties()) == 2

    found(book, BOB, "BBB", BLUE)
    assert len(book.state.computer_parties()) == 1

    found(book, CARLA, "CCC", GREEN)
    assert book.state.computer_parties() == []


def test_computer_parties_come_back_when_a_player_party_dissolves(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    found(book, CARLA, "CCC", GREEN)

    book.leave_party(CARLA, CAMPAIGN_OPEN)

    assert len(book.state.player_parties()) == 2
    assert len(book.state.computer_parties()) == 1


def test_party_opens_only_during_the_campaign_year(book: GovernmentBook):
    with pytest.raises(ConflictError, match="campanha"):
        book.found_party(
            ALICE,
            date(2020, 6, 1),
            name="Cedo",
            abbr="CED",
            color=RED,
            promise=2,
            contribution=Decimal(0),
        )


def test_party_abbr_takes_two_to_eight_letters(book: GovernmentBook):
    found(book, ALICE, "ABCDEFGH", RED)

    assert party_of(book, ALICE).abbr == "ABCDEFGH"
    with pytest.raises(UnprocessableEntityError, match="2 a 8 letras"):
        found(book, BOB, "ABCDEFGHI", BLUE)
    with pytest.raises(UnprocessableEntityError, match="2 a 8 letras"):
        found(book, BOB, "A", BLUE)


def test_bots_stay_out_of_parties(book: GovernmentBook):
    with pytest.raises(ForbiddenError):
        found(book, BOT, "BOT", RED)


def test_party_identity_is_unique(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    with pytest.raises(ConflictError, match="sigla"):
        found(book, BOB, "AAA", BLUE)
    with pytest.raises(ConflictError, match="cor"):
        found(book, BOB, "BBB", RED)
    with pytest.raises(ConflictError, match="já está"):
        found(book, ALICE, "ZZZ", GREEN)


def test_founder_role_passes_to_the_oldest_member_who_stays(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    party_id = party_of(book, ALICE).id
    book.join_party(BOB, CAMPAIGN_OPEN, party_id, Decimal(0))
    book.join_party(CARLA, CAMPAIGN_OPEN, party_id, Decimal(0))

    book.leave_party(ALICE, CAMPAIGN_OPEN)

    assert book.state.parties[party_id].founder_id == BOB.id


def test_only_the_founder_expels(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    party_id = party_of(book, ALICE).id
    book.join_party(BOB, CAMPAIGN_OPEN, party_id, Decimal(0))

    with pytest.raises(ForbiddenError):
        book.expel(BOB, CAMPAIGN_OPEN, "Alice", USERS)
    with pytest.raises(NotFoundError):
        book.expel(ALICE, CAMPAIGN_OPEN, "Carla", USERS)

    book.expel(ALICE, CAMPAIGN_OPEN, "Bob", USERS)
    assert book.state.party_of(BOB.id) is None


def test_monthly_contribution_buys_votes_and_is_charged_once_a_month(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED, "10000")
    party = party_of(book, ALICE)

    book.on_tick(USERS, date(2020, 11, 3), True)
    book.on_tick(USERS, date(2020, 11, 4), True)

    assert engine.get_cash(ALICE.client_id) == Decimal(90000)
    assert party.points == vote_points(Decimal(10000))
    computers = book.state.computer_parties()
    # Dificuldade Fácil: o computador gasta metade da verba do partido de jogadores
    assert all(c.spent == Decimal(5000) for c in computers)


def test_member_without_cash_skips_the_month(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED, "10000")
    engine.cash[ALICE.client_id] = Decimal(500)

    book.on_tick(USERS, date(2020, 11, 3), True)

    assert engine.get_cash(ALICE.client_id) == Decimal(500)
    assert party_of(book, ALICE).points == 0


def test_no_collection_before_the_campaign_opens(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    book.on_tick(USERS, date(2020, 9, 1), True)

    assert book.state.last_collection is None


def test_page_renews_on_the_day_the_campaign_opens(book: GovernmentBook, notices):
    book.on_tick(USERS, date(2020, 10, 5), False)
    assert notices == []

    book.on_tick(USERS, date(2020, 10, 7), False)
    assert [notice["kind"] for notice in notices] == ["UPDATED"]

    book.on_tick(USERS, date(2020, 10, 8), False)
    assert len(notices) == 1


def test_page_renews_on_the_day_the_tickets_close(book: GovernmentBook, notices):
    book.on_tick(USERS, date(2021, 9, 29), False)
    book.on_tick(USERS, date(2021, 10, 1), False)

    assert [notice["kind"] for notice in notices] == ["UPDATED"]


def run_campaign(book: GovernmentBook) -> None:
    for month in range(11, 13):
        book.on_tick(USERS, date(2020, month, 3), True)
    for month in range(1, 10):
        book.on_tick(USERS, date(2021, month, 3), True)


def test_two_rounds_end_with_the_term_starting_in_january(
    book: GovernmentBook, notices
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000")
    run_campaign(book)

    assert book.on_tick(USERS, FIRST_ROUND, False) is True
    alice_party = party_of(book, ALICE)
    # Nenhum passou de 50% dos válidos: vão ao 2º turno a Alice e o computador mais votado
    assert alice_party.id in (book.state.runoff or [])
    assert party_of(book, BOB).id not in (book.state.runoff or [])
    assert book.state.pending_term is None

    assert book.on_tick(USERS, RUNOFF, False) is True
    assert book.state.pending_term is not None
    assert book.state.cycle == 1

    assert book.on_tick(USERS, TERM_START, False) is False
    assert book.state.term is not None
    assert book.state.term.consecutive == 1
    posse = notices[-1]
    assert posse["kind"] == GovernmentNoticeKind.TERM_STARTED.value
    # O aviso da posse diz quem governa: sigla do partido eleito e nome do presidente
    assert book.state.term.party_id is not None
    assert posse["winner_abbr"] == book.state.parties[book.state.term.party_id].abbr
    assert posse["winner_name"]


def test_winning_party_keeps_members_but_restarts_the_support(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "10000")
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)

    party = party_of(book, ALICE)

    assert party is not None
    assert party.points == 0
    assert party.spent == 0
    assert book.state.polls == []


def test_donation_goes_only_to_a_finalist_and_only_from_an_eliminated_party(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000")
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    finalist = party_of(book, ALICE).id
    eliminated_cash = engine.get_cash(BOB.client_id)

    with pytest.raises(ConflictError, match="ficou de fora"):
        book.donate(ALICE, date(2021, 10, 10), finalist, Decimal(1000))
    with pytest.raises(ConflictError, match="finalistas"):
        book.donate(BOB, date(2021, 10, 10), party_of(book, BOB).id, Decimal(1000))
    with pytest.raises(ConflictError, match="prazo"):
        book.donate(BOB, date(2021, 10, 28), finalist, Decimal(1000))

    before = book.state.parties[finalist].points
    book.donate(BOB, date(2021, 10, 10), finalist, Decimal(1000))

    assert engine.get_cash(BOB.client_id) == eliminated_cash - 1000
    assert book.state.parties[finalist].points == before + vote_points(Decimal(1000))


def test_between_rounds_only_donations_are_open(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)

    with pytest.raises(ConflictError, match="só dá para doar"):
        book.leave_party(BOB, date(2021, 10, 10))
    with pytest.raises(ConflictError, match="só dá para doar"):
        book.set_contribution(ALICE, date(2021, 10, 10), Decimal(5))


def test_donation_is_closed_outside_the_gap_between_rounds(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    with pytest.raises(ConflictError, match="entre o 1º e o 2º turno"):
        book.donate(ALICE, CAMPAIGN_OPEN, 1, Decimal(10))


def test_vice_counts_only_after_accepting(book: GovernmentBook, notices):
    found(book, ALICE, "AAA", RED)
    party = party_of(book, ALICE)
    book.join_party(BOB, CAMPAIGN_OPEN, party.id, Decimal(0))

    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)
    assert notices[-1]["kind"] == GovernmentNoticeKind.VICE_INVITED.value

    assert election.effective_ticket(book.state, party) == (ALICE.id, None)

    book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    assert election.effective_ticket(book.state, party) == (ALICE.id, BOB.id)


def test_declined_vice_leaves_the_slot_empty(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    party = party_of(book, ALICE)
    book.join_party(BOB, CAMPAIGN_OPEN, party.id, Decimal(0))
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)

    book.answer_vice(BOB, CAMPAIGN_OPEN, False)

    assert party.vice_id is None
    with pytest.raises(NotFoundError):
        book.answer_vice(BOB, CAMPAIGN_OPEN, True)


def test_ticket_registration_closes_the_month_before_the_vote(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    with pytest.raises(ConflictError, match="inscrição"):
        book.set_ticket(ALICE, date(2021, 10, 1), "Alice", None, USERS)


def test_only_members_run_on_the_ticket(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)

    with pytest.raises(NotFoundError, match="filiado"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Bob", None, USERS)
    with pytest.raises(ConflictError, match="diferentes"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Alice", USERS)


def test_replay_rebuilds_the_same_state(book: GovernmentBook, stored):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000")
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.donate(BOB, date(2021, 10, 10), party_of(book, ALICE).id, Decimal(500))
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)

    rebuilt = replay(stored)

    assert rebuilt.cycle == book.state.cycle
    assert rebuilt.term == book.state.term
    assert rebuilt.results == book.state.results
    assert {p.id: (p.members, p.points) for p in rebuilt.parties.values()} == {
        p.id: (p.members, p.points) for p in book.state.parties.values()
    }


def test_resumed_book_starts_from_the_stored_events(
    book: GovernmentBook, engine, stored, notices
):
    found(book, ALICE, "AAA", RED, "10000")
    book.on_tick(USERS, date(2020, 11, 3), True)

    resumed = GovernmentBook(settings(), engine, lambda *_: None, SEED)

    assert party_of(resumed, ALICE).points == party_of(book, ALICE).points
    assert resumed.state.last_collection == date(2020, 11, 1)


def test_panel_follows_the_phase_of_the_race(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000")
    networths = {u.id: Decimal(1000 * u.id) for u in USERS}

    def panel(user: UserDTO, today: date):
        return build_panel(book, settings(), USERS, user, today, networths)

    assert panel(CARLA, date(2020, 5, 1)).phase is ElectionPhase.BEFORE_CAMPAIGN
    assert panel(CARLA, CAMPAIGN_OPEN).phase is ElectionPhase.CAMPAIGN
    assert panel(CARLA, CAMPAIGN_OPEN).can_found_or_join is True
    assert panel(ALICE, CAMPAIGN_OPEN).can_found_or_join is False
    assert panel(ALICE, CAMPAIGN_OPEN).can_edit_ticket is True
    assert panel(BOT, CAMPAIGN_OPEN).can_found_or_join is False

    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    between = panel(BOB, date(2021, 10, 10))
    assert between.phase is ElectionPhase.BETWEEN_ROUNDS
    assert between.can_donate is True
    assert panel(ALICE, date(2021, 10, 10)).can_donate is False
    assert between.last_result is not None
    assert between.last_result.round == 1

    book.on_tick(USERS, RUNOFF, False)
    assert panel(BOB, RUNOFF).phase is ElectionPhase.AWAITING_TERM

    book.on_tick(USERS, TERM_START, False)
    assert panel(BOB, TERM_START).term is not None


def test_party_ranking_adds_up_the_networth_of_the_members(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    party_id = party_of(book, ALICE).id
    book.join_party(BOB, CAMPAIGN_OPEN, party_id, Decimal(0))
    networths = {
        ALICE.id: Decimal(3000),
        BOB.id: Decimal(2000),
        CARLA.id: Decimal(9000),
    }

    panel = build_panel(book, settings(), USERS, ALICE, CAMPAIGN_OPEN, networths)

    assert [(s.abbr, s.total_networth) for s in panel.party_standings] == [
        ("AAA", Decimal(5000))
    ]
    assert panel.player_standings[0].nickname == "Carla"
    assert panel.player_standings[0].party_id is None


# Governar: medidas, Congresso, aprovação e impeachment

GOOD_MARKET = approval_rules.Market(
    inflation=Decimal("0.03"), stocks=Decimal("0.10"), target=Decimal("0.04")
)
# Inflação 8 pontos acima da meta e bolsa em queda: 50 - 20 - 6 = 24%, abaixo do piso
BAD_MARKET = approval_rules.Market(
    inflation=Decimal("0.12"), stocks=Decimal("-0.40"), target=Decimal("0.04")
)
FIRST_VOTE = date(2022, 1, 31)
SECTORS = {
    "TAEE11": StockSegmentDTO(sector="Energia", segment="Transmissão"),
    "EGIE3": StockSegmentDTO(sector="Energia", segment="Geração"),
    "ITUB4": StockSegmentDTO(sector="Bancos", segment="Bancos"),
}


@pytest.fixture
def market(monkeypatch: pytest.MonkeyPatch):
    """O mercado que a aprovação lê; cada teste escolhe o dele."""

    def use(value: approval_rules.Market) -> None:
        monkeypatch.setattr(approval_rules, "market_on", lambda _day: value)

    use(GOOD_MARKET)
    return use


def congress_says(monkeypatch: pytest.MonkeyPatch, approved: bool) -> None:
    monkeypatch.setattr(congress, "passes", lambda *_: approved)


def govern(book: GovernmentBook, engine, *, vice: bool = False) -> None:
    """Alice vence a eleição e toma posse; com `vice`, Bob é o vice dela."""
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    if vice:
        book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, ALICE).id, Decimal(0))
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)
        book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)
    assert book.state.term is not None
    assert book.state.term.president_id == ALICE.id


def propose(book: GovernmentBook, rate="0.20") -> None:
    book.propose(
        ALICE, TERM_START, MeasureKind.STOCK_PROFIT_RATE, Decimal(rate), None, None
    )


def test_term_start_hands_the_office_to_the_player_president(
    book: GovernmentBook, engine, office
):
    govern(book, engine)

    assert office == [ALICE.id]
    assert book.state.term is not None
    assert book.state.term.promise == 3


def test_only_the_president_proposes_and_the_queue_is_public(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    with pytest.raises(ForbiddenError):
        book.propose(
            BOB, TERM_START, MeasureKind.STOCK_PROFIT_RATE, Decimal("0.2"), None, None
        )
    propose(book)

    [queued] = book.state.measures.values()
    assert (queued.status, queued.before, queued.value) == (
        MeasureStatus.QUEUED,
        Decimal("0.15"),
        Decimal("0.20"),
    )
    with pytest.raises(ConflictError):
        propose(book, "0.25")
    with pytest.raises(ConflictError):
        book.propose(
            ALICE, TERM_START, MeasureKind.DAY_TRADE_RATE, Decimal("0.20"), None, None
        )


def test_sector_measure_needs_a_known_sector_and_segment(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    with pytest.raises(NotFoundError):
        book.propose(
            ALICE, TERM_START, MeasureKind.SECTOR_EXEMPT, None, "Mineração", None
        )
    with pytest.raises(NotFoundError):
        book.propose(
            ALICE, TERM_START, MeasureKind.SECTOR_EXEMPT, None, "Energia", "Bancos"
        )
    book.propose(ALICE, TERM_START, MeasureKind.SECTOR_EXEMPT, None, "Energia", None)
    assert book.tickers(book.state.measures[1]) == ["EGIE3", "TAEE11"]


def test_approved_measure_binds_only_ninety_days_after_the_vote(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, True)

    book.on_tick(USERS, FIRST_VOTE, False)

    measure = book.state.measures[1]
    assert measure.status is MeasureStatus.APPROVED
    assert measure.chance == 56
    assert measure.effective == date(2022, 5, 1)
    before, after = date(2022, 4, 29), date(2022, 5, 2)
    assert book.policy(before).rates[LossPool.COMMON] == Decimal("0.15")
    assert book.policy(after).rates[LossPool.COMMON] == Decimal("0.20")
    assert engine.tax_policy_on(after).rates[LossPool.COMMON] == Decimal("0.20")


def test_congress_votes_only_on_the_last_business_day_of_the_month(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, True)

    book.on_tick(USERS, date(2022, 1, 28), False)
    assert book.state.measures[1].status is MeasureStatus.QUEUED

    book.on_tick(USERS, FIRST_VOTE, False)
    assert book.state.measures[1].status is MeasureStatus.APPROVED


def test_rejected_measure_comes_back_to_the_queue(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, False)
    book.on_tick(USERS, FIRST_VOTE, False)
    assert book.state.measures[1].status is MeasureStatus.REJECTED

    book.repropose(ALICE, date(2022, 2, 1), 1)

    assert book.state.measures[2].status is MeasureStatus.QUEUED
    with pytest.raises(ConflictError):
        book.repropose(ALICE, date(2022, 2, 1), 2)


def test_withdrawn_measure_is_not_voted(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, True)

    book.withdraw(ALICE, TERM_START, 1)
    book.on_tick(USERS, FIRST_VOTE, False)

    assert book.state.measures[1].status is MeasureStatus.WITHDRAWN
    with pytest.raises(ConflictError):
        book.withdraw(ALICE, FIRST_VOTE, 1)


def test_approval_is_measured_every_month_and_kept_for_the_chart(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    book.on_tick(USERS, FIRST_VOTE, False)

    assert [(p.day, p.value) for p in book.state.approvals] == [(FIRST_VOTE, 56)]
    assert book.state.low_streak == 0
    # Fechado o mês, a mesma data não mede de novo
    book.on_tick(USERS, FIRST_VOTE, False)
    assert len(book.state.approvals) == 1


def test_president_wallet_is_frozen_and_the_others_keep_trading(
    book: GovernmentBook, engine
):
    govern(book, engine)

    with pytest.raises(ConflictError, match="carteira volta a operar"):
        book.ensure_can_trade(ALICE.client_id)
    book.ensure_can_trade(BOB.client_id)
    assert book.term_end() == date(2025, 12, 31)


def test_three_months_below_the_floor_remove_the_president_and_the_vice_takes_over(
    book: GovernmentBook, engine, market, office, notices, monkeypatch
):
    govern(book, engine, vice=True)
    propose(book)
    congress_says(monkeypatch, True)
    book.on_tick(USERS, FIRST_VOTE, False)
    market(BAD_MARKET)

    assert book.on_tick(USERS, date(2022, 2, 28), False) is False
    assert book.on_tick(USERS, date(2022, 3, 31), False) is False
    propose(book, "0.25")
    assert GovernmentNoticeKind.IMPEACHMENT_WARNING.value in [
        n["kind"] for n in notices
    ]
    assert book.on_tick(USERS, date(2022, 4, 29), False) is True

    term = book.state.term
    assert term is not None
    assert (term.president_id, term.succession) == (BOB.id, True)
    assert office[-1] == BOB.id
    # A medida aprovada segue os 90 dias; a fila não votada de quem saiu some
    assert book.state.measures[1].status is MeasureStatus.APPROVED
    assert book.state.measures[2].status is MeasureStatus.DROPPED
    book.ensure_can_trade(ALICE.client_id)
    with pytest.raises(ConflictError):
        book.ensure_can_trade(BOB.client_id)
    assert book.state.impeachments[0].successor_id == BOB.id


def test_impeachment_without_a_vice_leaves_a_neutral_computer_government(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    market(BAD_MARKET)

    for day in (date(2022, 1, 31), date(2022, 2, 28), date(2022, 3, 31)):
        book.on_tick(USERS, day, False)

    term = book.state.term
    assert term is not None
    assert (term.president_id, term.party_id) == (None, None)
    book.ensure_can_trade(ALICE.client_id)
    with pytest.raises(ForbiddenError):
        propose(book, "0.25")


def test_a_month_above_the_floor_resets_the_streak(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    market(BAD_MARKET)
    book.on_tick(USERS, date(2022, 1, 31), False)
    book.on_tick(USERS, date(2022, 2, 28), False)
    assert book.state.low_streak == 2

    market(GOOD_MARKET)
    book.on_tick(USERS, date(2022, 3, 31), False)

    assert book.state.low_streak == 0
    assert book.state.term is not None
    assert book.state.term.president_id == ALICE.id


def test_replay_rebuilds_measures_approval_and_policy(
    book: GovernmentBook, engine, stored, market, monkeypatch
):
    govern(book, engine, vice=True)
    propose(book)
    congress_says(monkeypatch, True)
    book.on_tick(USERS, FIRST_VOTE, False)

    resumed = GovernmentBook(settings(), engine, lambda *_: None, SEED)

    assert resumed.state.measures == book.state.measures
    assert resumed.state.approvals == book.state.approvals
    assert resumed.policy(date(2022, 6, 1)).rates[LossPool.COMMON] == Decimal("0.20")


def test_measure_in_force_is_announced_on_its_day(
    book: GovernmentBook, engine, market, notices, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, True)
    book.on_tick(USERS, FIRST_VOTE, False)

    book.on_tick(USERS, date(2022, 4, 29), False)
    kinds = [n["kind"] for n in notices]
    assert GovernmentNoticeKind.MEASURE_IN_FORCE.value not in kinds
    book.on_tick(USERS, date(2022, 5, 2), False)

    kinds = [n["kind"] for n in notices]
    assert kinds.count(GovernmentNoticeKind.MEASURE_IN_FORCE.value) == 1
