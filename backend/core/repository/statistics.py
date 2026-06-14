from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.models.models import Simulations, Snapshots, Users
from backend.core.runtime.active_context import ActiveContext


class StatisticsRepository:
    @transactional
    def get_players_history(self, session: Session) -> list[PlayerHistoryDTO]:
        simulation_id = ActiveContext.get_active_simulation_id()

        # 0. Capital inicial vem da linha da simulação (nunca do formulário),
        # garantindo métricas consistentes ao continuar/carregar simulações.
        starting_cash = float(
            session.execute(
                select(Simulations.starting_cash).where(Simulations.id == simulation_id)
            ).scalar_one()
        )

        # 1. Busca todos os usuários
        users = session.query(Users).all()

        if not users:
            return []

        # 2. Busca os snapshots da simulação ativa, ordenados
        snapshots = (
            session.query(Snapshots)
            .where(Snapshots.simulation_id == simulation_id)
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
                    total_contribution=s.total_contribution,
                )
                for s in user_snaps
            ]

            players_history.append(
                PlayerHistoryDTO(
                    player_nickname=user.nickname,
                    starting_cash=starting_cash,
                    history=history,
                )
            )

        return players_history
