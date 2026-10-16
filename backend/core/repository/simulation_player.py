from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.user import UserDTO
from backend.core.models.models import SimulationPlayers, Users


class SimulationPlayerRepository:
    @transactional
    def save(self, session: Session, simulation_id: int, colors: dict[int, str]):
        """Grava a cor de cada jogador na partida; quem já tem linha troca de cor."""
        if not colors:
            return
        stmt = insert(SimulationPlayers).values(
            [
                {"simulation_id": simulation_id, "user_id": user_id, "color": color}
                for user_id, color in colors.items()
            ]
        )
        session.execute(
            stmt.on_conflict_do_update(
                index_elements=["simulation_id", "user_id"],
                set_={"color": stmt.excluded.color},
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
    def participants(self, session: Session, simulation_id: int) -> list[UserDTO]:
        users = (
            session.execute(
                select(Users)
                .join(SimulationPlayers, SimulationPlayers.user_id == Users.id)
                .where(SimulationPlayers.simulation_id == simulation_id)
            )
            .scalars()
            .all()
        )
        return [
            UserDTO(id=user.id, client_id=user.client_id, nickname=user.nickname)
            for user in users
        ]
