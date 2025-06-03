import datetime
import decimal
from typing import List, Optional

from sqlalchemy import (
    DECIMAL,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Ativos(Base):
    __tablename__ = "ativos"
    __table_args__ = (Index("ticker_UNIQUE", "ticker", unique=True),)

    ativos_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16))
    classe: Mapped[str] = mapped_column(Enum("acao", "fii", "etf", "bdr"))

    preco_historico: Mapped[List["PrecoHistorico"]] = relationship(
        "PrecoHistorico", back_populates="ativos"
    )


class PrecoHistorico(Base):
    __tablename__ = "preco_historico"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ativos_id"], ["ativos.ativos_id"], name="fk_preco_historico_ativos"
        ),
        Index("fk_preco_historico_ativos_idx", "ativos_id"),
    )

    ativos_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time: Mapped[datetime.datetime] = mapped_column(DateTime, primary_key=True)
    open: Mapped[decimal.Decimal] = mapped_column(DECIMAL(15, 6))
    high: Mapped[decimal.Decimal] = mapped_column(DECIMAL(15, 6))
    low: Mapped[decimal.Decimal] = mapped_column(DECIMAL(15, 6))
    close: Mapped[decimal.Decimal] = mapped_column(DECIMAL(15, 6))
    volume: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 2))
    openinterest: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(15, 6))

    ativos: Mapped["Ativos"] = relationship("Ativos", back_populates="preco_historico")
