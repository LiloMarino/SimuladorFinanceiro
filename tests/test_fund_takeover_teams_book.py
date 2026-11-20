"""Aquisição hostil em equipes no livro das gestoras: times fixos, assembleia restrita e eliminação da equipe."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

import uuid
from decimal import Decimal
from types import SimpleNamespace

from backend.core.dto.user import UserDTO
from backend.core.enum import GameType
from backend.features.achievements import evaluator
from tests.test_bots import refusal
from tests.test_fund_assembly import (
    BETO,
    CAIO,
    SWAP,
    _assemblable,
    _close_all_sessions,
)
from tests.test_fund_book import TICKER, MemoryFunds, isolated, memory
from tests.test_fund_takeover_offer import ANA, CAP, GESTOR, _lose_the_assembly

# =========================
# Partida: times fixos
# =========================


def test_the_book_refuses_invite_leave_and_removal_in_fixed_teams(memory):
    setup = _assemblable(memory)
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}

    for call in (
        lambda: setup.book.invite_comanager(TICKER, "Caio", Decimal("0.1")),
        lambda: setup.book.answer_comanager_invite(TICKER, CAIO, True),
        lambda: setup.book.leave_comanagement(TICKER, CAIO),
        lambda: setup.book.remove_comanager(TICKER, CAIO.id),
    ):
        detail = refusal(call)
        assert "os times são fixos" in detail


# =========================
# Partida: assembleia só para tomar a gestora de outra equipe
# =========================


def test_the_assembly_refuses_a_convener_from_the_funds_own_team(memory):
    setup = _assemblable(memory)
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}

    detail = refusal(lambda: setup.book.convene_assembly(TICKER, CAIO, None))

    assert "assembleia serve para tomar a gestora de outra equipe" in detail


def test_the_assembly_refuses_a_candidate_from_the_funds_own_team(memory):
    setup = _assemblable(memory)
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}

    detail = refusal(lambda: setup.book.convene_assembly(TICKER, ANA, "Caio"))

    assert "assembleia serve para tomar a gestora de outra equipe" in detail


def test_another_team_can_convene_the_assembly(memory):
    setup = _assemblable(memory)
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}

    setup.book.convene_assembly(TICKER, ANA, None)

    assert setup.book.get(TICKER).terms.manager_user_id == GESTOR.id


def test_the_panel_blocks_the_swap_for_the_funds_own_team_only(memory):
    setup = _assemblable(memory)
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}
    fund = setup.book.get(TICKER)

    def swap(viewer):
        panel = setup.book.assembly_panel(fund, viewer, {}, {})
        return next(o for o in panel.options if o.agenda is SWAP)

    assert (swap(CAIO).can_convene, swap(CAIO).block) == (False, "team")
    assert swap(ANA).can_convene


# =========================
# Partida: tomar a gestora elimina a equipe inteira
# =========================


def _team_lose_the_assembly(memory: MemoryFunds):
    """A equipe do gestor (ele e o Caio, co-gestor) perde a gestora para a Ana, da outra equipe."""
    setup = _assemblable(memory)
    setup.book._manager_cap = CAP
    setup.book._teams = lambda: {GESTOR.id: 1, CAIO.id: 1, ANA.id: 2, BETO.id: 2}
    setup.book.seat_comanager(TICKER, CAIO.id, Decimal("0.2"))
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)
    _close_all_sessions(setup)
    return setup


def test_the_taken_gestora_eliminates_the_whole_team(memory):
    setup = _team_lose_the_assembly(memory)

    fund = setup.book.get(TICKER)
    assert fund.terms.manager_user_id == ANA.id
    assert set(setup.book.eliminated) == {GESTOR.id, CAIO.id}


def test_the_co_managers_of_the_lost_team_lose_their_seat(memory):
    setup = _team_lose_the_assembly(memory)

    assert setup.book.get(TICKER).comanagers == []


def test_a_taken_gestora_without_teams_keeps_only_the_founder_eliminated(memory):
    setup = _lose_the_assembly(memory)

    assert set(setup.book.eliminated) == {GESTOR.id}


def test_the_last_standing_team_wins_with_all_its_members_and_no_bot(monkeypatch):
    ana = UserDTO(id=1, client_id=uuid.uuid4(), nickname="Ana")
    caio = UserDTO(id=2, client_id=uuid.uuid4(), nickname="Caio")
    beto = UserDTO(id=3, client_id=uuid.uuid4(), nickname="Beto")
    robot = UserDTO(id=4, client_id=uuid.uuid4(), nickname="Robô", is_bot=True)
    overview = SimpleNamespace(
        players=[
            SimpleNamespace(player_nickname="Beto", team=2),
            SimpleNamespace(player_nickname="Ana", team=1),
            SimpleNamespace(player_nickname="Caio", team=1),
            SimpleNamespace(player_nickname="Robô", team=None),
        ],
        teams=[SimpleNamespace(team=1), SimpleNamespace(team=2)],
        parties=[],
        game_type=GameType.FUND_TAKEOVER,
        survivor_nickname=None,
    )
    monkeypatch.setattr(evaluator, "build_overview_report", lambda _ids: overview)

    result = evaluator.match_result(1, [ana, caio, beto, robot], False)

    assert result.winners == {ana.id, caio.id}
