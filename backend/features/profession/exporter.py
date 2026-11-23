"""
A mecânica do Exportador: a trava de câmbio e o mix de exportação, e o que a virada do
mês faz com a trava. Só funções do estado, do dia e da economia.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from backend.core.dto.profession import (
    ExchangeLock,
    ExporterAction,
    ExporterState,
    LockExchange,
    MechanicAction,
    MechanicState,
    SetExportMix,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.exporter import (
    BOT_DOLLAR_AVERAGE_MONTHS,
    BOT_MIX_BALANCED,
    BOT_MIX_DOLLAR_LEAN,
    BOT_MIX_GDP_LEAN,
    LOCK_TERMS_MONTHS,
    MAX_LOCK_SHARE,
    MIN_LOCK_SHARE,
    next_quarter_start,
)
from backend.core.professions import DRIVER_CURVES, IncomeDriver
from backend.features.economy.growth import MacroMonth


def next_mix_change(state: ExporterState) -> date | None:
    """O 1º dia do trimestre seguinte ao da última mudança do mix; nulo enquanto a primeira mudança ainda não aconteceu."""
    if state.mix_changed_on is None:
        return None
    return next_quarter_start(state.mix_changed_on)


def mix_change_allowed(state: ExporterState, day: date) -> bool:
    """O mix muda uma vez por trimestre do calendário; a primeira mudança é livre."""
    release = next_mix_change(state)
    return release is None or day >= release


def apply_exporter(
    state: MechanicState, action: MechanicAction, day: date, macro: MacroMonth
) -> ExporterState:
    """Contrata a trava ou muda o mix, recusando o que o estado ou o calendário não permitem."""
    state, action = cast(ExporterState, state), cast(ExporterAction, action)
    if isinstance(action, LockExchange):
        return lock_exchange(state, action, day)
    return set_export_mix(state, cast(SetExportMix, action), day)


def lock_exchange(
    state: ExporterState, action: LockExchange, day: date
) -> ExporterState:
    """Contrata a trava: uma por vez, para 1% a 100% da receita exportada, por 6 ou 12 meses."""
    if action.months not in LOCK_TERMS_MONTHS:
        raise ConflictError("O prazo da trava é de 6 ou 12 meses.")
    if not MIN_LOCK_SHARE <= action.share <= MAX_LOCK_SHARE:
        raise ConflictError("A trava cobre de 1% a 100% da receita exportada.")
    if state.lock is not None:
        raise ConflictError(
            "Já existe uma trava ativa: a próxima se contrata quando ela vencer."
        )
    return state.model_copy(
        update={
            "lock": ExchangeLock(
                share=action.share,
                months=action.months,
                locked_dollar=action.locked_dollar,
                contracted_on=day,
            )
        }
    )


def set_export_mix(
    state: ExporterState, action: SetExportMix, day: date
) -> ExporterState:
    """Muda a fração exportada, de 0% a 100%, no máximo uma vez por trimestre do calendário."""
    if not 0 <= action.share <= 1:
        raise ConflictError("A fração exportada vai de 0% a 100%.")
    if action.share == state.export_share:
        raise ConflictError("O mix já está nessa fração.")
    if not mix_change_allowed(state, day):
        release = cast(date, next_mix_change(state))
        raise ConflictError(
            f"O mix muda uma vez por trimestre: a próxima mudança é em {release:%d/%m/%Y}."
        )
    return state.model_copy(
        update={"export_share": action.share, "mix_changed_on": day}
    )


def after_payment(state: ExporterState, gain: Decimal) -> tuple[ExporterState, bool]:
    """
    O estado depois de um pagamento com a trava: soma o que ela rendeu no mês e conta o
    pagamento; no último a trava se encerra. Devolve também se ela se encerrou.
    """
    lock = state.lock
    if lock is None:
        return state, False
    paid = lock.paid_months + 1
    if paid >= lock.months:
        return state.model_copy(update={"lock": None}), True
    updated = lock.model_copy(update={"paid_months": paid, "gain": lock.gain + gain})
    return state.model_copy(update={"lock": updated}), False


def lock_wanted(
    state: ExporterState, dollar: Decimal, turn_dollars: list[Decimal]
) -> bool:
    """
    A política do bot trava quando não há trava e o dólar do dia está acima da média
    dos dólares de virada de mês dos últimos 12 meses; sem os 12, não trava.
    """
    if state.lock is not None or len(turn_dollars) < BOT_DOLLAR_AVERAGE_MONTHS:
        return False
    return dollar > sum(turn_dollars, Decimal(0)) / len(turn_dollars)


def mix_target(dollar_change: Decimal, growth: Decimal) -> Decimal:
    """
    A fração exportada da política do bot: 50/50, ou 70/30 quando só o dólar de 12
    meses está acima do neutro, ou 30/70 quando só o PIB de 12 meses está.
    """
    dollar_up = dollar_change > DRIVER_CURVES[IncomeDriver.DOLLAR].neutral
    growth_up = growth > DRIVER_CURVES[IncomeDriver.GDP].neutral
    if dollar_up and not growth_up:
        return BOT_MIX_DOLLAR_LEAN
    if growth_up and not dollar_up:
        return BOT_MIX_GDP_LEAN
    return BOT_MIX_BALANCED
