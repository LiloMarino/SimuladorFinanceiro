"""Livro do governo: partidos, contribuição mensal, apuração dos dois turnos, doação e retomada."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CampaignActionKind,
    CampaignEntryKind,
    CashflowEventType,
    ComputerDifficulty,
    ElectionPhase,
    GovernmentNoticeKind,
    MeasureKind,
    MeasureStatus,
    NewsType,
    PauseReason,
    VicePhase,
    VoterGroup,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import required
from backend.features.government import approval as approval_rules
from backend.features.government import (
    budget_panel,
    campaign,
    caretaker,
    congress,
    election,
    house,
    promises,
    voters,
)
from backend.features.government.calendar import election_cycle
from backend.features.government.campaign_panel import build_campaign, build_history
from backend.features.government.governance import build_governance
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_panel
from backend.features.government.state import Party, replay
from backend.features.notifications.news import Headline
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
FLAGS = [VoterValue.STABILITY, VoterValue.DEVELOPMENT, VoterValue.SAVER_PROTECTION]
# Bandeiras que agradam poucos grupos: o partido fica atrás do computador
NICHE = [VoterValue.FREE_MARKET, VoterValue.SAVER_PROTECTION, VoterValue.PUBLIC_SERVICE]
WORKERS = VoterGroup.FORMAL_WORKERS


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
def headlines() -> list[tuple[date, Headline]]:
    """As manchetes que o livro mandou ao jornal, com o dia de cada uma."""
    return []


@pytest.fixture
def office() -> list[int]:
    """Quem tomou posse: o livro avisa a partida a cada presidente jogador."""
    return []


@pytest.fixture
def book(engine, stored, notices, captured_events, office, headlines) -> GovernmentBook:
    return GovernmentBook(
        settings(),
        engine,
        lambda user, _day: office.append(user.id),
        lambda day, headline: headlines.append((day, headline)),
        SEED,
    )


def found(
    book: GovernmentBook,
    user: UserDTO,
    abbr: str,
    color: str,
    amount="10000",
    flags: list[VoterValue] = FLAGS,
):
    book.found_party(
        user,
        CAMPAIGN_OPEN,
        name=f"Partido {abbr}",
        abbr=abbr,
        color=color,
        flags=flags,
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
            flags=FLAGS,
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
    # A verba de 3 nov já perdeu 1 dia da queda pela metade a cada 3 meses
    assert party.campaign[WORKERS] == voters.campaign_points(
        Decimal(10000)
    ) * campaign.decay_factor(1)
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
    assert party_of(book, ALICE).campaign[WORKERS] == 0


def test_no_collection_before_the_campaign_opens(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED)

    book.on_tick(USERS, date(2020, 8, 3), True)
    book.on_tick(USERS, date(2020, 9, 1), True)

    assert book.state.last_collection is None
    assert engine.get_cash(ALICE.client_id) == Decimal(100000)
    assert party_of(book, ALICE).campaign[WORKERS] == 0


def test_campaign_opening_is_announced_once_and_pauses_the_game(
    book: GovernmentBook, notices
):
    assert book.on_tick(USERS, date(2020, 10, 5), False) is None
    assert notices == []

    assert book.on_tick(USERS, date(2020, 10, 7), False) == PauseReason.CAMPAIGN_OPENED
    assert [notice["kind"] for notice in notices] == ["CAMPAIGN_OPENED"]
    # O aviso leva as datas que o diálogo conta: fecho das chapas e 1º turno
    assert notices[0]["ticket_deadline"] == "2021-09-30"
    assert notices[0]["first_round"] == "2021-10-07"

    assert book.on_tick(USERS, date(2020, 10, 8), False) is None
    assert len(notices) == 1


def test_campaign_opening_on_a_weekend_is_announced_on_the_next_tick(
    engine, stored, notices, captured_events
):
    rules = settings().model_dump()
    # 1º turno numa segunda: a campanha abre num domingo
    rules.update(first_election=date(2021, 10, 4))
    weekend = GovernmentBook(
        SimulationDTO(**rules), engine, lambda *_: None, lambda *_: None, SEED
    )

    weekend.on_tick(USERS, date(2020, 10, 1), False)
    assert weekend.on_tick(USERS, date(2020, 10, 2), False) is None
    assert notices == []
    assert (
        weekend.on_tick(USERS, date(2020, 10, 5), False) == PauseReason.CAMPAIGN_OPENED
    )
    assert [notice["kind"] for notice in notices] == ["CAMPAIGN_OPENED"]


def test_campaign_that_opens_with_the_game_is_announced_on_the_first_day(
    engine, stored, notices, captured_events
):
    rules = settings().model_dump()
    rules.update(first_election=date(2020, 6, 1))
    early = GovernmentBook(
        SimulationDTO(**rules), engine, lambda *_: None, lambda *_: None, SEED
    )

    assert early.on_tick(USERS, date(2020, 1, 1), False) == PauseReason.CAMPAIGN_OPENED
    assert [notice["kind"] for notice in notices] == ["CAMPAIGN_OPENED"]


def test_resumed_game_does_not_repeat_the_campaign_opening(
    engine, stored, notices, captured_events
):
    rules = settings().model_dump()
    rules.update(first_election=date(2020, 6, 1))
    resumed = GovernmentBook(
        SimulationDTO(**rules), engine, lambda *_: None, lambda *_: None, SEED
    )

    assert resumed.on_tick(USERS, date(2020, 2, 3), False) is None
    assert notices == []


def test_reminders_come_before_the_tickets_close_and_on_the_eve_of_the_vote(
    book: GovernmentBook, notices
):
    book.on_tick(USERS, date(2021, 9, 22), False)
    assert notices == []

    # Sem pausa: os lembretes são só toast
    assert book.on_tick(USERS, date(2021, 9, 23), False) is None
    assert [n["kind"] for n in notices] == ["TICKETS_CLOSING"]
    assert notices[0]["ticket_deadline"] == "2021-09-30"

    book.on_tick(USERS, date(2021, 9, 24), False)
    assert len(notices) == 1

    book.on_tick(USERS, date(2021, 10, 5), False)
    assert book.on_tick(USERS, date(2021, 10, 6), False) is None
    kinds = [n["kind"] for n in notices]
    assert kinds == ["TICKETS_CLOSING", "UPDATED", "ELECTION_EVE"]
    assert notices[-1]["first_round"] == "2021-10-07"


def test_election_eve_falls_on_the_last_business_day_before_the_vote():
    # 1º turno numa segunda-feira: a véspera é a sexta
    cycle = election_cycle(date(2021, 10, 4), 0, date(2020, 1, 1))
    assert cycle.first_round == date(2021, 10, 4)
    assert cycle.eve == date(2021, 10, 1)


def test_page_renews_on_the_day_the_tickets_close(book: GovernmentBook, notices):
    book.on_tick(USERS, date(2021, 9, 29), False)
    book.on_tick(USERS, date(2021, 10, 1), False)

    assert [notice["kind"] for notice in notices] == ["UPDATED"]


def run_campaign(book: GovernmentBook) -> None:
    for month in range(11, 13):
        book.on_tick(USERS, date(2020, month, 3), True)
    for month in range(1, 10):
        book.on_tick(USERS, date(2021, month, 3), True)


def test_no_collection_between_the_rounds(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    assert book.state.runoff is not None
    cash = {u.id: engine.get_cash(u.client_id) for u in (ALICE, BOB)}
    collected = book.state.last_collection

    # Mesmo com a virada do mês entre os turnos, ninguém paga contribuição
    book.on_tick(USERS, date(2021, 10, 15), True)
    book.on_tick(USERS, date(2021, 10, 27), True)

    assert {u.id: engine.get_cash(u.client_id) for u in (ALICE, BOB)} == cash
    assert book.state.last_collection == collected


def test_no_collection_after_the_result(book: GovernmentBook, engine: PoliticalEngine):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    assert book.state.pending_term is not None
    cash = {u.id: engine.get_cash(u.client_id) for u in (ALICE, BOB)}
    collected = book.state.last_collection

    # Do resultado à posse e durante o mandato: a campanha seguinte só abre em 2023
    for day in (
        date(2021, 11, 3),
        date(2021, 12, 1),
        TERM_START,
        date(2022, 2, 1),
        date(2022, 3, 1),
    ):
        book.on_tick(USERS, day, True)

    assert {u.id: engine.get_cash(u.client_id) for u in (ALICE, BOB)} == cash
    assert book.state.last_collection == collected


def test_two_rounds_end_with_the_term_starting_in_january(
    book: GovernmentBook, notices
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)

    assert book.on_tick(USERS, FIRST_ROUND, False) == PauseReason.FIRST_ROUND_RESULT
    alice_party = party_of(book, ALICE)
    # Nenhum passou de 50% dos válidos: vão ao 2º turno a Alice e o computador mais votado
    assert alice_party.id in (book.state.runoff or [])
    assert party_of(book, BOB).id not in (book.state.runoff or [])
    assert book.state.pending_term is None

    assert book.on_tick(USERS, RUNOFF, False) == PauseReason.RUNOFF_RESULT
    assert book.state.pending_term is not None
    assert book.state.cycle == 1

    assert book.on_tick(USERS, TERM_START, False) is None
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
    assert party.campaign[WORKERS] == 0
    assert party.spent == 0
    assert book.state.polls == []


def test_donation_goes_only_to_a_finalist_and_only_from_an_eliminated_party(
    book: GovernmentBook, engine: PoliticalEngine
):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
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

    race = book.state.race
    assert race is not None
    before = race.groups[WORKERS].votes[finalist]
    book.donate(BOB, date(2021, 10, 10), finalist, Decimal(1000))

    assert engine.get_cash(BOB.client_id) == eliminated_cash - 1000
    # A doação vira voto do finalista no grupo, tirado dos indecisos
    unit = race.groups[WORKERS].unit
    assert race.groups[WORKERS].votes[finalist] == pytest.approx(
        before + voters.campaign_points(Decimal(1000)) * unit
    )


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


def test_vice_can_come_from_another_party_or_from_no_party(
    book: GovernmentBook, notices
):
    found(book, ALICE, "AAA", RED)
    found(book, CARLA, "CCC", BLUE)
    book.join_party(BOB, CAMPAIGN_OPEN, party_of(book, CARLA).id, Decimal(0))
    party = party_of(book, ALICE)
    book.on_tick(USERS, CAMPAIGN_OPEN, False)

    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)
    assert notices[-1]["kind"] == GovernmentNoticeKind.VICE_INVITED.value
    assert notices[-1]["target"] == "Bob"
    book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    assert notices[-1]["target"] == "Alice"
    assert election.effective_ticket(book.state, party) == (ALICE.id, BOB.id)
    # O vice segue no partido dele
    assert party_of(book, BOB).abbr == "CCC"
    assert BOB.id not in party.members

    # Sai do partido e segue vice; sem partido, também pode ser convidado
    book.leave_party(BOB, CAMPAIGN_OPEN)
    assert election.effective_ticket(book.state, party) == (ALICE.id, BOB.id)
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", None, USERS)
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)
    assert party.vice_id == BOB.id
    assert party.vice_accepted is False
    book.answer_vice(BOB, CAMPAIGN_OPEN, True)
    assert book.state.party_of(BOB.id) is None
    assert election.effective_ticket(book.state, party) == (ALICE.id, BOB.id)


def test_vice_cannot_be_a_bot_or_someone_on_another_ticket(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)

    with pytest.raises(ForbiddenError, match="Bot"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Robo", USERS)
    with pytest.raises(NotFoundError, match="na sala"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Ninguem", USERS)
    # Bob é o candidato padrão do BBB
    with pytest.raises(ConflictError, match="candidato pelo BBB"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Bob", USERS)

    book.set_ticket(BOB, CAMPAIGN_OPEN, "Bob", "Carla", USERS)
    with pytest.raises(ConflictError, match="já foi convidado para vice do BBB"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Carla", USERS)
    book.answer_vice(CARLA, CAMPAIGN_OPEN, True)
    with pytest.raises(ConflictError, match="já é vice do BBB"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Carla", USERS)


def test_vice_of_another_ticket_does_not_run_for_her_own_party(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    book.join_party(CARLA, CAMPAIGN_OPEN, party_of(book, ALICE).id, Decimal(0))
    book.set_ticket(BOB, CAMPAIGN_OPEN, "Bob", "Carla", USERS)
    book.answer_vice(CARLA, CAMPAIGN_OPEN, True)

    with pytest.raises(ConflictError, match="é vice do BBB"):
        book.set_ticket(ALICE, CAMPAIGN_OPEN, "Carla", None, USERS)


def test_panel_lists_every_human_with_the_reason_when_blocked(book: GovernmentBook):
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    networths = {u.id: Decimal(0) for u in USERS}

    def panel(user: UserDTO):
        return build_panel(book, settings(), USERS, user, CAMPAIGN_OPEN, networths)

    options = {o.nickname: o for o in panel(ALICE).vice_options}
    assert set(options) == {"Alice", "Bob", "Carla"}
    assert (options["Bob"].party_abbr, options["Bob"].blocked) == (
        "BBB",
        "candidato pelo BBB",
    )
    assert (options["Carla"].party_abbr, options["Carla"].blocked) == (None, None)
    assert panel(CARLA).vice_options == []

    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Carla", USERS)
    invited = panel(CARLA).my_vice
    assert invited is not None
    assert invited.phase is VicePhase.PENDING
    book.answer_vice(CARLA, CAMPAIGN_OPEN, True)
    accepted = panel(CARLA).my_vice
    assert accepted is not None
    assert accepted.phase is VicePhase.ACCEPTED
    assert panel(BOB).my_vice is None
    options = {o.nickname: o for o in panel(BOB).vice_options}
    assert options["Carla"].blocked == "já é vice do AAA"


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
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.donate(BOB, date(2021, 10, 10), party_of(book, ALICE).id, Decimal(500))
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)

    rebuilt = replay(stored)

    assert rebuilt.cycle == book.state.cycle
    assert rebuilt.term == book.state.term
    assert rebuilt.results == book.state.results
    assert {
        p.id: (p.members, p.campaign, p.radar) for p in rebuilt.parties.values()
    } == {p.id: (p.members, p.campaign, p.radar) for p in book.state.parties.values()}


def test_resumed_book_starts_from_the_stored_events(
    book: GovernmentBook, engine, stored, notices
):
    found(book, ALICE, "AAA", RED, "10000")
    book.on_tick(USERS, date(2020, 11, 3), True)

    resumed = GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)

    assert party_of(resumed, ALICE).campaign == party_of(book, ALICE).campaign
    assert resumed.state.last_collection == date(2020, 11, 1)


def test_panel_follows_the_phase_of_the_race(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
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

# Inflação na meta, SELIC no ponto neutro e bolsa em alta: os grupos miram acima de 50
GOOD_MARKET = approval_rules.Market(
    inflation=Decimal("0.03"),
    selic=Decimal("0.10"),
    stocks=Decimal("0.15"),
    target=Decimal("0.04"),
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
        monkeypatch.setattr(approval_rules, "market_on", lambda _day, *_: value)

    use(GOOD_MARKET)
    return use


@pytest.fixture
def bleak(monkeypatch: pytest.MonkeyPatch) -> None:
    """Um governo que nenhum grupo aprova: o alvo de todos é zero e a satisfação só desce."""
    monkeypatch.setattr(
        approval_rules,
        "group_target",
        lambda *_: approval_rules.GroupTarget(Decimal(0), []),
    )


def close_months(book: GovernmentBook, count: int, first: date = FIRST_VOTE):
    """Fecha `count` meses do governo a partir do mês de `first`; devolve o motivo da última pausa."""
    paused = None
    year, month = first.year, first.month
    for _ in range(count):
        paused = book.on_tick(USERS, congress.last_business_day(year, month), False)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return paused


def congress_says(monkeypatch: pytest.MonkeyPatch, approved: bool) -> None:
    """A casa inteira vota Sim (aprova) ou Não (rejeita), sem desobediência."""

    def count(_key, _seed, current: house.House, *_) -> house.Tally:
        blocs = {
            bloc.key: house.BlocVote(
                bloc.seats,
                approved,
                bloc.seats if approved else 0,
                0 if approved else bloc.seats,
                0,
            )
            for bloc in current.seated
        }
        yes = sum(v.yes for v in blocs.values())
        return house.Tally(yes, house.SEATS - yes, blocs)

    monkeypatch.setattr(house, "count", count)


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
    assert measure.tally is not None
    assert measure.tally.yes == house.SEATS
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
    start = dict(book.state.satisfaction)

    book.on_tick(USERS, FIRST_VOTE, False)

    [point] = book.state.approvals
    assert point.day == FIRST_VOTE
    # Cada grupo andou um terço do caminho até o alvo
    targets = required(book.approval(FIRST_VOTE)).targets
    for group, value in point.satisfaction.items():
        expected = approval_rules.next_satisfaction(start[group], targets[group].target)
        assert value == expected
    assert book.state.low_streak == 0
    # Fechado o mês, a mesma data não mede de novo
    book.on_tick(USERS, FIRST_VOTE, False)
    assert len(book.state.approvals) == 1


def test_each_group_starts_satisfied_in_the_proportion_it_voted_for_the_winner(
    book: GovernmentBook, engine
):
    govern(book, engine)

    start = book.state.satisfaction
    assert set(start) == set(VoterGroup)
    assert all(0 < value < 100 for value in start.values())
    # A posse parte da fatia de cada grupo no vencedor: sai do 2º turno, que decidiu
    final = book.state.results[-1]
    assert final.round == 2
    winner_share = final.shares[required(final.winner_id)] * 100
    assert abs(approval_rules.overall(start) - winner_share) < 10


def test_president_wallet_is_frozen_and_the_others_keep_trading(
    book: GovernmentBook, engine
):
    govern(book, engine)

    with pytest.raises(ConflictError, match="carteira volta a operar"):
        book.ensure_can_trade(ALICE.client_id)
    book.ensure_can_trade(BOB.client_id)
    assert book.term_end() == date(2025, 12, 31)


def test_six_closings_below_the_floor_after_the_grace_remove_the_president(
    book: GovernmentBook, engine, market, bleak, office, notices, monkeypatch
):
    govern(book, engine, vice=True)
    propose(book)
    congress_says(monkeypatch, True)

    # No 1º ano o piso não conta: nenhum fechamento soma à contagem
    assert close_months(book, 12) is None
    assert book.state.low_streak == 0
    assert required(book.approval(date(2022, 12, 31))).value < approval_rules.FLOOR

    # Do 13º mês em diante a contagem corre; o aviso vem no 5º fechamento abaixo do piso
    assert close_months(book, 5, date(2023, 1, 31)) is None
    assert book.state.low_streak == 5
    assert GovernmentNoticeKind.IMPEACHMENT_WARNING.value in [
        n["kind"] for n in notices
    ]
    # O 6º fechamento abre o pedido; a casa o vota no dia de votação do mês seguinte
    assert close_months(book, 1, date(2023, 6, 30)) is None
    request = book.state.request
    assert request is not None
    assert request.vote_day == date(2023, 7, 31)
    propose(book, "0.25")
    assert close_months(book, 1, date(2023, 7, 31)) == PauseReason.IMPEACHMENT

    term = book.state.term
    assert term is not None
    assert (term.president_id, term.succession) == (BOB.id, True)
    assert office[-1] == BOB.id
    # A fila não votada de quem saiu some; o sucessor começa no ponto em que o governo caiu
    assert book.state.measures[2].status is MeasureStatus.DROPPED
    assert term.satisfaction == book.state.satisfaction
    assert book.state.approvals == []
    book.ensure_can_trade(ALICE.client_id)
    with pytest.raises(ConflictError):
        book.ensure_can_trade(BOB.client_id)
    assert book.state.impeachments[0].successor_id == BOB.id


def test_impeachment_hands_the_office_to_a_vice_from_another_party(
    book: GovernmentBook, engine, market, bleak, office, monkeypatch
):
    engine.classification = SECTORS
    found(book, ALICE, "AAA", RED, "10000")
    book.set_ticket(ALICE, CAMPAIGN_OPEN, "Alice", "Carla", USERS)
    book.answer_vice(CARLA, CAMPAIGN_OPEN, True)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)
    book.on_tick(USERS, TERM_START, False)

    assert close_months(book, 19) == PauseReason.IMPEACHMENT

    term = book.state.term
    assert term is not None
    assert (term.president_id, term.succession) == (CARLA.id, True)
    assert office[-1] == CARLA.id
    assert book.state.party_of(CARLA.id) is None


def test_impeachment_without_a_vice_hands_the_office_to_the_largest_computer_bloc(
    book: GovernmentBook, engine, market, bleak, headlines, monkeypatch
):
    govern(book, engine)

    assert close_months(book, 19) == PauseReason.IMPEACHMENT

    day = date(2023, 7, 31)
    heir = required(
        caretaker.successor(
            book.state.house_on(day), {p.id for p in book.state.computer_parties()}
        )
    )
    term = required(book.state.term)
    assert (term.president_id, term.party_id) == (None, heir.party_id)
    assert required(book.caretaker()).abbr == heir.abbr
    assert headlines[-1][1].text.endswith(f"{heir.abbr} assume o governo")
    # A carteira de quem saiu volta a operar, e jogador nenhum propõe no lugar do computador
    book.ensure_can_trade(ALICE.client_id)
    with pytest.raises(ForbiddenError):
        propose(book, "0.25")


def test_computer_government_proposes_by_its_voters_and_the_house_votes(
    book: GovernmentBook, engine, market, bleak, stored, monkeypatch
):
    govern(book, engine)
    close_months(book, 19)
    party = required(book.caretaker())

    # No pregão seguinte o computador leva à fila a medida que os eleitores dele mais querem
    book.on_tick(USERS, date(2023, 8, 1), False)
    [first] = book._queue()
    assert (first.proposer_id, first.party_id) == (None, party.id)
    assert book.proposer_name(first) == party.candidate_name
    bloc = required(book.state.house_on(date(2023, 8, 1)).of_party(party.id))
    baselines = {
        kind: required(book.latest_value(kind)) for kind in promises.GENERAL_KINDS
    }
    choice = required(caretaker.pick(bloc.mix, baselines, set()))
    assert (first.kind, first.value) == (choice.kind, choice.value)
    # A bancada do partido que governa vota Sim na medida dele
    orientations, _, _ = book.measure_orientations(first, date(2023, 8, 1))
    assert orientations[bloc.key] is True
    # A sala vê a medida na fila em nome do candidato do computador, e a aprovação corre
    panel = build_governance(book, engine, USERS, ALICE, date(2023, 8, 1))
    assert [m.proposer for m in panel.queue] == [party.candidate_name]
    assert panel.approval is not None
    assert not panel.is_president

    # A casa vota no fechamento; a aprovação anda, e o piso não conta para o computador
    congress_says(monkeypatch, True)
    assert close_months(book, 3, date(2023, 8, 31)) is None
    assert book.state.measures[first.id].status is MeasureStatus.APPROVED
    assert len(book.state.approvals) == 3
    assert book.state.low_streak == 0
    assert book.state.request is None
    # Cada tipo de medida anda um passo por governo: a seguinte é de outro tipo
    kinds = [m.kind for m in book.state.measures.values() if book.is_current(m)]
    assert len(kinds) == len(set(kinds)) >= 3

    rebuilt = replay(stored)
    assert rebuilt.measures == book.state.measures
    assert rebuilt.term == book.state.term


def test_a_closing_above_the_floor_resets_the_streak(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    with monkeypatch.context() as bleak_month:
        bleak_month.setattr(
            approval_rules,
            "group_target",
            lambda *_: approval_rules.GroupTarget(Decimal(0), []),
        )
        close_months(book, 14)
    assert book.state.low_streak == 2

    # Um alvo alto leva a aprovação de volta acima do piso em poucos meses
    monkeypatch.setattr(
        approval_rules,
        "group_target",
        lambda *_: approval_rules.GroupTarget(Decimal(100), []),
    )
    close_months(book, 3, date(2023, 3, 31))

    assert book.state.low_streak == 0
    assert book.state.term is not None
    assert book.state.term.president_id == ALICE.id


def test_months_the_groups_approve_or_reprove_move_the_governing_party(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    def targets(group_targets: dict[VoterGroup, int]):
        monkeypatch.setattr(
            approval_rules,
            "group_target",
            lambda group, *_: approval_rules.GroupTarget(
                Decimal(group_targets[group]), []
            ),
        )

    # Metade dos grupos mira 100 (aprova) e a outra mira 0 (reprova), partindo do meio
    targets({g: 100 if i % 2 else 0 for i, g in enumerate(VoterGroup)})
    close_months(book, 6)

    approving = [g for i, g in enumerate(VoterGroup) if i % 2]
    reproving = [g for i, g in enumerate(VoterGroup) if not i % 2]
    for group in approving:
        assert party.term_support[group] > 0
        assert party.rejection[group] <= before[group]
    for group in reproving:
        assert party.term_support[group] < 0
        assert party.rejection[group] > before[group]


def test_replay_rebuilds_measures_approval_and_policy(
    book: GovernmentBook, engine, stored, market, monkeypatch
):
    govern(book, engine, vice=True)
    propose(book)
    congress_says(monkeypatch, True)
    book.on_tick(USERS, FIRST_VOTE, False)

    resumed = GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)

    assert resumed.state.measures == book.state.measures
    assert resumed.state.approvals == book.state.approvals
    assert resumed.state.satisfaction == book.state.satisfaction
    assert party_of(resumed, ALICE).term_support == party_of(book, ALICE).term_support
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


# Bandeiras, perfil e pesquisa


def test_party_needs_three_flags_without_both_extremes(book: GovernmentBook):
    with pytest.raises(UnprocessableEntityError, match="3 bandeiras"):
        found(book, ALICE, "AAA", RED, flags=FLAGS[:2])
    with pytest.raises(UnprocessableEntityError, match="não andam juntas"):
        found(
            book,
            ALICE,
            "AAA",
            RED,
            flags=[VoterValue.FREE_MARKET, VoterValue.SOCIAL_JUSTICE, FLAGS[0]],
        )


def test_founder_of_a_party_without_flags_chooses_them_once(
    book: GovernmentBook, engine, stored
):
    found(book, ALICE, "AAA", RED)
    founded = next(e for e in stored if e.payload.get("abbr") == "AAA")
    founded.payload.pop("flags")
    resumed = GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)
    party = party_of(resumed, ALICE)
    assert party.flags is None
    assert set(party.radar.values()) == {voters.RADAR_NEUTRAL}

    with pytest.raises(ConflictError, match="nenhum partido"):
        resumed.set_flags(CARLA, CAMPAIGN_OPEN, FLAGS)
    resumed.set_flags(ALICE, CAMPAIGN_OPEN, FLAGS)

    party = party_of(resumed, ALICE)
    assert party.flags == tuple(FLAGS)
    assert party.radar[FLAGS[0]] == voters.RADAR_FLAG
    with pytest.raises(ConflictError, match="já foram escolhidas"):
        resumed.set_flags(ALICE, CAMPAIGN_OPEN, FLAGS)


def test_approved_measure_moves_the_profile_of_the_governing_party(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book)
    congress_says(monkeypatch, True)

    book.on_tick(USERS, FIRST_VOTE, False)

    # Subir o IR do ganho comum de 15% para 20% recua o mercado e avança a justiça social
    party = party_of(book, ALICE)
    assert party.radar[VoterValue.FREE_MARKET] == voters.RADAR_NEUTRAL - 6
    assert party.radar[VoterValue.SOCIAL_JUSTICE] == voters.RADAR_NEUTRAL + 6
    assert party.radar[VoterValue.DEVELOPMENT] == voters.RADAR_FLAG - 2
    assert [m.measure_id for m in party.moves] == [1]


def test_panel_publishes_the_poll_with_margin_and_the_exact_standing_to_members(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED)
    run_campaign(book)
    exact_rules = settings().model_copy(update={"poll_margin": False})

    def panel(user: UserDTO, rules: SimulationDTO):
        return build_panel(book, rules, USERS, user, date(2021, 9, 10), {})

    published = panel(ALICE, settings())
    exact = panel(ALICE, exact_rules)

    assert len(published.electorate) == len(VoterGroup)
    assert panel(CARLA, settings()).electorate == []
    poll, truth = published.polls[-1], exact.polls[-1]
    assert (poll.margin, truth.margin) == (voters.TOTAL_MARGIN, 0)
    for group, real in zip(poll.groups, truth.groups, strict=True):
        assert group.margin == voters.MARGINS[group.group]
        for shown, value in zip(group.entries, real.entries, strict=True):
            assert abs(shown.points - value.points) <= group.margin
    assert poll.entries != truth.entries
    assert published.runoff_race is None


# Ações avulsas de campanha

ACTION_DAY = date(2020, 11, 10)
RETIREES = VoterGroup.RETIREES


@pytest.fixture
def dice(monkeypatch: pytest.MonkeyPatch):
    """Fixa o número que o dado vai dar; a TV rola dois dados com o mesmo número."""

    def fix(roll: int) -> None:
        monkeypatch.setattr(
            campaign,
            "roll_dice",
            lambda _seed, _id, kind: (
                (roll,) * (2 if kind is CampaignActionKind.TV else 1)
            ),
        )

    return fix


def two_parties(book: GovernmentBook) -> tuple[Party, Party]:
    found(book, ALICE, "AAA", RED)
    found(book, BOB, "BBB", BLUE)
    return party_of(book, ALICE), party_of(book, BOB)


def test_event_is_paid_on_click_and_lifts_the_group(
    book: GovernmentBook, engine: PoliticalEngine, notices
):
    mine, _ = two_parties(book)
    cash = engine.get_cash(ALICE.client_id)
    spent = mine.spent
    support = mine.standing(RETIREES).support

    result = book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, None
    )

    record = result.record
    price = campaign.PRICES[CampaignActionKind.EVENT]
    assert engine.get_cash(ALICE.client_id) == cash - price
    assert record.rolls == campaign.roll_dice(SEED, record.id, CampaignActionKind.EVENT)
    assert result.support_before == support
    assert mine.spent == spent + price
    assert mine.campaign[RETIREES] == pytest.approx(record.support)
    assert notices[-1]["kind"] == GovernmentNoticeKind.CAMPAIGN_ACTION.value
    assert notices[-1]["party_abbr"] == "AAA"


def test_any_member_acts_and_the_return_halves_for_the_whole_party(
    book: GovernmentBook, dice
):
    mine, _ = two_parties(book)
    book.join_party(CARLA, CAMPAIGN_OPEN, mine.id, Decimal(0))
    dice(10)

    first = book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.RALLY, RETIREES, None
    ).record
    second = book.campaign_action(
        CARLA, ACTION_DAY, CampaignActionKind.RALLY, RETIREES, None
    ).record
    other_group = book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.RALLY, WORKERS, None
    ).record
    next_month = book.campaign_action(
        ALICE, date(2020, 12, 2), CampaignActionKind.RALLY, RETIREES, None
    ).record

    assert (first.rate, second.rate) == (1, Decimal("0.5"))
    assert (other_group.rate, next_month.rate) == (1, 1)
    assert second.user_id == CARLA.id


def test_the_card_names_who_made_the_first_action_of_the_month(
    book: GovernmentBook, dice
):
    mine, _ = two_parties(book)
    book.join_party(CARLA, CAMPAIGN_OPEN, mine.id, Decimal(0))
    dice(10)
    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, None)
    book.campaign_action(
        CARLA, ACTION_DAY + timedelta(days=1), CampaignActionKind.EVENT, RETIREES, None
    )

    panel = build_campaign(book, [ALICE, CARLA], CARLA, ACTION_DAY + timedelta(days=2))

    event = next(a for a in panel.actions if a.action is CampaignActionKind.EVENT)
    by_group = {t.group: t for t in event.targets}
    assert by_group[RETIREES].uses_this_month == 2
    assert by_group[RETIREES].first_by == ALICE.nickname
    assert by_group[RETIREES].first_day == ACTION_DAY
    assert by_group[WORKERS].first_by is None
    assert by_group[WORKERS].first_day is None


def test_tv_reaches_every_group_with_the_higher_of_two_dice(
    book: GovernmentBook, monkeypatch: pytest.MonkeyPatch
):
    mine, _ = two_parties(book)
    monkeypatch.setattr(campaign, "roll_dice", lambda *_: (3, 16))

    record = book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.TV, None, None
    ).record

    assert record.roll == 16
    assert record.support > 0
    for group in VoterGroup:
        assert mine.campaign[group] == pytest.approx(record.support)


def test_attack_takes_support_from_the_rival_in_the_group(book: GovernmentBook, dice):
    mine, rival = two_parties(book)
    dice(10)

    record = book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, rival.id
    ).record

    assert rival.campaign[RETIREES] == pytest.approx(
        -campaign.NORMAL_GAIN[CampaignActionKind.ATTACK]
    )
    assert mine.campaign[RETIREES] == 0
    assert record.target_id == rival.id


def test_attack_disaster_backfires_as_rejection_for_the_attacker(
    book: GovernmentBook, dice
):
    mine, rival = two_parties(book)
    dice(1)

    book.campaign_action(
        ALICE, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, rival.id
    )

    assert mine.rejection[RETIREES] > 0
    assert rival.campaign[RETIREES] == 0


def test_event_repairs_rejection_up_to_the_campaign_limit(book: GovernmentBook, dice):
    mine, _ = two_parties(book)
    mine.rejection[RETIREES] = Decimal(10)
    dice(10)

    for day in range(2, 10):
        book.campaign_action(
            ALICE, date(2020, 11, day), CampaignActionKind.EVENT, RETIREES, None
        )

    assert mine.repaired[RETIREES] == campaign.EVENT_REPAIR_LIMIT
    assert mine.rejection[RETIREES] == 10 - campaign.EVENT_REPAIR_LIMIT


def test_failed_action_charges_nothing(book: GovernmentBook, engine: PoliticalEngine):
    mine, rival = two_parties(book)
    cash = engine.get_cash(ALICE.client_id)

    with pytest.raises(UnprocessableEntityError, match="grupo"):
        book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.EVENT, None, None)
    with pytest.raises(UnprocessableEntityError, match="todos os grupos"):
        book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.TV, RETIREES, None)
    with pytest.raises(NotFoundError, match="rival"):
        book.campaign_action(
            ALICE, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, None
        )
    with pytest.raises(ConflictError, match="rival"):
        book.campaign_action(
            ALICE, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, mine.id
        )
    with pytest.raises(UnprocessableEntityError, match="rival"):
        book.campaign_action(
            ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, rival.id
        )
    assert engine.get_cash(ALICE.client_id) == cash

    engine.add_cash(ALICE.client_id, -(cash - 100))
    with pytest.raises(ConflictError, match="Caixa insuficiente"):
        book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.TV, None, None)
    assert engine.get_cash(ALICE.client_id) == 100
    assert book.state.actions == []


def test_actions_are_for_members_during_the_campaign_until_the_eve(
    book: GovernmentBook,
):
    two_parties(book)

    with pytest.raises(ConflictError, match="partido"):
        book.campaign_action(CARLA, ACTION_DAY, CampaignActionKind.TV, None, None)
    with pytest.raises(ForbiddenError):
        book.campaign_action(BOT, ACTION_DAY, CampaignActionKind.TV, None, None)
    with pytest.raises(ConflictError, match="véspera"):
        book.campaign_action(ALICE, FIRST_ROUND, CampaignActionKind.TV, None, None)

    eve = FIRST_ROUND - timedelta(days=1)
    assert book.campaign_closed_reason(eve) is None
    book.campaign_action(ALICE, eve, CampaignActionKind.TV, None, None)


def test_between_the_rounds_only_the_finalists_act_until_the_eve(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    book.on_tick(USERS, FIRST_ROUND, False)
    gap = date(2021, 10, 10)

    with pytest.raises(ConflictError, match="só os finalistas"):
        book.campaign_action(BOB, gap, CampaignActionKind.TV, None, None)
    with pytest.raises(ConflictError, match="véspera do 2º turno"):
        book.campaign_action(ALICE, RUNOFF, CampaignActionKind.TV, None, None)

    race = book.state.race
    assert race is not None
    before = race.groups[WORKERS].votes[party_of(book, ALICE).id]
    book.campaign_action(ALICE, gap, CampaignActionKind.EVENT, WORKERS, None)
    assert race.groups[WORKERS].votes[party_of(book, ALICE).id] >= before


def test_campaign_support_halves_every_three_months(book: GovernmentBook, dice):
    mine, _ = two_parties(book)
    dice(10)
    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.RALLY, RETIREES, None)
    start = mine.campaign[RETIREES]

    book.on_tick(USERS, ACTION_DAY + timedelta(days=campaign.HALF_LIFE_DAYS), False)

    assert mine.campaign[RETIREES] == pytest.approx(start / 2)


def test_replay_restores_actions_decay_and_repairs(book: GovernmentBook, stored):
    _, rival = two_parties(book)
    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, None)
    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.TV, None, None)
    book.campaign_action(
        ALICE, date(2020, 11, 12), CampaignActionKind.ATTACK, WORKERS, rival.id
    )
    book.on_tick(USERS, date(2020, 12, 20), False)
    book.state.advance(date(2020, 12, 20))

    rebuilt = replay(stored)
    rebuilt.advance(date(2020, 12, 20))

    assert rebuilt.actions == book.state.actions
    assert rebuilt.next_action_id == book.state.next_action_id
    for party_id, party in book.state.parties.items():
        again = rebuilt.parties[party_id]
        for group in VoterGroup:
            assert again.campaign[group] == pytest.approx(party.campaign[group])
        assert again.repaired == party.repaired


def test_computer_spends_part_of_its_monthly_budget_on_actions(
    book: GovernmentBook,
):
    found(book, ALICE, "AAA", RED, "10000")

    book.on_tick(USERS, date(2020, 11, 3), True)

    computers = {p.id for p in book.state.computer_parties()}
    actions = [a for a in book.state.actions if a.user_id is None]
    assert actions
    assert {a.party_id for a in actions} <= computers
    for computer in computers:
        paid = sum(a.price for a in actions if a.party_id == computer)
        assert paid <= book.state.parties[computer].spent


def test_actions_and_charges_reset_after_the_election(book: GovernmentBook):
    found(book, ALICE, "AAA", RED, "8000")
    found(book, BOB, "BBB", BLUE, "2000", NICHE)
    run_campaign(book)
    book.campaign_action(ALICE, date(2021, 9, 10), CampaignActionKind.TV, None, None)

    book.on_tick(USERS, FIRST_ROUND, False)
    book.on_tick(USERS, RUNOFF, False)

    assert book.state.actions == []
    assert book.state.charges == []
    assert all(
        sum(p.repaired.values()) == 0 and p.spent == 0
        for p in book.state.parties.values()
    )


def test_campaign_panel_lists_prices_history_and_received_attacks(
    book: GovernmentBook, dice
):
    mine, _ = two_parties(book)
    dice(10)
    book.campaign_action(ALICE, ACTION_DAY, CampaignActionKind.EVENT, RETIREES, None)
    book.campaign_action(BOB, ACTION_DAY, CampaignActionKind.ATTACK, RETIREES, mine.id)

    panel = build_campaign(book, USERS, ALICE, ACTION_DAY)
    seen_by_rival = build_history(book, USERS, BOB, ACTION_DAY)

    assert panel.open is True
    assert panel.party_abbr == "AAA"
    assert [a.action for a in panel.actions] == list(CampaignActionKind)
    event = next(a for a in panel.actions if a.action is CampaignActionKind.EVENT)
    retirees = next(t for t in event.targets if t.group is RETIREES)
    assert retirees.uses_this_month == 1
    assert retirees.rate == Decimal("0.5")
    assert retirees.repair_limit == campaign.EVENT_REPAIR_LIMIT
    assert {r.abbr for r in panel.rivals} == {"BBB"} | {
        p.abbr for p in book.state.computer_parties()
    }
    assert "AAA" not in {r.abbr for r in panel.rivals}
    kinds = [e.kind for e in panel.recent]
    assert CampaignEntryKind.ATTACK_RECEIVED in kinds
    received = next(
        e for e in panel.recent if e.kind is CampaignEntryKind.ATTACK_RECEIVED
    )
    assert received.rolls == [] and received.roll is None and received.price is None
    assert [e.kind for e in seen_by_rival.entries] == [CampaignEntryKind.ATTACK]
    assert seen_by_rival.entries[0].rolls == [10]


# Jornal da partida


def texts(headlines: list[tuple[date, Headline]], news_type: NewsType) -> list[str]:
    return [h.text for _, h in headlines if h.news_type is news_type]


def test_the_election_reaches_the_journal_from_the_campaign_to_the_inauguration(
    book: GovernmentBook, engine, headlines
):
    govern(book, engine)

    assert texts(headlines, NewsType.PARTY_LIFE)[0] == (
        "Alice funda o AAA, Partido AAA"
    )
    [closed] = [
        t for t in texts(headlines, NewsType.ELECTION_CALENDAR) if "fechadas" in t
    ]
    assert "Alice pelo AAA" in closed
    results = texts(headlines, NewsType.ELECTION_RESULT)
    assert results[-1].startswith("Virada: Alice (AAA) vence o 2º turno, com ")
    posse, house_seated = texts(headlines, NewsType.TERM_STARTED)
    assert posse == "Alice toma posse; o mandato vai até 2025"
    assert house_seated.startswith("Novo Congresso toma posse: ")
    assert headlines[-1][0] == TERM_START


def test_the_proposal_and_the_withdrawal_reach_the_journal(
    book: GovernmentBook, engine, market, headlines
):
    govern(book, engine)
    headlines.clear()

    propose(book)
    [measure_id] = book.state.measures
    book.withdraw(ALICE, TERM_START, measure_id)

    assert texts(headlines, NewsType.MEASURE_PROPOSED) == [
        "Alice propõe: Ações: IR das vendas com lucro em 20%",
        "Alice retira a proposta: Ações: IR das vendas com lucro em 20%",
    ]


def test_the_impeachment_names_the_president_who_falls(
    book: GovernmentBook, engine, market, bleak, headlines
):
    govern(book, engine)

    assert close_months(book, 19) == PauseReason.IMPEACHMENT

    last = texts(headlines, NewsType.ELECTION_RESULT)[-1]
    assert last.startswith("Casa tira Alice (AAA) da Presidência por ")


def test_the_engine_reads_the_risk_premium_from_the_budget(
    book: GovernmentBook, engine
):
    # A dívida de largada passa de 50% do PIB: o Tesouro já cobra prêmio no primeiro dia
    premium = engine.risk_premium_on(CAMPAIGN_OPEN)

    assert premium == book.risk_premium_on(CAMPAIGN_OPEN)
    assert premium == book.budget().premium_on(CAMPAIGN_OPEN)


def test_preview_estimates_what_the_measure_does_to_the_budget(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    cut = book.preview(
        ALICE, TERM_START, MeasureKind.STOCK_PROFIT_RATE, Decimal("0.05"), None, None
    )
    raise_ = book.preview(
        ALICE, TERM_START, MeasureKind.DAY_TRADE_RATE, Decimal("0.30"), None, None
    )

    assert cut.budget.revenue_change < 0
    assert cut.budget.result_after < cut.budget.result_before
    assert cut.budget.debt_after > cut.budget.debt_before
    assert cut.budget.rate_before == Decimal("0.15")
    assert cut.budget.rate_after == Decimal("0.05")
    assert raise_.budget.revenue_change > 0
    assert raise_.budget.debt_after < raise_.budget.debt_before


def test_queue_budget_sums_the_queued_measures_on_the_current_policy(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book, "0.20")

    queue = budget_panel.queue_budget(
        book.budget(),
        book.latest_policy(),
        [m for m in book.state.measures.values() if m.status is MeasureStatus.QUEUED],
        TERM_START,
    )

    assert queue.total > 0
    assert queue.result_if_passes == queue.result_now + queue.total


def test_the_runoff_headline_calls_a_turnaround_when_the_first_round_leader_loses(
    book: GovernmentBook, engine, headlines
):
    govern(book, engine)
    first = next(r for r in book.state.results if r.round == 1)
    finalists = first.finalists
    leader = max(finalists, key=lambda f: (first.points[f], -f))
    other = next(f for f in finalists if f != leader)

    assert book._turned_from(2, finalists, leader) is None
    assert book._turned_from(2, finalists, other) == book.state.parties[leader].abbr
    assert book._turned_from(1, finalists, other) is None
