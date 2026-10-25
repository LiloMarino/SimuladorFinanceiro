"""
O desafio da vela. O padrão que fecha no último pregão pergunta "sobe ou desce?"; a
resposta vale até o pregão seguinte e é conferida no fechamento do 5º pregão depois
do padrão, pelas mesmas regras que marcam o padrão no gráfico.

O histórico de cada ativo chega pronto de quem chama (já com o impacto de preço e
terminando na data da simulação), então o serviço não conhece o relógio da partida.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import cast

import pandas as pd

from backend.core import repository
from backend.core.dto.candle_challenge import (
    CandleChallengeDTO,
    CandleChallengeRankingDTO,
    ChallengeAnswerDTO,
    ChallengeDirection,
    ChallengeRankEntryDTO,
    ChallengeRecordDTO,
    ChallengeResult,
    ChallengeScoreDTO,
    OpenChallengeDTO,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.core.utils import next_business_day
from backend.features.technical_analysis.patterns import (
    OUTCOME_SESSIONS,
    PATTERNS,
    Occurrence,
    build_candle_patterns,
    detect,
    is_hit,
    outcome,
)

# O histórico de um ativo até a data da simulação; None quando o ativo não existe
type FrameOf = Callable[[str], pd.DataFrame | None]


def current(
    simulation_id: int, user_id: int, ticker: str, frame: pd.DataFrame
) -> CandleChallengeDTO:
    """A pergunta de hoje, a última resposta do jogador nesse ativo e o placar dele."""
    hits, answered = repository.candle_challenge.score(simulation_id, user_id)
    score = ChallengeScoreDTO(hits=hits, answered=answered)
    if len(frame) == 0:
        return CandleChallengeDTO(open=None, last=None, score=score)

    occurrences = detect(frame)
    last_pos = len(frame) - 1
    today = _sided_ending_at(occurrences, last_pos)
    open_challenge = None
    if today is not None and not _answered(simulation_id, user_id, ticker, today):
        open_challenge = OpenChallengeDTO(
            pattern_code=today.code,
            pattern_date=today.end.date(),
            price=float(frame["close"].iloc[last_pos]),
            settles_on=_after_sessions(today.end.date(), OUTCOME_SESSIONS),
        )

    # O desafio de ontem que ninguém respondeu sai de cena no pregão seguinte
    yesterday = _sided_ending_at(occurrences, last_pos - 1)
    expired = (
        yesterday
        if yesterday is not None
        and not _answered(simulation_id, user_id, ticker, yesterday)
        else None
    )
    record = repository.candle_challenge.latest(simulation_id, user_id, ticker)
    answer = None
    if record is not None and (
        expired is None or record.pattern_date > expired.end.date()
    ):
        answer = _answer_dto(record, frame)
    elif expired is not None:
        answer = _expired_dto(expired, frame)
    return CandleChallengeDTO(open=open_challenge, last=answer, score=score)


def answer(
    simulation_id: int,
    user_id: int,
    ticker: str,
    direction: ChallengeDirection,
    frame: pd.DataFrame,
) -> CandleChallengeDTO:
    """Grava a resposta ao desafio de hoje; só vale enquanto o último pregão é o do padrão."""
    today = _sided_ending_at(detect(frame), len(frame) - 1) if len(frame) > 0 else None
    if today is None:
        raise UnprocessableEntityError(
            "Não há desafio aberto neste ativo: o padrão já passou."
        )
    created = repository.candle_challenge.create(
        ChallengeRecordDTO(
            simulation_id=simulation_id,
            user_id=user_id,
            ticker=ticker,
            pattern_date=today.end.date(),
            pattern_code=today.code,
            direction=direction,
            answered_on=today.end.date(),
            result=None,
            settled_on=None,
        )
    )
    if not created:
        raise ConflictError("Você já respondeu a este desafio.")
    return current(simulation_id, user_id, ticker, frame)


def settle(simulation_id: int, frame_of: FrameOf) -> None:
    """Confere as respostas que já têm 5 pregões depois do padrão, de todos os jogadores."""
    frames: dict[str, pd.DataFrame | None] = {}
    for record in repository.candle_challenge.waiting(simulation_id):
        if record.ticker not in frames:
            frames[record.ticker] = frame_of(record.ticker)
        frame = frames[record.ticker]
        if frame is None:
            continue
        pos = _position(frame, record.pattern_date)
        if pos is None:
            continue
        day = _timestamp(frame, pos)
        pattern = Occurrence(record.pattern_code, day, day, pos)
        change = outcome(frame, pattern)
        if change is None:
            continue
        repository.candle_challenge.settle(
            record,
            _result(record.direction, change),
            _timestamp(frame, pos + OUTCOME_SESSIONS).date(),
        )


def ranking(simulation_ids: list[int]) -> CandleChallengeRankingDTO:
    """O placar da partida: mais acertos primeiro e, no empate, a maior taxa de acerto."""
    rows = sorted(
        repository.candle_challenge.ranking(simulation_ids),
        key=lambda row: (-row[1], -row[1] / row[2], row[0]),
    )
    return CandleChallengeRankingDTO(
        players=[
            ChallengeRankEntryDTO(
                position=position,
                player_nickname=nickname,
                hits=hits,
                answered=answered,
            )
            for position, (nickname, hits, answered) in enumerate(rows, start=1)
        ]
    )


def _result(direction: ChallengeDirection, change: float) -> ChallengeResult:
    hit = is_hit(direction, change)
    if hit is None:
        return "void"
    return "hit" if hit else "miss"


def _sided_ending_at(occurrences: list[Occurrence], pos: int) -> Occurrence | None:
    """O padrão que fecha na posição `pos`, quando sugere um lado: o doji não vira desafio."""
    return next(
        (
            o
            for o in occurrences
            if o.end_pos == pos and PATTERNS[o.code].direction != "neutral"
        ),
        None,
    )


def _answered(
    simulation_id: int, user_id: int, ticker: str, pattern: Occurrence
) -> bool:
    return (
        repository.candle_challenge.get(
            simulation_id, user_id, ticker, pattern.end.date()
        )
        is not None
    )


def _position(frame: pd.DataFrame, day: date) -> int | None:
    pos = int(frame.index.get_indexer([pd.Timestamp(day)])[0])
    return pos if pos >= 0 else None


def _timestamp(frame: pd.DataFrame, pos: int) -> pd.Timestamp:
    return cast(pd.Timestamp, frame.index[pos])


def _after_sessions(day: date, sessions: int) -> date:
    for _ in range(sessions):
        day = next_business_day(day)
    return day


def _answer_dto(
    record: ChallengeRecordDTO, frame: pd.DataFrame
) -> ChallengeAnswerDTO | None:
    pos = _position(frame, record.pattern_date)
    if pos is None:
        return None
    close = frame["close"]
    price = float(close.iloc[pos])
    after = len(frame) - 1 - pos
    stats = next(
        s for s in build_candle_patterns(frame).stats if s.code == record.pattern_code
    )
    if record.result is None or after < OUTCOME_SESSIONS:
        now = float(close.iloc[-1])
        return ChallengeAnswerDTO(
            pattern_code=record.pattern_code,
            pattern_date=record.pattern_date,
            status="waiting",
            direction=record.direction,
            price=price,
            settles_on=_after_sessions(record.pattern_date, OUTCOME_SESSIONS),
            sessions_left=max(OUTCOME_SESSIONS - after, 0),
            current_price=now,
            change=now / price - 1,
            stats=stats,
        )
    final = float(close.iloc[pos + OUTCOME_SESSIONS])
    return ChallengeAnswerDTO(
        pattern_code=record.pattern_code,
        pattern_date=record.pattern_date,
        status=record.result,
        direction=record.direction,
        price=price,
        settles_on=record.settled_on
        or _timestamp(frame, pos + OUTCOME_SESSIONS).date(),
        sessions_left=None,
        current_price=final,
        change=final / price - 1,
        stats=stats,
    )


def _expired_dto(pattern: Occurrence, frame: pd.DataFrame) -> ChallengeAnswerDTO:
    stats = next(
        s for s in build_candle_patterns(frame).stats if s.code == pattern.code
    )
    return ChallengeAnswerDTO(
        pattern_code=pattern.code,
        pattern_date=pattern.end.date(),
        status="expired",
        direction=None,
        price=float(frame["close"].iloc[pattern.end_pos]),
        settles_on=_after_sessions(pattern.end.date(), OUTCOME_SESSIONS),
        sessions_left=None,
        current_price=None,
        change=None,
        stats=stats,
    )
