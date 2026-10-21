import random
import re
from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.simulation import SimulationSettingsDTO, SimulationSummaryDTO
from backend.core.enum import GameType, PlayerGrouping, TeamNaming, VictoryCriterion
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.models.models import (
    EconomicIndicatorHistory,
    Simulations,
    StockPriceHistory,
)

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
            starting_cash=settings.starting_cash,
            monthly_contribution=settings.monthly_contribution,
            price_impact_enabled=settings.price_impact_enabled,
            price_impact_k=settings.price_impact_k,
            price_impact_decay_days=settings.price_impact_decay_days,
            victory_criterion=settings.victory_criterion.value,
            game_type=settings.game_type.value,
            goal_net_worth=settings.goal_net_worth,
            monthly_salary=settings.monthly_salary,
            monthly_expense=settings.monthly_expense,
            unexpected_per_year=settings.unexpected_per_year,
            withdrawal_rate=settings.withdrawal_rate,
            inflation_adjusted=settings.inflation_adjusted,
            # Os imprevistos saem dela: fica no servidor, fora das configurações
            random_seed=random.SystemRandom().randrange(2**31),
            player_grouping=settings.player_grouping.value,
            team_naming=settings.team_naming.value,
            show_equivalent_rate=settings.show_equivalent_rate,
            show_maturity_projection=settings.show_maturity_projection,
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
        return deleted_id is not None

    @staticmethod
    def _to_summary(simulation: Simulations) -> SimulationSummaryDTO:
        return SimulationSummaryDTO(
            id=simulation.id,
            name=simulation.name,
            start_date=simulation.start_date,
            end_date=simulation.end_date,
            starting_cash=simulation.starting_cash,
            monthly_contribution=simulation.monthly_contribution,
            price_impact_enabled=simulation.price_impact_enabled,
            price_impact_k=simulation.price_impact_k,
            price_impact_decay_days=simulation.price_impact_decay_days,
            victory_criterion=VictoryCriterion(simulation.victory_criterion),
            game_type=GameType(simulation.game_type),
            goal_net_worth=simulation.goal_net_worth,
            monthly_salary=simulation.monthly_salary,
            monthly_expense=simulation.monthly_expense,
            unexpected_per_year=simulation.unexpected_per_year,
            withdrawal_rate=simulation.withdrawal_rate,
            inflation_adjusted=simulation.inflation_adjusted,
            player_grouping=PlayerGrouping(simulation.player_grouping),
            team_naming=TeamNaming(simulation.team_naming),
            show_equivalent_rate=simulation.show_equivalent_rate,
            show_maturity_projection=simulation.show_maturity_projection,
            created_at=simulation.created_at,
            last_simulated_at=simulation.last_simulated_at,
        )
