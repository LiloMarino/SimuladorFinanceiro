"""A estatal na tela da ação: preço, valor justo, dividendos por ação, meses e quem tem as ações."""

from collections.abc import Callable
from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.state_company import (
    StateCompanyDetailDTO,
    StateCompanyDTO,
    StateCompanyHoldersDTO,
    StateCompanyMonthDetailDTO,
    StatePolicyPayoutDTO,
)
from backend.core.enum import (
    StateCompanyOrigin,
    StateCompanyStatus,
    StateMonthReason,
)
from backend.features.state_companies import payout, reference
from backend.features.state_companies.book import (
    MarketPrice,
    StateCompanyBook,
    government_shares,
)
from backend.features.state_companies.orders import StateOrder

SHARE_PLACES = Decimal("0.0001")
PRICE_PLACES = Decimal("0.01")


def _per_share(value: Decimal, shares: int) -> Decimal:
    return (value / shares).quantize(SHARE_PLACES)


def _month_row(
    book: StateCompanyBook,
    company: StateCompanyDTO,
    month: date,
    reason: StateMonthReason,
    price: float | None,
    *,
    fair_value: Decimal | None = None,
    profit: Decimal | None = None,
    treasury_dividend: Decimal | None = None,
) -> StateCompanyMonthDetailDTO:
    """O mês por ação; a política e o payout do mês só existem onde o lucro foi apurado."""
    settled = reason in (StateMonthReason.PAID, StateMonthReason.LOSS)
    order = book.orders(month).get(company.ticker, StateOrder())
    return StateCompanyMonthDetailDTO(
        month=month,
        reason=reason,
        price=None if price is None else Decimal(str(price)).quantize(PRICE_PLACES),
        fair_value=(
            None if fair_value is None else _per_share(fair_value, company.shares)
        ),
        profit=None if profit is None else _per_share(profit, company.shares),
        dividend=(
            None
            if treasury_dividend is None
            else _per_share(
                treasury_dividend / company.government_share, company.shares
            )
        ),
        dividend_policy=order.dividend_policy if settled else None,
        payout=payout.payout_ratio(order.dividend_policy) if settled else None,
    )


def _months(
    book: StateCompanyBook, company: StateCompanyDTO, simulation_id: int, today: date
) -> list[StateCompanyMonthDetailDTO]:
    """A fundação, cada mês fechado gravado e, na estatal vendida, o mês da venda."""
    if company.founded_on is None:
        return []
    closes = repository.fund.month_end_closes(simulation_id, company.stock_id, today)
    founded_month = company.founded_on.replace(day=1)
    rows = [
        _month_row(
            book,
            company,
            founded_month,
            book.month_reason(company, founded_month, None),
            closes.get(founded_month),
            fair_value=company.invested,
        )
    ]
    rows.extend(
        _month_row(
            book,
            company,
            stored.month,
            book.month_reason(company, stored.month, stored.profit),
            closes.get(stored.month),
            fair_value=stored.fair_value,
            profit=stored.profit,
            treasury_dividend=stored.treasury_dividend,
        )
        for stored in repository.state_company.months_of(company.id)
    )
    sold_month = book.privatized_month(company)
    if sold_month is not None and sold_month <= today.replace(day=1):
        rows.append(
            _month_row(
                book,
                company,
                sold_month,
                book.month_reason(company, sold_month, None),
                closes.get(sold_month),
            )
        )
    return rows


def _holders(
    company: StateCompanyDTO,
    simulation_id: int,
    today: date,
    portfolio_id: int | None,
    maker_stock: Decimal,
) -> StateCompanyHoldersDTO:
    """
    Quem tem as ações: o governo, o estoque do formador e as carteiras da partida
    separadas em quem vê, os outros jogadores, os bots e as gestoras.
    """
    players = bots = funds = you = Decimal(0)
    for held_by, is_bot, balance in repository.state_company.shares_by_portfolio(
        simulation_id, company.stock_id, today
    ):
        if held_by == portfolio_id:
            you += balance
        elif is_bot is None:
            funds += balance
        elif is_bot:
            bots += balance
        else:
            players += balance
    sold = company.status is StateCompanyStatus.PRIVATIZED
    return StateCompanyHoldersDTO(
        government=Decimal(0 if sold else government_shares(company)),
        maker=maker_stock,
        players=players,
        bots=bots,
        funds=funds,
        you=you,
    )


def build_detail(
    book: StateCompanyBook,
    ticker: str,
    *,
    simulation_id: int,
    today: date,
    market_price: MarketPrice,
    maker_stock: Callable[[str], Decimal],
    portfolio_id: int | None,
) -> StateCompanyDetailDTO | None:
    """O detalhe da estatal na tela da ação; None quando a ação não é de estatal da partida."""
    company = book.company(ticker)
    if company is None:
        return None
    founded = company.origin is StateCompanyOrigin.FOUNDED
    sold = company.status is StateCompanyStatus.PRIVATIZED
    months = _months(book, company, simulation_id, today) if founded else []
    policy = book.orders(today).get(ticker, StateOrder()).dividend_policy
    if founded:
        dividends = sum(
            (m.dividend for m in months if m.dividend is not None), Decimal(0)
        )
    else:
        dividends = book.imported_dividend_per_share_12m(company, today).quantize(
            SHARE_PLACES
        )
    price = market_price(ticker)
    return StateCompanyDetailDTO(
        ticker=ticker,
        origin=company.origin,
        status=company.status,
        founded_on=company.founded_on,
        size=company.size,
        government_share=Decimal(0) if sold else company.government_share,
        shares=company.shares,
        price=price,
        fair_value=(book.offer_price(company, today) if founded and not sold else None),
        dividends=dividends,
        dividend_policy=policy,
        policies=[
            StatePolicyPayoutDTO(dividend_policy=option, payout=ratio)
            for option, ratio in payout.PAYOUT.items()
        ],
        beta=Decimal(str(reference.MARKET_BETA)) if founded else None,
        months=months,
        holders=(
            _holders(company, simulation_id, today, portfolio_id, maker_stock(ticker))
            if founded
            else None
        ),
    )
