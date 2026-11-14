import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fund import FundDayDTO, FundDTO
from backend.core.enum import DataOrigin
from backend.core.models.models import (
    FundDays,
    Funds,
    Portfolios,
    Stock,
    StockPriceHistory,
)

# Colunas da linha de `funds` que mudam depois de a gestora nascer
_MUTABLE = (
    "quotas",
    "maker_quotas",
    "maker_cash",
    "offer_remaining",
    "listed_on",
    "management_fee",
    "performance_fee",
    "pending_management_fee",
    "pending_performance_fee",
    "pending_from",
    "high_water_mark",
    "high_water_mark_on",
    "last_performance_on",
)


def _to_dto(fund: Funds, ticker: str) -> FundDTO:
    return FundDTO(ticker=ticker, **{k: getattr(fund, k) for k in _columns()})


def _columns() -> list[str]:
    return [
        "id",
        "stock_id",
        "portfolio_id",
        "client_id",
        "founder_user_id",
        "manager_user_id",
        "name",
        *_MUTABLE,
    ]


class FundRepository:
    @transactional
    def create(
        self,
        session: Session,
        *,
        simulation_id: int,
        stock_id: int,
        ticker: str,
        client_id: uuid.UUID,
        founder_user_id: int,
        manager_user_id: int,
        name: str,
        management_fee: Decimal,
        performance_fee: Decimal,
    ) -> FundDTO:
        """Abre a carteira da gestora (sem jogador dono) e grava a gestora com zero cota."""
        now = datetime.now(UTC)
        portfolio = Portfolios(
            simulation_id=simulation_id,
            user_id=None,
            created_at=now,
            starting_cash=Decimal(0),
        )
        session.add(portfolio)
        session.flush()
        fund = Funds(
            simulation_id=simulation_id,
            stock_id=stock_id,
            portfolio_id=portfolio.id,
            client_id=client_id,
            founder_user_id=founder_user_id,
            manager_user_id=manager_user_id,
            name=name,
            management_fee=management_fee,
            performance_fee=performance_fee,
            created_at=now,
        )
        session.add(fund)
        session.flush()
        return _to_dto(fund, ticker)

    @transactional
    def of_simulation(self, session: Session, simulation_id: int) -> list[FundDTO]:
        """As gestoras da partida, em ordem de criação."""
        rows = session.execute(
            select(Funds, Stock.ticker)
            .join(Stock, Stock.id == Funds.stock_id)
            .where(Funds.simulation_id == simulation_id)
            .order_by(Funds.id)
        ).all()
        return [_to_dto(fund, ticker) for fund, ticker in rows]

    @transactional
    def save(self, session: Session, fund: FundDTO) -> None:
        """Grava as colunas que mudam: cotas, formador, oferta, taxas e marca d'água."""
        session.execute(
            update(Funds)
            .where(Funds.id == fund.id)
            .values({column: getattr(fund, column) for column in _MUTABLE})
        )

    @transactional
    def save_day(self, session: Session, fund_id: int, day: FundDayDTO) -> None:
        """Grava o fechamento do pregão; refazer o dia troca a linha."""
        values = {"fund_id": fund_id, **day.model_dump()}
        session.execute(
            insert(FundDays)
            .values(values)
            .on_conflict_do_update(
                index_elements=["fund_id", "day"],
                set_={k: v for k, v in values.items() if k not in ("fund_id", "day")},
            )
        )

    @transactional
    def days(
        self, session: Session, fund_id: int, before: date, limit: int
    ) -> list[FundDayDTO]:
        """Os últimos `limit` fechamentos antes de `before`, do mais antigo ao mais recente."""
        rows = session.execute(
            select(FundDays)
            .where(FundDays.fund_id == fund_id, FundDays.day < before)
            .order_by(FundDays.day.desc())
            .limit(limit)
        ).scalars()
        return [FundDayDTO.model_validate(row) for row in reversed(list(rows))]

    @transactional
    def drop_days_from(self, session: Session, fund_id: int, day: date) -> None:
        """Apaga os fechamentos de `day` em diante: o dia refeito pela retomada recomeça limpo."""
        session.execute(
            delete(FundDays).where(FundDays.fund_id == fund_id, FundDays.day >= day)
        )

    @transactional
    def save_candle(
        self, session: Session, simulation_id: int, candle: CandleDTO
    ) -> None:
        """A vela da cota na série da própria partida: só ela enxerga esse preço."""
        values = {
            "stock_id": candle.id,
            "price_date": candle.price_date,
            "version": simulation_id,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
            "origin": DataOrigin.GENERATED.value,
        }
        session.execute(
            insert(StockPriceHistory)
            .values(values)
            .on_conflict_do_update(
                index_elements=["stock_id", "price_date", "version"],
                set_={
                    k: v
                    for k, v in values.items()
                    if k not in ("stock_id", "price_date", "version")
                },
            )
        )

    @transactional
    def last_close(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        """O último fechamento da cota na série da partida até `until`, ou None sem vela."""
        return session.execute(
            select(StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock_id,
                StockPriceHistory.version == simulation_id,
                StockPriceHistory.price_date <= until,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
        ).scalar_one_or_none()
