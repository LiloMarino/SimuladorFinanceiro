"""O livro-caixa da gestora lido sem banco: oferta, taxas recebidas, compradores e movimentos."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import FundOfferSaleDTO
from backend.core.enum import CashflowEventType, EquityEventType
from backend.features.funds import fund_ledger
from backend.features.funds.fund_ledger import OfferFacts, OfferTotals

FUND_PORTFOLIO = 7
MANAGER_PORTFOLIO = 1
D1 = date(2004, 3, 1)
D2 = date(2004, 3, 2)
D3 = date(2004, 3, 3)


def cash(kind: CashflowEventType, day: date, amount: str) -> CashflowEventDTO:
    return CashflowEventDTO(
        simulation_id=1,
        portfolio_id=FUND_PORTFOLIO,
        event_type=kind,
        event_date=day,
        amount=Decimal(amount),
    )


def equity(
    kind: EquityEventType,
    day: date,
    quantity: str,
    price: str,
    *,
    portfolio: int = MANAGER_PORTFOLIO,
    ticker: str = "AURA11",
) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=1,
        portfolio_id=portfolio,
        event_type=kind,
        event_date=day,
        ticker=ticker,
        quantity=Decimal(quantity),
        price=Decimal(price),
    )


def proceeds(day: date, amount: str) -> CashflowEventDTO:
    return cash(CashflowEventType.FUND_OFFER_PROCEEDS, day, amount)


def test_one_year_before_handles_the_leap_day():
    assert fund_ledger.one_year_before(date(2005, 3, 1)) == date(2004, 3, 1)
    assert fund_ledger.one_year_before(date(2004, 2, 29)) == date(2003, 2, 28)


def test_next_performance_is_the_month_turn_six_months_after_the_base():
    # 6 meses depois de 15/03 é setembro; 01/09/2004 é quarta
    assert fund_ledger.next_performance_on(date(2004, 3, 15)) == date(2004, 9, 1)
    # 01/05/2004 foi sábado: a cobrança cai na segunda, 03/05
    assert fund_ledger.next_performance_on(date(2003, 11, 10)) == date(2004, 5, 3)
    # Virada de ano
    assert fund_ledger.next_performance_on(date(2004, 8, 20)) == date(2005, 2, 1)


def sale(day: date, quotas: str, price: str) -> FundOfferSaleDTO:
    return FundOfferSaleDTO(
        day=day, buyer_user_id=2, quotas=Decimal(quotas), price=Decimal(price)
    )


def test_offer_totals_sum_the_quotas_and_the_money_of_each_stored_sale():
    totals = fund_ledger.offer_totals(
        [sale(D1, "5", "100"), sale(D1, "3", "100"), sale(D2, "2", "101")]
    )

    assert totals == OfferTotals(sold=Decimal(10), raised=Decimal(1002))


def test_offer_totals_without_sales_are_empty():
    totals = fund_ledger.offer_totals([])

    assert totals == OfferTotals(sold=Decimal(0), raised=Decimal(0))


def test_fees_received_counts_only_fees_after_the_cutoff():
    events = [
        cash(CashflowEventType.FUND_MANAGEMENT_FEE, D1, "10"),
        cash(CashflowEventType.FUND_MANAGEMENT_FEE, D3, "12"),
        cash(CashflowEventType.FUND_PERFORMANCE_FEE, D3, "30"),
        proceeds(D3, "1000"),
    ]

    assert fund_ledger.fees_received(events, D2) == Decimal(42)
    assert fund_ledger.fees_received(events, D3) == Decimal(0)


def offer(
    *, closed_on: date | None, sold: str = "10", raised: str = "1000"
) -> OfferFacts:
    return OfferFacts(
        listed_on=D1,
        price=Decimal(100),
        offered=Decimal(20),
        totals=OfferTotals(Decimal(sold), Decimal(raised)),
        closed_on=closed_on,
    )


def kinds(found) -> list[str]:
    return [m.type for m in found]


def test_movements_come_newest_first_with_the_kind_of_each_event():
    found = fund_ledger.movements(
        cash_events=[
            cash(CashflowEventType.FUND_TRANSFER_IN, D1, "5000"),
            cash(CashflowEventType.FUND_MANAGEMENT_FEE, D3, "8"),
            cash(CashflowEventType.FUND_PERFORMANCE_FEE, D3, "20"),
            proceeds(D2, "500"),
        ],
        contributed_stocks=[
            equity(
                EquityEventType.TRANSFER_IN,
                D1,
                "10",
                "30",
                portfolio=FUND_PORTFOLIO,
                ticker="PETR4",
            )
        ],
        manager_trades=[equity(EquityEventType.SELL, D2, "4", "110")],
        offer=None,
        today=D3,
    )

    assert [(m.day, m.type) for m in found] == [
        (D3, "performance_fee"),
        (D3, "management_fee"),
        (D2, "manager_sell"),
        (D1, "contribution"),
        (D1, "contribution"),
    ]
    sell = next(m for m in found if m.type == "manager_sell")
    assert (sell.quotas, sell.price, sell.amount) == (
        Decimal(4),
        Decimal(110),
        Decimal(440),
    )
    stock = next(m for m in found if m.ticker == "PETR4")
    assert (stock.type, stock.amount) == ("contribution", Decimal(300))


def test_movements_of_an_offer_in_progress_have_no_closing():
    found = fund_ledger.movements(
        cash_events=[],
        contributed_stocks=[],
        manager_trades=[],
        offer=offer(closed_on=None),
        today=D2,
    )

    assert kinds(found) == ["offer_opened"]
    assert found[0].quotas == Decimal(20)
    assert found[0].price == Decimal(100)


def test_movements_of_a_closed_offer_close_on_the_stored_day_with_the_asked_size():
    found = fund_ledger.movements(
        cash_events=[],
        contributed_stocks=[],
        manager_trades=[],
        offer=offer(closed_on=D2),
        today=date(2004, 3, 9),
    )

    opened = next(m for m in found if m.type == "offer_opened")
    closed = next(m for m in found if m.type == "offer_closed")
    assert opened.quotas == Decimal(20)
    assert closed.day == D2
    assert (closed.quotas, closed.amount, closed.price) == (
        Decimal(10),
        Decimal(1000),
        Decimal(100),
    )


def test_a_closed_offer_without_sales_has_no_price_of_sale():
    found = fund_ledger.movements(
        cash_events=[],
        contributed_stocks=[],
        manager_trades=[],
        offer=offer(closed_on=D3, sold="0", raised="0"),
        today=D3,
    )

    closed = next(m for m in found if m.type == "offer_closed")
    assert (closed.quotas, closed.amount, closed.price) == (0, 0, None)


def test_a_report_is_published_at_each_month_turn_after_the_offer():
    found = fund_ledger.movements(
        cash_events=[],
        contributed_stocks=[],
        manager_trades=[],
        offer=offer(closed_on=None),
        today=date(2004, 6, 15),
    )

    reports = [m.day for m in found if m.type == "report_published"]
    assert reports == [date(2004, 6, 1), date(2004, 5, 3), date(2004, 4, 1)]


def test_movements_are_cut_to_the_limit():
    many = [
        cash(CashflowEventType.FUND_TRANSFER_IN, date(2004, 3, 1 + i % 28), "1")
        for i in range(fund_ledger.MOVEMENTS_LIMIT + 10)
    ]

    found = fund_ledger.movements(
        cash_events=many,
        contributed_stocks=[],
        manager_trades=[],
        offer=None,
        today=date(2004, 4, 1),
    )

    assert len(found) == fund_ledger.MOVEMENTS_LIMIT
    assert found[0].day >= found[-1].day


def test_last_business_day_before_skips_the_weekend():
    # 03/05/2004 é segunda: o pregão anterior é a sexta, 30/04
    assert fund_ledger.last_business_day_before(date(2004, 5, 3)) == date(2004, 4, 30)
