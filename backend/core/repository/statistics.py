from collections import defaultdict

from sqlalchemy.orm import Session

from backend import config
from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.models.models import Snapshots, Users


class StatisticsRepository:
    @transactional
    def get_players_history(self, session: Session) -> list[PlayerHistoryDTO]:
        # 1. Busca todos os usuários
        users = session.query(Users).all()

        if not users:
            return []

        # 2. Busca todos os snapshots de todos os usuários, ordenados
        snapshots = (
            session.query(Snapshots)
            .order_by(Snapshots.user_id, Snapshots.snapshot_date)
            .all()
        )

        # 3. Agrupa snapshots por usuário
        snapshots_by_user: dict[int, list[Snapshots]] = defaultdict(list)
        for snap in snapshots:
            snapshots_by_user[snap.user_id].append(snap)

        # 4. Monta o DTO final
        players_history: list[PlayerHistoryDTO] = []
        for user in users:
            user_snaps = snapshots_by_user.get(user.id, [])

            if not user_snaps:
                continue

            history: list[PatrimonialHistoryDTO] = [
                PatrimonialHistoryDTO(
                    snapshot_date=s.snapshot_date,
                    total_equity=s.total_equity,
                    total_fixed=s.total_fixed,
                    total_cash=s.total_cash,
                    total_networth=s.total_networth,
                )
                for s in user_snaps
            ]

            last_snapshot = history[-1]
            players_history.append(
                PlayerHistoryDTO(
                    player_id=str(user.client_id),
                    player_nickname=user.nickname,
                    starting_cash=config.toml.simulation.starting_cash,
                    history=history,
                    last_snapshot=last_snapshot,
                )
            )

        return players_history
