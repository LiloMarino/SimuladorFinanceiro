import random
import re
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.simulation import (
    SimulationResultDTO,
    SimulationSettingsDTO,
    SimulationSummaryDTO,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.models.models import (
    EconomicIndicatorHistory,
    SimulationPlayers,
    Simulations,
    StockPriceHistory,
    Users,
)

_DEFAULT_NAME_PREFIX = "Simulação #"
_DEFAULT_NAME_PATTERN = re.compile(r"^Simulação #(\d+)$")


def encode_rules(settings: SimulationSettingsDTO) -> dict[str, Any]:
    """As regras como `Simulations.rules` as guarda: as configurações sem o nome."""
    return settings.model_dump(mode="json", exclude={"name"})


def decode_settings(name: str, rules: dict[str, Any]) -> SimulationSettingsDTO:
    """As configurações da partida, lidas de `Simulations.rules`; é a única porta de leitura."""
    return SimulationSettingsDTO.model_validate({**rules, "name": name})


class SimulationRepository:
    @transactional
    def create_simulation(
        self,
        session: Session,
        settings: SimulationSettingsDTO,
        *,
        is_backtest: bool = False,
    ) -> int:
        now = datetime.now(UTC)
        simulation = Simulations(
            name=settings.name,
            rules=encode_rules(settings),
            random_seed=random.SystemRandom().randrange(2**31),
            is_backtest=is_backtest,
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
    def get_result(
        self, session: Session, simulation_id: int
    ) -> tuple[date | None, SimulationResultDTO] | None:
        """O ranking guardado e o último dia gravado que ele cobre; None se nunca foi calculado."""
        row = session.execute(
            select(Simulations.result_as_of, Simulations.result).where(
                Simulations.id == simulation_id
            )
        ).one_or_none()
        if row is None or row.result is None:
            return None
        return row.result_as_of, SimulationResultDTO.model_validate(row.result)

    @transactional
    def save_result(
        self,
        session: Session,
        simulation_id: int,
        as_of: date | None,
        result: SimulationResultDTO,
    ) -> None:
        session.execute(
            update(Simulations)
            .where(Simulations.id == simulation_id)
            .values(result=result.to_json(), result_as_of=as_of)
        )

    @transactional
    def get_last_simulated(self, session: Session) -> SimulationSummaryDTO | None:
        simulation = session.scalars(
            select(Simulations).order_by(Simulations.last_simulated_at.desc()).limit(1)
        ).first()
        if simulation is None:
            return None
        return self._to_summary(simulation)

    @transactional
    def get_random_seed(self, session: Session, simulation_id: int) -> int:
        return session.execute(
            select(Simulations.random_seed).where(Simulations.id == simulation_id)
        ).scalar_one()

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

    @transactional
    def delete(self, session: Session, simulation_id: int) -> bool:
        # Jogadores, eventos e snapshots saem em cascata pelas chaves estrangeiras;
        # a cópia congelada das séries (version = id da partida) não tem chave
        # estrangeira e sai na mesma transação.
        bot_ids = session.scalars(
            select(Users.id)
            .join(SimulationPlayers, SimulationPlayers.user_id == Users.id)
            .where(
                SimulationPlayers.simulation_id == simulation_id,
                Users.is_bot.is_(True),
            )
        ).all()
        session.execute(
            delete(EconomicIndicatorHistory).where(
                EconomicIndicatorHistory.version == simulation_id
            )
        )
        session.execute(
            delete(StockPriceHistory).where(StockPriceHistory.version == simulation_id)
        )
        deleted_id = session.scalar(
            delete(Simulations)
            .where(Simulations.id == simulation_id)
            .returning(Simulations.id)
        )
        # O bot é de uma partida só: sem ela, o usuário dele não serve a mais ninguém
        session.execute(
            delete(Users).where(
                Users.id.in_(bot_ids),
                ~select(SimulationPlayers.user_id)
                .where(SimulationPlayers.user_id == Users.id)
                .exists(),
            )
        )
        return deleted_id is not None

    @staticmethod
    def _to_summary(simulation: Simulations) -> SimulationSummaryDTO:
        return SimulationSummaryDTO(
            **decode_settings(simulation.name, simulation.rules).model_dump(),
            id=simulation.id,
            is_backtest=simulation.is_backtest,
            created_at=simulation.created_at,
            last_simulated_at=simulation.last_simulated_at,
        )
