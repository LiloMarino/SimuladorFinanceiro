import datetime
import decimal
import uuid

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Double,
    Enum,
    ForeignKeyConstraint,
    Identity,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FixedIncomeAsset(Base):
    __tablename__ = "fixed_income_asset"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="fixed_income_asset_pkey"),
        UniqueConstraint("asset_uuid", name="fixed_income_asset_uuid_key"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    asset_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    issuer: Mapped[str] = mapped_column(Text, nullable=False)
    investment_type: Mapped[str] = mapped_column(
        Enum("CDB", "LCI", "LCA", "TESOURO_DIRETO", name="investment_type"),
        nullable=False,
    )
    rate_type: Mapped[str] = mapped_column(
        Enum("SELIC", "IPCA", "CDI", "PREFIXADO", name="rate_type"), nullable=False
    )
    maturity_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    interest_rate: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))

    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="asset"
    )


class IpcaHistory(Base):
    __tablename__ = "ipca_history"
    __table_args__ = (PrimaryKeyConstraint("ref_month", name="ipca_history_pkey"),)

    ref_month: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    rate_value: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)


class SelicHistory(Base):
    __tablename__ = "selic_history"
    __table_args__ = (PrimaryKeyConstraint("rate_date", name="selic_history_pkey"),)

    rate_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    rate_value: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)


class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="stock_pkey"),
        UniqueConstraint("name", name="stock_name_key"),
        UniqueConstraint("ticker", name="stock_ticker_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    ticker: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="stock"
    )
    stock_price_history: Mapped[list["StockPriceHistory"]] = relationship(
        "StockPriceHistory", back_populates="stock"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("client_id", name="users_client_id_key"),
        UniqueConstraint("nickname", name="users_nickname_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    nickname: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    event_cashflow: Mapped[list["EventCashflow"]] = relationship(
        "EventCashflow", back_populates="user"
    )
    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="user"
    )
    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="user"
    )
    snapshots: Mapped[list["Snapshots"]] = relationship(
        "Snapshots", back_populates="user"
    )


class EventCashflow(Base):
    __tablename__ = "event_cashflow"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_cashflow_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_cashflow_pkey"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(
        Enum("DEPOSIT", "WITHDRAW", "DIVIDEND", name="cashflow_event_type"),
        nullable=False,
    )
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    user: Mapped["Users"] = relationship("Users", back_populates="event_cashflow")


class EventEquity(Base):
    __tablename__ = "event_equity"
    __table_args__ = (
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="event_equity_stock_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_equity_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_equity_pkey"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(
        Enum("BUY", "SELL", name="equity_event_type"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="event_equity")
    user: Mapped["Users"] = relationship("Users", back_populates="event_equity")


class EventFixedIncome(Base):
    __tablename__ = "event_fixed_income"
    __table_args__ = (
        ForeignKeyConstraint(
            ["asset_id"],
            ["fixed_income_asset.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="event_fixed_income_asset_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_fixed_income_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_fixed_income_pkey"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(
        Enum("BUY", "REDEEM", name="fixed_income_event_type"), nullable=False
    )
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    asset: Mapped["FixedIncomeAsset"] = relationship(
        "FixedIncomeAsset", back_populates="event_fixed_income"
    )
    user: Mapped["Users"] = relationship("Users", back_populates="event_fixed_income")


class Snapshots(Base):
    __tablename__ = "snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="snapshots_user_id_fkey",
        ),
        PrimaryKeyConstraint("user_id", "snapshot_date", name="snapshots_pkey"),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    total_equity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    total_fixed: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    total_cash: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    total_networth: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    user: Mapped["Users"] = relationship("Users", back_populates="snapshots")


class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="stock_price_history_stock_id_fkey",
        ),
        PrimaryKeyConstraint("stock_id", "price_date", name="stock_price_history_pkey"),
    )

    stock_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    open: Mapped[float] = mapped_column(Double(53), nullable=False)
    high: Mapped[float] = mapped_column(Double(53), nullable=False)
    low: Mapped[float] = mapped_column(Double(53), nullable=False)
    close: Mapped[float] = mapped_column(Double(53), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)

    stock: Mapped["Stock"] = relationship("Stock", back_populates="stock_price_history")
