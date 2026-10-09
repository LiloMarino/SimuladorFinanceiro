from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.player_history import PlayerHistoryDTO
from backend.core.models.models import Simulations, Snapshots, Users


class StatisticsRepository:
    @transactional
    def get_players_history(
        self, session: Session, simulation_ids: list[int]
    ) -> list[PlayerHistoryDTO]:
        # Capital inicial vem da linha da simulação (nunca do formulário),
        # garantindo métricas consistentes ao continuar/carregar simulações.
        rows = session.execute(
            select(Snapshots, Users.nickname, Simulations.name, Simulations.starting_cash)
            .join(Users, Users.id == Snapshots.user_id)
            .join(Simulations, Simulations.id == Snapshots.simulation_id)
            .where(Snapshots.simulation_id.in_(simulation_ids))
            .order_by(Snapshots.simulation_id, Snapshots.user_id, Snapshots.snapshot_date)
        ).all()

        # Agrupa os snapshots por jogador em cada simulação, preservando a ordem de data
        grouped: dict[tuple[int, int], list] = defaultdict(list)
        for row in rows:
            grouped[(row.Snapshots.simulation_id, row.Snapshots.user_id)].append(row)

        return [
            PlayerHistoryDTO(
                player_nickname=group[0].nickname,
                simulation_id=simulation_id,
                simulation_name=group[0].name,
                starting_cash=group[0].starting_cash,
                history=[
                    PatrimonialHistoryDTO(
                        snapshot_date=r.Snapshots.snapshot_date,
                        total_equity=r.Snapshots.total_equity,
                        total_fixed=r.Snapshots.total_fixed,
                        total_cash=r.Snapshots.total_cash,
                        total_networth=r.Snapshots.total_networth,
                        total_contribution=r.Snapshots.total_contribution,
                    )
                    for r in group
                ],
            )
            for (simulation_id, _), group in grouped.items()
        ]
