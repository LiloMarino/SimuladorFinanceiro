from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import case, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.enum import AssetClass, DataOrigin
from backend.core.models.models import (
    AchievementProgress,
    Achievements,
    EventEquity,
    EventFixedIncome,
    Segments,
    Simulations,
    Stock,
    StockPriceHistory,
)
from backend.core.repository.series_version import seen_by


@dataclass(frozen=True)
class UnlockRow:
    code: str
    simulation_id: int | None
    simulation_name: str | None
    unlocked_at: datetime
    game_date: date
    seen_at: datetime | None


class AchievementsRepository:
    @transactional
    def unlocked_codes(self, session: Session, user_id: int) -> set[str]:
        return set(
            session.scalars(
                select(Achievements.code).where(Achievements.user_id == user_id)
            )
        )

    @transactional
    def unlock(
        self,
        session: Session,
        user_id: int,
        codes: list[str],
        simulation_id: int,
        game_date: date,
    ) -> list[str]:
        """Grava as conquistas; devolve só as que não existiam, que são as que saíram agora."""
        if not codes:
            return []
        stmt = (
            insert(Achievements)
            .values(
                [
                    {
                        "user_id": user_id,
                        "code": code,
                        "simulation_id": simulation_id,
                        "unlocked_at": datetime.now(UTC),
                        "game_date": game_date,
                    }
                    for code in codes
                ]
            )
            .on_conflict_do_nothing(index_elements=["user_id", "code"])
            .returning(Achievements.code)
        )
        return list(session.scalars(stmt))

    @transactional
    def unlocks(self, session: Session, user_id: int) -> list[UnlockRow]:
        rows = session.execute(
            select(Achievements, Simulations.name)
            .outerjoin(Simulations, Simulations.id == Achievements.simulation_id)
            .where(Achievements.user_id == user_id)
        ).all()
        return [
            UnlockRow(
                code=a.code,
                simulation_id=a.simulation_id,
                simulation_name=name,
                unlocked_at=a.unlocked_at,
                game_date=a.game_date,
                seen_at=a.seen_at,
            )
            for a, name in rows
        ]

    @transactional
    def best_progress(self, session: Session, user_id: int) -> dict[str, Decimal]:
        rows = session.execute(
            select(AchievementProgress.code, AchievementProgress.best).where(
                AchievementProgress.user_id == user_id
            )
        ).all()
        return {code: best for code, best in rows}

    @transactional
    def save_progress(
        self, session: Session, user_id: int, values: dict[str, Decimal]
    ) -> None:
        """Guarda o valor de cada conquista; quem já tinha um melhor o mantém."""
        if not values:
            return
        stmt = insert(AchievementProgress).values(
            [
                {"user_id": user_id, "code": code, "best": best}
                for code, best in values.items()
            ]
        )
        session.execute(
            stmt.on_conflict_do_update(
                index_elements=["user_id", "code"],
                set_={
                    "best": func.greatest(AchievementProgress.best, stmt.excluded.best)
                },
            )
        )

    @transactional
    def mark_seen(self, session: Session, user_id: int) -> None:
        session.execute(
            update(Achievements)
            .where(Achievements.user_id == user_id, Achievements.seen_at.is_(None))
            .values(seen_at=datetime.now(UTC))
        )

    # --------------------------------------------------
    # Medidas sobre os eventos da partida, lidas pelas métricas
    # --------------------------------------------------

    @transactional
    def equity_orders(
        self, session: Session, simulation_id: int, user_id: int, event_type: str | None
    ) -> int:
        stmt = select(func.count()).where(
            EventEquity.simulation_id == simulation_id, EventEquity.user_id == user_id
        )
        if event_type is not None:
            stmt = stmt.where(EventEquity.event_type == event_type)
        return session.scalar(stmt) or 0

    @transactional
    def fixed_income_buys(
        self, session: Session, simulation_id: int, user_id: int
    ) -> int:
        return (
            session.scalar(
                select(func.count()).where(
                    EventFixedIncome.simulation_id == simulation_id,
                    EventFixedIncome.user_id == user_id,
                    EventFixedIncome.event_type == "BUY",
                )
            )
            or 0
        )

    @transactional
    def equity_order_dates(
        self, session: Session, simulation_id: int, user_id: int, event_type: str
    ) -> list[date]:
        """Dias das ordens de ações, do mais antigo ao mais novo."""
        return list(
            session.scalars(
                select(EventEquity.event_date)
                .where(
                    EventEquity.simulation_id == simulation_id,
                    EventEquity.user_id == user_id,
                    EventEquity.event_type == event_type,
                )
                .order_by(EventEquity.event_date)
            )
        )

    @transactional
    def held_assets(self, session: Session, simulation_id: int, user_id: int) -> int:
        """Ações e títulos de renda fixa com saldo positivo, somados."""
        stocks = session.scalars(_held_stock_ids(simulation_id, user_id)).all()

        signed_amount = case(
            (EventFixedIncome.event_type == "BUY", EventFixedIncome.amount),
            else_=-EventFixedIncome.amount,
        )
        titles = session.scalars(
            select(EventFixedIncome.asset_id)
            .where(
                EventFixedIncome.simulation_id == simulation_id,
                EventFixedIncome.user_id == user_id,
            )
            .group_by(EventFixedIncome.asset_id)
            .having(func.sum(signed_amount) > Decimal("0.01"))
        ).all()
        return len(stocks) + len(titles)

    @transactional
    def held_sectors(self, session: Session, simulation_id: int, user_id: int) -> int:
        """Setores distintos das ações com saldo positivo; ativo sem setor não conta."""
        return (
            session.scalar(
                select(func.count(func.distinct(Segments.sector_id)))
                .select_from(Stock)
                .join(Segments, Segments.id == Stock.segment_id)
                .where(Stock.id.in_(_held_stock_ids(simulation_id, user_id)))
            )
            or 0
        )

    @transactional
    def day_traded_assets(
        self, session: Session, simulation_id: int, user_id: int
    ) -> int:
        """Quantos pares (ativo, dia) tiveram compra e venda; a cripto não tem day trade."""
        bought = func.sum(case((EventEquity.event_type == "BUY", 1), else_=0))
        sold = func.sum(case((EventEquity.event_type == "SELL", 1), else_=0))
        pairs = (
            select(EventEquity.stock_id)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.user_id == user_id,
                Stock.asset_class != AssetClass.CRYPTO.value,
            )
            .group_by(EventEquity.stock_id, EventEquity.event_date)
            .having(bought > 0, sold > 0)
            .subquery()
        )
        return session.scalar(select(func.count()).select_from(pairs)) or 0

    @transactional
    def equity_flows(
        self, session: Session, simulation_id: int, user_id: int, since: date
    ) -> list[tuple[str, date, Decimal]]:
        """Quantidade líquida (compras - vendas) do jogador por ativo e dia, a partir de `since`."""
        net = func.sum(_signed_quantity())
        rows = session.execute(
            select(Stock.ticker, EventEquity.event_date, net)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.user_id == user_id,
                EventEquity.event_date >= since,
            )
            .group_by(Stock.ticker, EventEquity.event_date)
        ).all()
        return [(ticker, day, quantity) for ticker, day, quantity in rows if quantity]

    @transactional
    def real_market_end(self, session: Session, simulation_id: int) -> date | None:
        """O último pregão com dado real que a partida enxerga; None sem mercado real."""
        return session.scalar(
            select(func.max(StockPriceHistory.price_date)).where(
                StockPriceHistory.origin == DataOrigin.REAL.value,
                seen_by(StockPriceHistory, simulation_id),
            )
        )


def _signed_quantity():
    """Compra soma e venda subtrai, para o saldo de cada ativo."""
    return case(
        (EventEquity.event_type == "BUY", EventEquity.quantity),
        else_=-EventEquity.quantity,
    )


def _held_stock_ids(simulation_id: int, user_id: int):
    """Os ativos de renda variável com saldo positivo do jogador na partida."""
    return (
        select(EventEquity.stock_id)
        .where(
            EventEquity.simulation_id == simulation_id,
            EventEquity.user_id == user_id,
        )
        .group_by(EventEquity.stock_id)
        .having(func.sum(_signed_quantity()) > 0)
    )
