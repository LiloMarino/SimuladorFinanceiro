"""O que o livro-caixa e as negociações da cota dizem da gestora: oferta, taxas e movimentos.

Tudo aqui é função pura sobre listas de eventos, para ser lida sem banco.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import (
    FundBuybackDTO,
    FundIssuanceDTO,
    FundMovementDTO,
    FundMovementType,
    FundOfferSaleDTO,
)
from backend.core.enum import CashflowEventType, EquityEventType
from backend.core.utils import is_business_day, next_business_day, next_month_turn

MOVEMENTS_LIMIT = 30

# Meses entre duas cobranças de performance, contados da oferta
PERFORMANCE_PERIOD_MONTHS = 6

_FEE_MOVEMENTS: dict[CashflowEventType, FundMovementType] = {
    CashflowEventType.FUND_MANAGEMENT_FEE: "management_fee",
    CashflowEventType.FUND_PERFORMANCE_FEE: "performance_fee",
}


@dataclass(frozen=True)
class OfferTotals:
    """O que a oferta já vendeu: as cotas e o dinheiro que entrou na gestora."""

    sold: Decimal
    raised: Decimal


def one_year_before(day: date) -> date:
    try:
        return day.replace(year=day.year - 1)
    except ValueError:
        return day.replace(year=day.year - 1, day=28)


def first_business_day_on_or_after(day: date) -> date:
    return day if is_business_day(day) else next_business_day(day)


def next_performance_on(base: date) -> date:
    """O dia da próxima cobrança de performance: a virada do mês seis meses depois de `base`."""
    month_index = base.year * 12 + base.month - 1 + PERFORMANCE_PERIOD_MONTHS
    target = date(month_index // 12, month_index % 12 + 1, 1)
    return first_business_day_on_or_after(target)


def offer_totals(sales: Iterable[FundOfferSaleDTO]) -> OfferTotals:
    """O que as vendas gravadas da oferta somam: cotas vendidas e dinheiro recebido."""
    sold = raised = Decimal(0)
    for sale in sales:
        sold += sale.quotas
        raised += sale.quotas * sale.price
    return OfferTotals(sold=sold, raised=raised)


def fees_received(events: Iterable[CashflowEventDTO], after: date) -> Decimal:
    """As taxas que saíram da gestora para o gestor depois de `after`."""
    return sum(
        (
            event.amount
            for event in events
            if event.event_type in _FEE_MOVEMENTS and event.event_date > after
        ),
        Decimal(0),
    )


@dataclass(frozen=True)
class OfferFacts:
    """A oferta como a gestora a gravou, para virar movimentos."""

    listed_on: date
    # O preço e as cotas postas à venda na abertura
    price: Decimal | None
    offered: Decimal | None
    totals: OfferTotals
    # Nulo com a oferta aberta
    closed_on: date | None

    @property
    def in_progress(self) -> bool:
        return self.closed_on is None


def movements(
    *,
    cash_events: Iterable[CashflowEventDTO],
    contributed_stocks: Iterable[EquityEventDTO],
    manager_trades: Iterable[EquityEventDTO],
    offer: OfferFacts | None,
    issuances: Iterable[FundIssuanceDTO] = (),
    buybacks: Iterable[FundBuybackDTO] = (),
    today: date,
) -> list[FundMovementDTO]:
    """Os movimentos mais novos da gestora, do mais recente ao mais antigo."""
    found: list[FundMovementDTO] = []

    def add(
        day: date,
        kind: FundMovementType,
        *,
        quotas: Decimal | None = None,
        price: Decimal | None = None,
        amount: Decimal | None = None,
        ticker: str | None = None,
    ) -> None:
        found.append(
            FundMovementDTO(
                day=day,
                type=kind,
                quotas=quotas,
                price=price,
                amount=amount,
                ticker=ticker,
            )
        )

    for event in cash_events:
        if event.event_type is CashflowEventType.FUND_TRANSFER_IN:
            add(event.event_date, "contribution", amount=event.amount)
        elif event.event_type in _FEE_MOVEMENTS:
            add(
                event.event_date,
                _FEE_MOVEMENTS[event.event_type],
                amount=event.amount,
            )
    for event in contributed_stocks:
        if event.event_type is EquityEventType.TRANSFER_IN:
            add(
                event.event_date,
                "contribution",
                amount=event.price * event.quantity,
                ticker=event.ticker,
            )
    for trade in manager_trades:
        add(
            trade.event_date,
            "manager_buy"
            if trade.event_type is EquityEventType.BUY
            else "manager_sell",
            quotas=trade.quantity,
            price=trade.price,
            amount=trade.price * trade.quantity,
        )
    if offer is not None:
        add(offer.listed_on, "offer_opened", quotas=offer.offered, price=offer.price)
        if offer.closed_on is not None:
            sold = offer.totals.sold
            add(
                offer.closed_on,
                "offer_closed",
                quotas=sold,
                price=offer.totals.raised / sold if sold > 0 else None,
                amount=offer.totals.raised,
            )
        turn = next_month_turn(offer.listed_on)
        while turn <= today:
            add(turn, "report_published")
            turn = next_month_turn(turn)

    for issuance in issuances:
        add(
            issuance.announced_on,
            "issuance_opened",
            quotas=issuance.quotas,
            price=issuance.price,
        )
        if issuance.closed_on is not None:
            add(
                issuance.closed_on,
                "issuance_closed",
                quotas=issuance.sold,
                price=issuance.price,
                amount=issuance.sold * issuance.price,
            )
    for buyback in buybacks:
        add(
            buyback.announced_on,
            "buyback_opened",
            quotas=buyback.quantity,
            price=buyback.max_price,
        )

    found.sort(key=lambda movement: movement.day)
    return found[::-1][:MOVEMENTS_LIMIT]


def last_business_day_before(day: date) -> date:
    previous = day - timedelta(days=1)
    while not is_business_day(previous):
        previous -= timedelta(days=1)
    return previous
