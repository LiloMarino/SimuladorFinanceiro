"""O andamento de um backtest que roda: pontos do gráfico, falhas e a estimativa de tempo."""

import threading
import time
from datetime import date
from decimal import Decimal

from backend.core.dto.backtest import (
    BacktestFailureDTO,
    BacktestParticipantDTO,
    BacktestPointDTO,
    BacktestProgressDTO,
    BacktestProgressEventDTO,
    BacktestStatusDTO,
)
from backend.core.dto.snapshot import SnapshotDTO
from backend.features.backtest.reference import ReferenceWallet
from backend.features.realtime import notify

# O gráfico anda a cada tantos pregões
SAMPLE_EVERY = 20

# A estimativa de tempo aparece quando há pregões suficientes para a média valer:
# os primeiros carregam a preparação do motor e inflam a conta
MIN_DAYS_FOR_ESTIMATE = 20


class BacktestProgress:
    """
    A thread do loop escreve (`record_day`, `fail`, `publish`) e as rotas leem
    (`status`): o estado todo fica sob um lock só.

    Os participantes seguem a ordem do `user_id`, a mesma em que o motor lista os
    jogadores; o ponto do gráfico guarda o patrimônio nessa ordem.
    """

    def __init__(
        self,
        *,
        simulation_id: int,
        name: str,
        host_nickname: str,
        start_date: date,
        end_date: date,
        starting_cash: Decimal,
        total_days: int,
        participants: list[BacktestParticipantDTO],
        user_ids: list[int],
    ) -> None:
        self._lock = threading.Lock()
        self._simulation_id = simulation_id
        self._name = name
        self._host_nickname = host_nickname
        self._start_date = start_date
        self._end_date = end_date
        self._total_days = total_days
        self._participants = participants
        self._index_of = {user_id: i for i, user_id in enumerate(user_ids)}
        self._wallet = ReferenceWallet(starting_cash)
        self._started_at = time.monotonic()
        self._done_days = 0
        self._current_date: date | None = None
        self._points: list[BacktestPointDTO] = []
        self._failures: list[BacktestFailureDTO] = []
        # O que já saiu em evento: o próximo aviso leva só o que veio depois
        self._sent_points = 0
        self._sent_failures = 0

    def record_day(
        self, day: date, snapshots: list[SnapshotDTO], contribution: Decimal
    ) -> bool:
        """
        Registra o pregão. Devolve se é hora de gravar o lote e avisar a sala: o
        pregão é múltiplo de `SAMPLE_EVERY` ou o último do período.
        """
        reference = self._wallet.step(day, contribution)
        with self._lock:
            self._done_days += 1
            self._current_date = day
            due = (
                self._done_days % SAMPLE_EVERY == 0
                or self._done_days >= self._total_days
            )
            if due:
                equity = [Decimal(0)] * len(self._participants)
                for snapshot in snapshots:
                    equity[self._index_of[snapshot.user_id]] = snapshot.total_networth
                self._points.append(
                    BacktestPointDTO(
                        day=day,
                        equity=equity,
                        contributed=reference.contributed,
                        cdi=reference.cdi,
                        ibov=reference.ibov,
                    )
                )
        return due

    def fail(self, nickname: str, day: date, message: str) -> None:
        with self._lock:
            self._failures.append(
                BacktestFailureDTO(nickname=nickname, day=day, message=message)
            )

    def publish(self) -> None:
        """Avisa a sala do andamento, com os pontos e as falhas desde o último aviso."""
        with self._lock:
            event = BacktestProgressEventDTO(
                progress=self._progress(),
                points=self._points[self._sent_points :],
                failures=self._failures[self._sent_failures :],
            )
            self._sent_points = len(self._points)
            self._sent_failures = len(self._failures)
        notify("backtest_progress", event.to_json())

    def status(self) -> BacktestStatusDTO:
        with self._lock:
            return BacktestStatusDTO(
                progress=self._progress(),
                participants=self._participants,
                points=list(self._points),
                failures=list(self._failures),
            )

    def _progress(self) -> BacktestProgressDTO:
        elapsed = time.monotonic() - self._started_at
        left = (
            elapsed / self._done_days * (self._total_days - self._done_days)
            if self._done_days >= MIN_DAYS_FOR_ESTIMATE
            else None
        )
        return BacktestProgressDTO(
            simulation_id=self._simulation_id,
            name=self._name,
            host_nickname=self._host_nickname,
            start_date=self._start_date,
            end_date=self._end_date,
            total_days=self._total_days,
            done_days=self._done_days,
            current_date=self._current_date,
            seconds_left=left,
        )
