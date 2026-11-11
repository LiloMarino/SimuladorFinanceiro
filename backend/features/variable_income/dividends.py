"""
Contas dos proventos sem banco: o rendimento por ação dos últimos 12 meses e a
divisão dos proventos recebidos por mês, por ano e por pagador.
"""

from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from datetime import date
from decimal import Decimal

from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.dividends import (
    AssetCorporateEventDTO,
    AssetCorporateEventsDTO,
    ClassAmountDTO,
    DividendBucketDTO,
    DividendPayerDTO,
    DividendPaymentDTO,
    PayerAmountDTO,
    PortfolioDividendsDTO,
)
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.enum import AssetClass, CorporateEventKind, EquityEventType
from backend.core.utils import ratio, subtract_months

TRAILING_MONTHS = 12


def scale_dividends(
    events: Iterable[CorporateEventDTO],
    tickers: dict[int, str],
    factor: Callable[[str, date], float],
) -> list[CorporateEventDTO]:
    """
    Os eventos com o provento na escala do preço da partida: cada dividendo e JCP vale o
    histórico vezes o fator da bolsa do dia da data ex, o mesmo que escala o preço do ativo.
    O desdobramento é uma razão e passa como veio.
    """
    return [
        event.model_copy(
            update={
                "value": event.value * factor(tickers[event.stock_id], event.ex_date)
            }
        )
        if event.kind is CorporateEventKind.DIVIDEND and event.stock_id in tickers
        else event
        for event in events
    ]


def trailing_per_share(
    events: Iterable[CorporateEventDTO], today: date
) -> dict[int, Decimal]:
    """
    O provento por ação de cada ativo nos 12 meses até `today` (a data ex em
    (hoje - 12 meses, hoje]), na unidade de hoje: o provento de antes de um
    desdobramento ou grupamento é dividido pela razão dos eventos que vieram depois
    dele. Um desdobramento na mesma data ex já está na unidade do provento.
    """
    start = subtract_months(today, TRAILING_MONTHS)
    window = [e for e in events if start < e.ex_date <= today]
    splits: dict[int, list[CorporateEventDTO]] = defaultdict(list)
    for event in window:
        if event.kind is CorporateEventKind.SPLIT:
            splits[event.stock_id].append(event)

    totals: dict[int, Decimal] = defaultdict(Decimal)
    for event in window:
        if event.kind is not CorporateEventKind.DIVIDEND:
            continue
        later_ratio = Decimal(1)
        for split in splits[event.stock_id]:
            if split.ex_date > event.ex_date:
                later_ratio *= Decimal(str(split.value))
        totals[event.stock_id] += Decimal(str(event.value)) / later_ratio
    return dict(totals)


def dividend_yield(
    per_share: Decimal, price: Decimal, asset_class: AssetClass
) -> Decimal | None:
    """Provento por ação de 12 meses ÷ preço de hoje; a cripto não paga, e preço zero não mede."""
    return _yield(per_share, price, asset_class)


def yield_on_cost(
    per_share: Decimal, avg_price: Decimal, asset_class: AssetClass
) -> Decimal | None:
    """O mesmo provento ÷ o preço médio do jogador."""
    return _yield(per_share, avg_price, asset_class)


def _yield(
    per_share: Decimal, price: Decimal, asset_class: AssetClass
) -> Decimal | None:
    if asset_class is AssetClass.CRYPTO or price <= 0:
        return None
    return per_share / price


def month_start(day: date) -> date:
    return day.replace(day=1)


def trailing_window_start(today: date) -> date:
    """O primeiro dia dos 12 meses-calendário que terminam no mês de `today`."""
    return subtract_months(month_start(today), TRAILING_MONTHS - 1)


def _bucket(period: date, payments: Sequence[DividendPaymentDTO]) -> DividendBucketDTO:
    by_class: dict[AssetClass, Decimal] = defaultdict(Decimal)
    by_payer: dict[str, PayerAmountDTO] = {}
    for payment in payments:
        by_class[payment.asset_class] += payment.amount
        payer = by_payer.get(payment.ticker)
        by_payer[payment.ticker] = PayerAmountDTO(
            ticker=payment.ticker,
            name=payment.name,
            asset_class=payment.asset_class,
            amount=(payer.amount if payer else Decimal(0)) + payment.amount,
        )
    return DividendBucketDTO(
        period=period,
        amount=sum(by_class.values(), Decimal(0)),
        by_class=[ClassAmountDTO(asset_class=c, amount=a) for c, a in by_class.items()],
        payers=sorted(by_payer.values(), key=lambda p: p.amount, reverse=True),
    )


def monthly_buckets(
    payments: Sequence[DividendPaymentDTO], today: date
) -> list[DividendBucketDTO]:
    """Os 12 meses-calendário até o de `today`, do mais antigo ao mais novo, com os meses sem provento zerados."""
    first = trailing_window_start(today)
    by_month: dict[date, list[DividendPaymentDTO]] = defaultdict(list)
    for payment in payments:
        if payment.event_date >= first:
            by_month[month_start(payment.event_date)].append(payment)
    months = [subtract_months(first, -i) for i in range(TRAILING_MONTHS)]
    return [_bucket(month, by_month[month]) for month in months]


