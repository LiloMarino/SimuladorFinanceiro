"""O ticker global de um ativo criado na partida: a cota de uma gestora ou a ação de uma estatal fundada."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    AssetOrigin,
    Currency,
    StateCompanyOrigin,
)
from backend.core.models.models import StateCompanies, Stock


def letters_taken(session: Session, ticker: str, asset_class: AssetClass) -> bool:
    """Se as quatro letras do ticker já são de outro ativo (PETR11 conflita com PETR4).

    A cota convive com as de outras gestoras; a ação fundada reusa a linha do mesmo
    ticker que uma partida anterior fundou.
    """
    taken = select(Stock.id).where(Stock.ticker.startswith(ticker[:4], autoescape=True))
    if asset_class is AssetClass.FUND:
        taken = taken.where(Stock.asset_class != AssetClass.FUND.value)
    else:
        founded = select(StateCompanies.stock_id).where(
            StateCompanies.origin == StateCompanyOrigin.FOUNDED.value
        )
        taken = taken.where(~and_(Stock.ticker == ticker, Stock.id.in_(founded)))
    return session.execute(taken.limit(1)).first() is not None


def claim_stock(
    session: Session, ticker: str, name: str, asset_class: AssetClass
) -> StockDTO | None:
    """A linha de `stock` do ativo criado na partida; None quando as letras são de outro ativo.

    O ticker é global: nasce com a primeira partida que o usa e as demais reusam a linha.
    """
    if letters_taken(session, ticker, asset_class):
        return None
    stock = session.execute(
        select(Stock).where(Stock.ticker == ticker)
    ).scalar_one_or_none()
    if stock is None:
        stock = Stock(
            ticker=ticker,
            name=name,
            asset_class=asset_class.value,
            currency=Currency.BRL.value,
            origin=AssetOrigin.DOMESTIC.value,
        )
        session.add(stock)
        session.flush()
    return StockDTO.from_model(stock)
