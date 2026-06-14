import re
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationSummaryDTO
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.models.models import Simulations

_DEFAULT_NAME_PREFIX = "Simulação #"
_DEFAULT_NAME_PATTERN = re.compile(r"^Simulação #(\d+)$")


class SimulationRepository:
    @transactional
    def create_simulation(
        self, session: Session, settings: SimulationSettingsDTO
    ) -> int:
        now = datetime.now(UTC)
        simulation = Simulations(
            name=settings.name,
            start_date=settings.start_date,
            end_date=settings.end_date,
            starting_cash=Decimal(str(settings.starting_cash)),
            monthly_contribution=Decimal(str(settings.monthly_contribution)),
            created_at=now,
            last_simulated_at=now,
        )
        session.add(simulation)
        try:
            session.flush()
        except IntegrityError as exc:
            raise ConflictError(
                f"Já existe uma simulação com o nome '{settings.name}'."
            ) from exc
        return simulation.id

    @transactional
    def get_simulation(
        self, session: Session, simulation_id: int
    ) -> SimulationSummaryDTO | None:
        simulation = session.get(Simulations, simulation_id)
        if simulation is None:
            return None
        return self._to_summary(simulation)

    @transactional
    def list_simulations(
        self, session: Session, search: str | None = None
    ) -> list[SimulationSummaryDTO]:
        stmt = select(Simulations).order_by(Simulations.last_simulated_at.desc())
        if search:
            stmt = stmt.where(Simulations.name.ilike(f"%{search}%"))
        simulations = session.scalars(stmt).all()
        return [self._to_summary(s) for s in simulations]

    @transactional
    def get_last_simulated(self, session: Session) -> SimulationSummaryDTO | None:
        simulation = session.scalars(
            select(Simulations).order_by(Simulations.last_simulated_at.desc()).limit(1)
        ).first()
        if simulation is None:
            return None
        return self._to_summary(simulation)

    @transactional
    def touch_last_simulated(self, session: Session, simulation_id: int) -> None:
        session.execute(
            update(Simulations)
            .where(Simulations.id == simulation_id)
            .values(last_simulated_at=datetime.now(UTC))
        )

    @transactional
    def generate_default_name(self, session: Session) -> str:
        # Calcula o maior N entre os nomes no padrão "Simulação #N" e retorna N+1.
        names = session.scalars(
            select(Simulations.name).where(
                Simulations.name.op("~")(r"^Simulação #\d+$")
            )
        ).all()
        max_index = 0
        for name in names:
            match = _DEFAULT_NAME_PATTERN.match(name)
            if match:
                max_index = max(max_index, int(match.group(1)))
        return f"{_DEFAULT_NAME_PREFIX}{max_index + 1}"

    @transactional
    def rename(
        self, session: Session, simulation_id: int, name: str
    ) -> SimulationSummaryDTO:
        simulation = session.get(Simulations, simulation_id)
        if simulation is None:
            raise ConflictError("Simulação não encontrada.")
        simulation.name = name
        try:
            session.flush()
        except IntegrityError as exc:
            raise ConflictError(
                f"Já existe uma simulação com o nome '{name}'."
            ) from exc
        return self._to_summary(simulation)

    @staticmethod
    def _to_summary(simulation: Simulations) -> SimulationSummaryDTO:
        return SimulationSummaryDTO(
            id=simulation.id,
            name=simulation.name,
            start_date=simulation.start_date,
            end_date=simulation.end_date,
            starting_cash=float(simulation.starting_cash),
            monthly_contribution=float(simulation.monthly_contribution),
            created_at=simulation.created_at,
            last_simulated_at=simulation.last_simulated_at,
        )
