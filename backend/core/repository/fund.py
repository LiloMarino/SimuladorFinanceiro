import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import FundDayDTO, FundDTO, FundOfferSaleDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    AssetOrigin,
    Currency,
    DataOrigin,
    EquityEventType,
)
from backend.core.models.models import (
    EventEquity,
    FundDays,
    FundOfferSales,
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
    "offer_quotas",
    "offer_price",
    "offer_closed_on",
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


def _equity_event(event: EventEquity, ticker: str) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=event.simulation_id,
        portfolio_id=event.portfolio_id,
        event_type=EquityEventType(event.event_type),
        ticker=ticker,
        quantity=event.quantity,
        price=event.price,
        event_date=event.event_date,
        created_at=event.created_at,
    )


def _letters_taken_by_asset(session: Session, ticker: str) -> bool:
    """Se as quatro letras do ticker já são de um ativo importado (PETR11 conflita com PETR4)."""
    return (
        session.execute(
            select(Stock.id)
            .where(
                Stock.ticker.startswith(ticker[:4], autoescape=True),
                Stock.asset_class != AssetClass.FUND.value,
            )
            .limit(1)
        ).first()
        is not None
    )


class FundRepository:
    @transactional
    def claim_stock(self, session: Session, ticker: str, name: str) -> StockDTO | None:
        """A linha de `stock` da cota de uma gestora.

        O ticker é global: a cota nasce com a primeira gestora e as demais partidas reusam a
        linha. Quatro letras de um ativo importado devolvem None.
        """
        if _letters_taken_by_asset(session, ticker):
            return None
        stock = session.execute(
            select(Stock).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        if stock is None:
            stock = Stock(
                ticker=ticker,
                name=name,
                asset_class=AssetClass.FUND.value,
                currency=Currency.BRL.value,
                origin=AssetOrigin.DOMESTIC.value,
            )
            session.add(stock)
            session.flush()
        return StockDTO.from_model(stock)

    @transactional
    def letters_taken_by_asset(self, session: Session, ticker: str) -> bool:
        """A conferência de `claim_stock` sem gravar: as quatro letras já são de um ativo importado."""
        return _letters_taken_by_asset(session, ticker)

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
    def record_offer_sale(
        self, session: Session, fund_id: int, sale: FundOfferSaleDTO
    ) -> None:
        """Grava uma venda da oferta pública no momento em que acontece."""
        session.add(FundOfferSales(fund_id=fund_id, **sale.model_dump()))

    @transactional
    def offer_sales(self, session: Session, fund_id: int) -> list[FundOfferSaleDTO]:
        """As vendas da oferta pública da gestora, na ordem em que aconteceram."""
        rows = session.execute(
            select(FundOfferSales)
            .where(FundOfferSales.fund_id == fund_id)
            .order_by(FundOfferSales.id)
        ).scalars()
        return [FundOfferSaleDTO.model_validate(row) for row in rows]

    @transactional
    def drop_offer_sales_from(self, session: Session, fund_id: int, day: date) -> None:
        """Apaga as vendas de `day` em diante: o dia refeito pela retomada recomeça limpo."""
        session.execute(
            delete(FundOfferSales).where(
                FundOfferSales.fund_id == fund_id, FundOfferSales.day >= day
            )
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

    @transactional
    def last_traded_close(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        """O fechamento do último pregão em que a cota negociou até `until`, ou None se nunca negociou."""
        return session.execute(
            select(StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock_id,
                StockPriceHistory.version == simulation_id,
                StockPriceHistory.price_date <= until,
                StockPriceHistory.volume > 0,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
        ).scalar_one_or_none()

    @transactional
    def quota_trades(
        self, session: Session, simulation_id: int, stock_id: int
    ) -> list[EquityEventDTO]:
        """As compras e vendas da cota em todas as carteiras da partida, na ordem em que aconteceram."""
        rows = session.execute(
            select(EventEquity, Stock.ticker)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.stock_id == stock_id,
                EventEquity.event_type.in_(
                    [EquityEventType.BUY.value, EquityEventType.SELL.value]
                ),
            )
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()
        return [_equity_event(event, ticker) for event, ticker in rows]

    @transactional
    def portfolio_equity_events(
        self, session: Session, simulation_id: int, portfolio_id: int
    ) -> list[EquityEventDTO]:
        """Os eventos de renda variável da carteira na partida, na ordem em que aconteceram."""
        rows = session.execute(
            select(EventEquity, Stock.ticker)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.portfolio_id == portfolio_id,
            )
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()
        return [_equity_event(event, ticker) for event, ticker in rows]
