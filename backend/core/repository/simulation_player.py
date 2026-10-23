from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import SimulationPlayers, Users
from backend.core.repository.user import user_dto


class SimulationPlayerRepository:
    @transactional
    def save(
        self,
        session: Session,
        simulation_id: int,
        colors: dict[int, str],
        teams: dict[int, int] | None = None,
    ):
        """
        Grava a cor de cada jogador na partida; quem já tem linha troca de cor.
        `teams` (user_id -> equipe) só vem em partida em equipes e grava junto com a cor.
        """
        if not colors:
            return
        teams = teams or {}
        stmt = insert(SimulationPlayers).values(
            [
                {
                    "simulation_id": simulation_id,
                    "user_id": user_id,
                    "color": color,
                    "team": teams.get(user_id),
                }
                for user_id, color in colors.items()
            ]
        )
        session.execute(
            stmt.on_conflict_do_update(
                index_elements=["simulation_id", "user_id"],
                set_={"color": stmt.excluded.color, "team": stmt.excluded.team},
            )
        )

    @transactional
    def colors(self, session: Session, simulation_id: int) -> dict[int, str]:
        """Cor de cada participante da partida, por `user_id`."""
        rows = session.execute(
            select(SimulationPlayers.user_id, SimulationPlayers.color).where(
                SimulationPlayers.simulation_id == simulation_id
            )
        ).all()
        return {user_id: color for user_id, color in rows}

    @transactional
    def teams(self, session: Session, simulation_id: int) -> dict[int, int]:
        """Equipe de cada participante da partida, por `user_id`; vazio fora do modo em equipes."""
        rows = session.execute(
            select(SimulationPlayers.user_id, SimulationPlayers.team).where(
                SimulationPlayers.simulation_id == simulation_id,
                SimulationPlayers.team.is_not(None),
            )
        ).all()
        return {user_id: team for user_id, team in rows if team is not None}

    @transactional
    def participants(self, session: Session, simulation_id: int) -> list[UserDTO]:
        users = (
            session.execute(
                select(Users)
                .join(SimulationPlayers, SimulationPlayers.user_id == Users.id)
                .where(SimulationPlayers.simulation_id == simulation_id)
                .order_by(Users.id)
            )
            .scalars()
            .all()
        )
        return [user_dto(user) for user in users]

    @transactional
    def bots(
        self, session: Session, simulation_ids: list[int]
    ) -> list[tuple[int, UserDTO]]:
        """Os bots das partidas, como (simulation_id, usuário)."""
        rows = session.execute(
            select(SimulationPlayers.simulation_id, Users)
            .join(Users, Users.id == SimulationPlayers.user_id)
            .where(
                SimulationPlayers.simulation_id.in_(simulation_ids),
                Users.is_bot.is_(True),
            )
            .order_by(SimulationPlayers.simulation_id, Users.id)
        ).all()
        return [(simulation_id, user_dto(user)) for simulation_id, user in rows]
