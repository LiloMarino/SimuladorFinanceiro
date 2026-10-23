from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from backend.core.dto.events.strategy import StrategyEventDTO
from backend.core.enum import StrategyLogKind


@dataclass(frozen=True)
class ModeState:
    """O modo do jogador, derivado das linhas de modo do registro."""

    key: str | None = None
    params: dict | None = None
    # Dia em que ligou ou trocou para a estratégia em vigor
    since: date | None = None
    # O erro que devolveu ao manual; fica até o jogador ligar de novo
    error: StrategyEventDTO | None = None
    error_seen: bool = False
    # A última linha de modo é a retomada da partida
    resumed: bool = False


def derive_state(rows: list[StrategyEventDTO]) -> ModeState:
    """Percorre as linhas de modo na ordem em que aconteceram; a última manda."""
    state = ModeState()
    for row in rows:
        match row.kind:
            case StrategyLogKind.ENABLED | StrategyLogKind.SWITCHED:
                state = ModeState(row.strategy_key, row.params, row.event_date)
            case StrategyLogKind.PARAMS:
                state = ModeState(row.strategy_key, row.params, state.since)
            case StrategyLogKind.RESUMED:
                state = ModeState(state.key, state.params, state.since, resumed=True)
            case StrategyLogKind.DISABLED:
                state = ModeState()
            case StrategyLogKind.ERROR:
                state = ModeState(error=row)
            case StrategyLogKind.ERROR_SEEN:
                state = ModeState(error=state.error, error_seen=True)
            case StrategyLogKind.ORDER:
                continue
    return state
