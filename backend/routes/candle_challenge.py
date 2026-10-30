from fastapi import APIRouter, status

from backend.core.dependencies import ClientID
from backend.core.dto.candle_challenge import (
    AnswerChallengeRequest,
    CandleChallengeViewDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import ConflictError, ForbiddenError
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.runtime.user_manager import UserManager
from backend.features.candle_challenge.game import candle_game

candle_challenge_router = APIRouter(
    prefix="/api/candle-challenge", tags=["Candle challenge"]
)


def _player(client_id: ClientID) -> UserDTO:
    user = UserManager.get_user(client_id)
    if user is None or user.is_bot:
        raise ForbiddenError("Só quem está na sala joga o desafio da vela.")
    return user


@candle_challenge_router.get(
    "",
    response_model=CandleChallengeViewDTO,
    summary="Desafio da vela da sala",
    description=(
        "O estado do desafio da vela do lobby: a pergunta aberta ou a revelação, o "
        "placar da rodada e a resposta de quem pergunta à pergunta aberta."
    ),
)
def get_candle_challenge(client_id: ClientID):
    return candle_game.view(_player(client_id))


@candle_challenge_router.post(
    "/start",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Começar o desafio da vela",
    description=(
        "Abre uma rodada de 10 perguntas com quem pediu; os outros jogadores da sala "
        "recebem o convite. Vale também para jogar de novo depois do fim."
    ),
)
def start_candle_challenge(client_id: ClientID):
    user = _player(client_id)
    if SimulationManager.has_active_simulation():
        raise ConflictError("O desafio da vela só roda no lobby.")
    candle_game.start(user)


@candle_challenge_router.post(
    "/join",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Entrar no desafio da vela",
    description="Entra na rodada em andamento; quem entra joga a partir da próxima pergunta.",
)
def join_candle_challenge(client_id: ClientID):
    candle_game.join(_player(client_id))


@candle_challenge_router.post(
    "/answer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Responder ao desafio da vela",
    description="Grava sobe ou desce; dá para trocar a resposta até a pergunta fechar.",
)
def answer_candle_challenge(client_id: ClientID, payload: AnswerChallengeRequest):
    candle_game.answer(_player(client_id), payload.direction)


@candle_challenge_router.post(
    "/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair do desafio da vela",
    description="Sai da rodada; quando não sobra ninguém, ela termina.",
)
def leave_candle_challenge(client_id: ClientID):
    candle_game.leave(_player(client_id).id)
