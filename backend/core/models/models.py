import datetime
import decimal
from typing import List

from sqlalchemy import (
    BigInteger,
    DateTime,
    Double,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Ativos(Base):
    __tablename__ = "ativos"
    __table_args__ = (Index("ticker_UNIQUE", "ticker", unique=True),)

    ativos_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16))
    nome: Mapped[str] = mapped_column(String(50))

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
    open: Mapped[float] = mapped_column(Double())
    high: Mapped[float] = mapped_column(Double())
    low: Mapped[float] = mapped_column(Double())
    close: Mapped[float] = mapped_column(Double())
    volume: Mapped[int] = mapped_column(BigInteger)

    ativos: Mapped["Ativos"] = relationship("Ativos", back_populates="preco_historico")