def yearly_buckets(
    payments: Sequence[DividendPaymentDTO], today: date
) -> list[DividendBucketDTO]:
    """Um ano-calendário por barra, do primeiro provento ao ano de `today`; sem provento, só o ano de hoje."""
    by_year: dict[int, list[DividendPaymentDTO]] = defaultdict(list)
    for payment in payments:
        by_year[payment.event_date.year].append(payment)
    first_year = min(by_year, default=today.year)
    return [
        _bucket(date(year, 1, 1), by_year[year])
        for year in range(first_year, today.year + 1)
    ]


def top_payers(
    payments: Sequence[DividendPaymentDTO], today: date
) -> list[DividendPayerDTO]:
    """Quem pagou nos 12 meses-calendário até `today`, do que mais pagou ao que menos, com a parte de cada um."""
    first = trailing_window_start(today)
    bucket = _bucket(first, [p for p in payments if p.event_date >= first])
    return [
        DividendPayerDTO(**p.model_dump(), share=ratio(p.amount, bucket.amount))
        for p in bucket.payers
    ]


def build_portfolio_dividends(
    payments: Sequence[DividendPaymentDTO], today: date
) -> PortfolioDividendsDTO:
    """O card de proventos da Carteira a partir dos créditos de provento no caixa, em ordem de data."""
    first = trailing_window_start(today)
    total_12m = sum((p.amount for p in payments if p.event_date >= first), Decimal(0))
    paid = {p.asset_class for p in payments}
    return PortfolioDividendsDTO(
        total=sum((p.amount for p in payments), Decimal(0)),
        total_12m=total_12m,
        payments_count=len(payments),
        first_payment_date=payments[0].event_date if payments else None,
        average_per_month=total_12m / TRAILING_MONTHS,
        classes=[c for c in AssetClass if c in paid],
        monthly=monthly_buckets(payments, today),
        yearly=yearly_buckets(payments, today),
        payers=top_payers(payments, today),
    )


def _signed_quantity(event: EquityEventDTO) -> Decimal:
    return event.event_type.quantity_sign * event.quantity


def build_asset_events(
    *,
    ticker: str,
    asset_class: AssetClass,
    events: Sequence[CorporateEventDTO],
    equity_events: Sequence[EquityEventDTO],
    payments: Sequence[DividendPaymentDTO],
    match_start: date,
    per_share: Decimal,
    price: Decimal,
    avg_price: Decimal | None,
) -> AssetCorporateEventsDTO:
    """
    O histórico de proventos e desdobramentos do ativo, do mais recente ao mais antigo.
    As ações do jogador são as da abertura da data ex: os eventos corporativos do dia
    entram na abertura, antes de qualquer compra ou venda dele.
    """
    rows = []
    for event in events:
        ex_date = event.ex_date
        if ex_date <= match_start:
            rows.append(
                AssetCorporateEventDTO(
                    ex_date=ex_date,
                    kind=event.kind,
                    value=Decimal(str(event.value)),
                    before_match=True,
                    shares=None,
                    shares_after=None,
                    received=None,
                )
            )
            continue

        opening = sum(
            (_signed_quantity(e) for e in equity_events if e.event_date < ex_date),
            Decimal(0),
        )
        same_day = [
            e
            for e in equity_events
            if e.event_date == ex_date
            and e.event_type in (EquityEventType.SPLIT, EquityEventType.FRACTION_SELL)
        ]
        applied = sum((_signed_quantity(e) for e in same_day), Decimal(0))
        if event.kind is CorporateEventKind.SPLIT:
            fractions = [
                e.quantity * e.price
                for e in same_day
                if e.event_type is EquityEventType.FRACTION_SELL
            ]
            shares, shares_after = opening, opening + applied
            received = sum(fractions, Decimal(0)) if fractions else None
        else:
            # O dividendo vem depois do desdobramento da mesma data, na unidade nova
            shares, shares_after = opening + applied, None
            received = sum(
                (p.amount for p in payments if p.event_date == ex_date), Decimal(0)
            )
        rows.append(
            AssetCorporateEventDTO(
                ex_date=ex_date,
                kind=event.kind,
                value=Decimal(str(event.value)),
                before_match=False,
                shares=shares,
                shares_after=shares_after,
                received=received,
            )
        )

    return AssetCorporateEventsDTO(
        ticker=ticker,
        asset_class=asset_class,
        dividend_yield_12m=dividend_yield(per_share, price, asset_class),
        per_share_12m=per_share,
        yield_on_cost=None
        if avg_price is None
        else yield_on_cost(per_share, avg_price, asset_class),
        received_total=sum((p.amount for p in payments), Decimal(0)),
        payments_count=len(payments),
        match_start_date=match_start,
        events=rows,
    )
