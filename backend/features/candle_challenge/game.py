"""
O desafio da vela da sala: uma rodada de 10 perguntas que todos respondem ao mesmo
tempo enquanto a partida não começa.

O servidor sorteia e cronometra a rodada numa thread própria e transmite o estado pelo
tempo real. Cada pergunta fica aberta por alguns segundos; ao fechar, a revelação mostra
o ativo, a data, as 5 velas seguintes e o voto de cada um, e a próxima pergunta vem
logo depois. Quem entra no meio assiste à pergunta aberta e joga a partir da próxima.
O placar é da rodada; as vitórias da sala ficam na memória do servidor.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Protocol

from backend.core import repository
from backend.core.dto.candle_challenge import (
    QUESTIONS_PER_ROUND,
    CandleChallengeStateDTO,
    CandleChallengeViewDTO,
    ChallengeDirection,
    ChallengeFinalDTO,
    ChallengeMark,
    ChallengeNoticeEventDTO,
    ChallengeNoticeKind,
    ChallengePhase,
    ChallengePlayerDTO,
    ChallengeQuestionDTO,
    ChallengeRevealDTO,
    ChallengeVoteDTO,
    ChallengeWinsDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.runtime.user_manager import UserManager
from backend.features.achievements.evaluator import (
    unlock_from_lobby,
    unlocked_event,
)
from backend.features.candle_challenge.question import (
    NoQuestionError,
    Question,
    QuestionSource,
)
from backend.features.realtime import notify

logger = logging.getLogger(__name__)

# Tempo com a pergunta aberta e com o resultado na tela, em segundos
QUESTION_SECONDS = 8.0
REVEAL_SECONDS = 5.0


class Store(Protocol):
    """O que o jogo guarda no banco: acertos, recorde e as conquistas que eles desbloqueiam."""

    def hit(self, user: UserDTO) -> None: ...

    def record(self, user: UserDTO) -> tuple[int, date | None]: ...

    def save_record(self, user: UserDTO, streak: int) -> None: ...


class DatabaseStore:
    def hit(self, user: UserDTO) -> None:
        repository.candle_challenge.add_hits(user.id, 1)
        if unlocked := unlock_from_lobby(user.id):
            notify(
                "achievement_unlocked",
                unlocked_event(unlocked).to_json(),
                to=user.client_id,
            )

    def record(self, user: UserDTO) -> tuple[int, date | None]:
        return repository.candle_challenge.record(user.id)

    def save_record(self, user: UserDTO, streak: int) -> None:
        repository.candle_challenge.save_record(
            user.id, streak, datetime.now(UTC).date()
        )


@dataclass
class _Player:
    user: UserDTO
    # Primeira pergunta (pela ordem de abertura) que ele joga
    from_seq: int
    marks: dict[int, ChallengeMark] = field(default_factory=dict)
    hits: int = 0


@dataclass
class _Round:
    id: int
    starter: str
    solo: bool
    players: dict[int, _Player]
    cancel: threading.Event = field(default_factory=threading.Event)
    # Perguntas abertas até agora, contando as anuladas
    seq: int = 0
    # Perguntas fechadas que valeram ponto
    closed: int = 0
    # Número mostrado na tela: o da pergunta aberta ou o da que acabou de fechar
    shown: int = 1
    phase: ChallengePhase = "loading"
    finished: bool = False
    question: Question | None = None
    reveal: ChallengeRevealDTO | None = None
    answers: dict[int, ChallengeDirection] = field(default_factory=dict)
    asked: list[tuple[str, date]] = field(default_factory=list)
    deadline: float = 0.0
    duration: float = 0.0
    streak: int = 0
    best_streak: int = 0
    record_before: int = 0
    record_on_before: date | None = None
    winners: list[str] = field(default_factory=list)


class CandleGame:
    def __init__(
        self,
        source: QuestionSource | None = None,
        store: Store | None = None,
        *,
        question_seconds: float = QUESTION_SECONDS,
        reveal_seconds: float = REVEAL_SECONDS,
        autorun: bool = True,
    ) -> None:
        self._source = source or QuestionSource()
        self._store = store or DatabaseStore()
        self._question_seconds = question_seconds
        self._reveal_seconds = reveal_seconds
        self._autorun = autorun
        self._lock = threading.RLock()
        self._round: _Round | None = None
        self._wins: dict[str, int] = {}
        self._rounds = 0
        self._round_seq = 0

    # =========================
    # Consulta
    # =========================

    def view(self, user: UserDTO) -> CandleChallengeViewDTO:
        with self._lock:
            rnd = self._round
            direction = (
                rnd.answers.get(user.id) if rnd and rnd.phase == "question" else None
            )
            return CandleChallengeViewDTO(state=self._state(), direction=direction)

    def is_active(self) -> bool:
        with self._lock:
            return self._round is not None and not self._round.finished

    # =========================
    # Ações dos jogadores
    # =========================

    def start(self, user: UserDTO) -> None:
        """Abre uma rodada nova com quem pediu; os outros recebem o convite."""
        with self._lock:
            if self._round is not None and not self._round.finished:
                raise ConflictError("Já tem um desafio da vela rolando.")
            humans = [u for u in UserManager.list_active_players() if not u.is_bot]
            solo = len(humans) <= 1
            self._round_seq += 1
            rnd = _Round(
                id=self._round_seq,
                starter=user.nickname,
                solo=solo,
                players={user.id: _Player(user, from_seq=1)},
            )
            if solo:
                rnd.record_before, rnd.record_on_before = self._store.record(user)
            self._round = rnd
        self._publish()
        if self._autorun:
            threading.Thread(
                target=self._run, args=(rnd,), name="candle-challenge", daemon=True
            ).start()

    def join(self, user: UserDTO) -> None:
        with self._lock:
            rnd = self._running()
            if user.id in rnd.players:
                return
            rnd.players[user.id] = _Player(user, from_seq=rnd.seq + 1)
        self._publish()
        self._notice("joined", user.nickname)

    def leave(self, user_id: int) -> None:
        with self._lock:
            rnd = self._round
            if rnd is None or user_id not in rnd.players:
                return
            del rnd.players[user_id]
            if not rnd.players:
                rnd.cancel.set()
                self._round = None
        self._publish()

    def answer(self, user: UserDTO, direction: ChallengeDirection) -> None:
        """Grava (ou troca) a resposta; vale até a pergunta fechar."""
        with self._lock:
            rnd = self._running()
            player = rnd.players.get(user.id)
            if rnd.phase != "question" or player is None or player.from_seq > rnd.seq:
                raise UnprocessableEntityError("Não há pergunta aberta para você.")
            rnd.answers[user.id] = direction
        self._publish()

    def abort(self, kind: ChallengeNoticeKind = "ended_by_match") -> None:
        """Encerra a rodada sem vencedor; os acertos já feitos ficam gravados."""
        with self._lock:
            rnd = self._round
            if rnd is None:
                return
            number = rnd.shown
            was_running = not rnd.finished
            rnd.cancel.set()
            self._round = None
        self._publish()
        if was_running:
            self._notice(kind, None, number)

    # =========================
    # Rodada
    # =========================

    def _run(self, rnd: _Round) -> None:
        try:
            question = self._draw(rnd)
            while question is not None:
                if not self._open(rnd, question):
                    return
                if rnd.cancel.wait(self._question_seconds):
                    return
                self._close(rnd)
                if rnd.closed >= QUESTIONS_PER_ROUND:
                    if not rnd.cancel.wait(self._reveal_seconds):
                        self._finish(rnd)
                    return
                started = time.monotonic()
                question = self._draw(rnd)
                rest = self._reveal_seconds - (time.monotonic() - started)
                if rnd.cancel.wait(max(rest, 0)):
                    return
        except Exception:
            logger.exception("Erro no desafio da vela")
            self.abort("unavailable")

    def _draw(self, rnd: _Round) -> Question | None:
        with self._lock:
            asked = list(rnd.asked)
        try:
            question = self._source.draw(asked)
            # A estatística da dica é calculada aqui, antes da pergunta abrir
            self._source.stats(question.pattern_code)
        except NoQuestionError:
            logger.warning("Sem recorte para o desafio da vela", exc_info=True)
            self.abort("unavailable")
            return None
        return question

    def _open(self, rnd: _Round, question: Question) -> bool:
        with self._lock:
            if self._round is not rnd:
                return False
            rnd.seq += 1
            rnd.phase = "question"
            rnd.question = question
            rnd.asked.append(question.key)
            rnd.answers = {}
            rnd.reveal = None
            rnd.shown = rnd.closed + 1
            rnd.duration = self._question_seconds
            rnd.deadline = time.monotonic() + rnd.duration
        self._publish()
        return True

    def _close(self, rnd: _Round) -> None:
        with self._lock:
            question = rnd.question
            if self._round is not rnd or question is None:
                return
            votes = [
                ChallengeVoteDTO(nickname=p.user.nickname, direction=rnd.answers[uid])
                for uid, p in rnd.players.items()
                if uid in rnd.answers and p.from_seq <= rnd.seq
            ]
            scorers: list[_Player] = []
            if question.outcome != "void":
                rnd.closed += 1
                rnd.shown = rnd.closed
                for uid, player in rnd.players.items():
                    if player.from_seq > rnd.seq:
                        continue
                    direction = rnd.answers.get(uid)
                    mark: ChallengeMark = (
                        "none"
                        if direction is None
                        else "hit"
                        if direction == question.outcome
                        else "miss"
                    )
                    player.marks[rnd.closed] = mark
                    if mark == "hit":
                        player.hits += 1
                        scorers.append(player)
                if rnd.solo:
                    hit = bool(scorers)
                    rnd.streak = rnd.streak + 1 if hit else 0
                    rnd.best_streak = max(rnd.best_streak, rnd.streak)
            rnd.phase = "reveal"
            rnd.duration = self._reveal_seconds
            rnd.deadline = time.monotonic() + rnd.duration
            rnd.reveal = ChallengeRevealDTO(
                ticker=question.ticker,
                start=question.start,
                end=question.end,
                bars=question.bars,
                bars_after=question.bars_after,
                outcome=question.outcome,
                change=question.change,
                votes=votes if question.outcome != "void" else [],
                remaining_ms=int(rnd.duration * 1000),
                duration_ms=int(rnd.duration * 1000),
            )
            beat_record = rnd.solo and rnd.best_streak > rnd.record_before
            solo_user = next(iter(rnd.players.values())).user if rnd.solo else None
            best = rnd.best_streak
        self._publish()
        self._persist(scorers, solo_user if beat_record else None, best)

    def _persist(
        self, scorers: list[_Player], record_user: UserDTO | None, streak: int
    ) -> None:
        """Os acertos e o recorde são extras: um erro ao gravá-los não derruba a rodada."""
        for player in scorers:
            try:
                self._store.hit(player.user)
            except Exception:
                logger.exception("Erro ao gravar o acerto do desafio da vela")
        if record_user is not None:
            try:
                self._store.save_record(record_user, streak)
            except Exception:
                logger.exception("Erro ao gravar o recorde do desafio da vela")

    def _finish(self, rnd: _Round) -> None:
        with self._lock:
            if self._round is not rnd:
                return
            rnd.finished = True
            rnd.phase = "loading"
            rnd.question = None
            rnd.reveal = None
            self._rounds += 1
            top = max((p.hits for p in rnd.players.values()), default=0)
            if not rnd.solo and top > 0:
                rnd.winners = [
                    p.user.nickname for p in rnd.players.values() if p.hits == top
                ]
                for nickname in rnd.winners:
                    self._wins[nickname] = self._wins.get(nickname, 0) + 1
        self._publish()

    # =========================
    # Estado
    # =========================

    def _running(self) -> _Round:
        if self._round is None or self._round.finished:
            raise ConflictError("Não há desafio da vela rolando.")
        return self._round

    def _publish(self) -> None:
        with self._lock:
            payload = self._state().to_json()
        notify("candle_challenge_state", payload)

    def _notice(
        self,
        kind: ChallengeNoticeKind,
        nickname: str | None,
        number: int | None = None,
    ) -> None:
        notify(
            "candle_challenge_notice",
            ChallengeNoticeEventDTO(
                kind=kind, nickname=nickname, number=number
            ).to_json(),
        )

    def _state(self) -> CandleChallengeStateDTO:
        rnd = self._round
        wins = sorted(self._wins.items(), key=lambda w: (-w[1], w[0]))
        wins_dto = [ChallengeWinsDTO(nickname=n, wins=w) for n, w in wins]
        if rnd is None:
            return CandleChallengeStateDTO(
                status="idle",
                phase=None,
                round_id=self._round_seq,
                starter=None,
                solo=False,
                number=0,
                total=QUESTIONS_PER_ROUND,
                question=None,
                reveal=None,
                players=[],
                final=None,
                wins=wins_dto,
                rounds=self._rounds,
                streak=0,
                record=0,
            )
        now = time.monotonic()
        question = None
        if rnd.phase == "question" and rnd.question is not None:
            question = ChallengeQuestionDTO(
                id=rnd.seq,
                pattern_code=rnd.question.pattern_code,
                bars=rnd.question.bars,
                stats=self._source.stats(rnd.question.pattern_code),
                remaining_ms=max(0, int((rnd.deadline - now) * 1000)),
                duration_ms=int(rnd.duration * 1000),
            )
        reveal = rnd.reveal
        if reveal is not None:
            reveal = reveal.model_copy(
                update={"remaining_ms": max(0, int((rnd.deadline - now) * 1000))}
            )
        final = None
        if rnd.finished:
            final = ChallengeFinalDTO(
                winners=rnd.winners,
                best_streak=rnd.best_streak,
                new_record=rnd.solo and rnd.best_streak > rnd.record_before,
                previous_record=rnd.record_before,
                previous_record_on=rnd.record_on_before,
            )
        return CandleChallengeStateDTO(
            status="finished" if rnd.finished else "running",
            phase=None if rnd.finished else rnd.phase,
            round_id=rnd.id,
            starter=rnd.starter,
            solo=rnd.solo,
            number=rnd.shown,
            total=QUESTIONS_PER_ROUND,
            question=question,
            reveal=reveal,
            players=self._players(rnd),
            final=final,
            wins=wins_dto,
            rounds=self._rounds,
            streak=rnd.streak,
            record=rnd.record_before,
        )

    def _players(self, rnd: _Round) -> list[ChallengePlayerDTO]:
        colors = UserManager.room_colors()
        ranked = sorted(rnd.players.values(), key=lambda p: -p.hits)
        players: list[ChallengePlayerDTO] = []
        for index, player in enumerate(ranked):
            tied = index > 0 and ranked[index - 1].hits == player.hits
            position = players[-1].position if tied else index + 1
            eligible = player.from_seq <= rnd.seq
            joined_at = (
                min(player.marks)
                if player.marks
                else rnd.closed + (1 if eligible or rnd.phase == "reveal" else 2)
            )
            players.append(
                ChallengePlayerDTO(
                    nickname=player.user.nickname,
                    color=colors.get(player.user.id, ""),
                    position=position,
                    hits=player.hits,
                    answered=len(player.marks),
                    joined_at=joined_at,
                    replied=rnd.phase == "question" and player.user.id in rnd.answers,
                    last=(
                        player.marks.get(rnd.shown)
                        if rnd.phase == "reveal" and not rnd.finished
                        else None
                    ),
                    marks=[player.marks.get(i) for i in range(1, rnd.closed + 1)],
                )
            )
        return players


candle_game = CandleGame()
