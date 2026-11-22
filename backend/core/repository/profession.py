import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.profession import (
    MechanicState,
    ProfessionPeriodDTO,
    initial_state,
    state_from_json,
)
from backend.core.enum import Profession
from backend.core.models.models import (
    ProfessionPeriods,
    ProfessionStates,
    SimulationPlayers,
)


def _upsert_state(
    session: Session, simulation_id: int, user_id: int, state: MechanicState
) -> None:
    values = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "state": state.to_json(),
    }
    statement = insert(ProfessionStates).values(values)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["simulation_id", "user_id"],
            set_={"state": statement.excluded.state},
        )
    )


def _upsert_period(
    session: Session,
    simulation_id: int,
    user_id: int,
    profession: Profession,
    start: datetime.date,
) -> None:
    values = {
        "simulation_id": simulation_id,
        "user_id": user_id,
        "start_date": start,
        "profession": profession.value,
    }
    statement = insert(ProfessionPeriods).values(values)
    session.execute(
        statement.on_conflict_do_update(
            index_elements=["simulation_id", "user_id", "start_date"],
            set_={"profession": statement.excluded.profession},
        )
    )


class ProfessionRepository:
    @transactional
    def open(
        self,
        session: Session,
        simulation_id: int,
        professions: dict[int, Profession],
        start: datetime.date,
    ) -> None:
        """
        Abre a profissão de quem entra na partida: o estado inicial e o primeiro período,
        desde `start`. Quem já tem estado e período os mantém.
        """
        for user_id, profession in professions.items():
            states = insert(ProfessionStates).values(
                simulation_id=simulation_id,
                user_id=user_id,
                state=initial_state(profession).to_json(),
            )
            session.execute(
                states.on_conflict_do_nothing(
                    index_elements=["simulation_id", "user_id"]
                )
            )
            periods = insert(ProfessionPeriods).values(
                simulation_id=simulation_id,
                user_id=user_id,
                start_date=start,
                profession=profession.value,
            )
            session.execute(
                periods.on_conflict_do_nothing(
                    index_elements=["simulation_id", "user_id", "start_date"]
                )
            )

    @transactional
    def states(self, session: Session, simulation_id: int) -> dict[int, MechanicState]:
        """O estado de cada jogador da partida, no tipo da profissão atual dele."""
        rows = session.execute(
            select(
                ProfessionStates.user_id,
                ProfessionStates.state,
                SimulationPlayers.profession,
            )
            .join(
                SimulationPlayers,
                (SimulationPlayers.simulation_id == ProfessionStates.simulation_id)
                & (SimulationPlayers.user_id == ProfessionStates.user_id),
            )
            .where(ProfessionStates.simulation_id == simulation_id)
        ).all()
        return {
            user_id: state_from_json(Profession(profession or Profession.CLT), data)
            for user_id, data, profession in rows
        }

    @transactional
    def save_state(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        state: MechanicState,
    ) -> None:
        _upsert_state(session, simulation_id, user_id, state)

    @transactional
    def periods(
        self, session: Session, simulation_id: int
    ) -> dict[int, list[ProfessionPeriodDTO]]:
        """Os períodos de profissão de cada jogador, do mais antigo ao mais novo."""
        rows = session.execute(
            select(
                ProfessionPeriods.user_id,
                ProfessionPeriods.profession,
                ProfessionPeriods.start_date,
            )
            .where(ProfessionPeriods.simulation_id == simulation_id)
            .order_by(ProfessionPeriods.user_id, ProfessionPeriods.start_date)
        ).all()
        periods: dict[int, list[ProfessionPeriodDTO]] = {}
        for user_id, profession, start in rows:
            periods.setdefault(user_id, []).append(
                ProfessionPeriodDTO(profession=Profession(profession), start=start)
            )
        return periods

    @transactional
    def switch(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        profession: Profession,
        day: datetime.date,
        state: MechanicState,
    ) -> None:
        """A troca no meio da partida, numa transação só: a profissão do jogador, o período que abre em `day` e o estado inicial da nova."""
        session.execute(
            update(SimulationPlayers)
            .where(
                SimulationPlayers.simulation_id == simulation_id,
                SimulationPlayers.user_id == user_id,
            )
            .values(profession=profession.value)
        )
        _upsert_period(session, simulation_id, user_id, profession, day)
        _upsert_state(session, simulation_id, user_id, state)
