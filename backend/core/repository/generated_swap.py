"""
Troca do dado gerado, dentro da sessão de quem grava.

A ordem é o contrato: primeiro cada partida salva que jogou os dias gerados
recebe a cópia deles (`freeze_generated`), depois o gerado da série comum sai
(`drop_generated`) e só então entra o dado novo. Tudo na mesma sessão, para que
uma falha no meio não deixe a base pela metade.
"""

from datetime import date

from sqlalchemy import (
    ColumnElement,
    Date,
    delete,
    func,
    literal,
    select,
    union_all,
    update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute, Session

from backend.core.dto.generated_future import ReplacedGeneratedDTO
from backend.core.enum import DataOrigin
from backend.core.models.models import (
    EconomicIndicatorHistory,
    EventCashflow,
    EventEquity,
    EventFixedIncome,
    GeneratedFuture,
    Simulations,
    Snapshots,
    StockPriceHistory,
)
from backend.core.repository.series_version import COMMON_VERSION, SeriesModel
from backend.core.repository.simulation import decode_settings


def _date_column(model: SeriesModel) -> InstrumentedAttribute[date]:
    if model is StockPriceHistory:
        return StockPriceHistory.price_date
    return EconomicIndicatorHistory.ref_date


def played_periods(session: Session) -> list[tuple[int, date, date]]:
    """Cada partida salva com o que ela jogou: do início ao último dia gravado."""
    recorded = union_all(
        *(
            select(model.simulation_id, model.event_date.label("day"))
            for model in (EventCashflow, EventEquity, EventFixedIncome)
        ),
        select(Snapshots.simulation_id, Snapshots.snapshot_date.label("day")),
    ).subquery()
    last_day = (
        select(recorded.c.simulation_id, func.max(recorded.c.day).label("day"))
        .group_by(recorded.c.simulation_id)
        .subquery()
    )
    rows = session.execute(
        select(
            Simulations.id, Simulations.name, Simulations.rules, last_day.c.day
        ).join(last_day, last_day.c.simulation_id == Simulations.id)
    ).all()
    periods = [
        (sim_id, decode_settings(name, rules).start_date, end)
        for sim_id, name, rules, end in rows
    ]
    return [(sim_id, start, end) for sim_id, start, end in periods if end >= start]


def _generated(
    model: SeriesModel, where: list[ColumnElement[bool]]
) -> list[ColumnElement[bool]]:
    return [
        model.version == COMMON_VERSION,
        model.origin == DataOrigin.GENERATED.value,
        *where,
    ]


def freeze_generated(
    session: Session,
    model: SeriesModel,
    where: list[ColumnElement[bool]],
    until: date | None = None,
) -> None:
    """
    Copia o gerado comum que cada partida salva jogou para a versão dela. Cópia
    que já existe fica: a partida continua vendo o que viu da primeira vez.
    """
    columns = [c.name for c in model.__table__.columns if c.name != "version"]
    day = _date_column(model)
    for simulation_id, start, end in played_periods(session):
        last = min(end, until) if until else end
        source = select(
            *(model.__table__.c[name] for name in columns),
            literal(simulation_id).label("version"),
        ).where(*_generated(model, where), day.between(start, last))
        session.execute(
            insert(model)
            .from_select([*columns, "version"], source)
            .on_conflict_do_nothing()
        )


def drop_generated(
    session: Session,
    model: SeriesModel,
    where: list[ColumnElement[bool]],
    until: date | None = None,
) -> ReplacedGeneratedDTO | None:
    """
    Apaga o gerado comum até `until` (todo, sem `until`). A faixa vai por data
    e não por dia a dia: o gerado tem os feriados, que o real não tem.
    """
    day = _date_column(model)
    condition = _generated(model, where)
    if until is not None:
        condition.append(day <= until)
    days, start, end = session.execute(
        select(func.count(), func.min(day), func.max(day)).where(*condition)
    ).one()
    if not days:
        return None
    session.execute(delete(model).where(*condition))
    return ReplacedGeneratedDTO(days=days, start=start, end=end)


def swap_generated_for_real(
    session: Session,
    model: SeriesModel,
    where: list[ColumnElement[bool]],
    real_end: date,
) -> ReplacedGeneratedDTO | None:
    """
    O real chegou até `real_end`: congela, apaga o gerado que ele cobre e marca
    no futuro gravado até onde o real avançou, para a Central sugerir gerar de novo.
    """
    freeze_generated(session, model, where, real_end)
    replaced = drop_generated(session, model, where, real_end)
    if replaced is not None:
        mark_real_advanced(session, real_end)
    return replaced


def mark_real_advanced(session: Session, real_end: date) -> None:
    """Guarda no futuro gravado até onde o real já ocupou o lugar do gerado."""
    real_end_value = literal(real_end, type_=Date)
    session.execute(
        update(GeneratedFuture).values(
            real_advanced_until=func.greatest(
                func.coalesce(GeneratedFuture.real_advanced_until, real_end_value),
                real_end_value,
            )
        )
    )
