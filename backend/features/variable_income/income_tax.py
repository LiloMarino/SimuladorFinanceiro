"""Apuração mensal do IR sobre o ganho líquido na venda de renda variável.

Segue o motor fiscal do Finance Manager, com as regras do Perguntas e Respostas
IRPF da Receita:
- o ganho líquido é o resultado do conjunto das operações do mês;
- o day trade pareia a 1ª compra com a 1ª venda do mesmo ativo no dia e paga 20%;
  a operação comum paga 15%;
- o ganho comum com ações é isento quando as vendas de ações do mês somam até
  R$ 20.000,00; a isenção cobre só ação em operação comum;
- o ganho com cripto é isento quando as vendas de cripto do mês somam até
  R$ 35.000,00; cripto paga 15% e não tem day trade distinto: toda venda é comum;
- o prejuízo comum (ação, ETF e BDR) compensa ganho comum, o de day trade compensa
  day trade, o de FII compensa FII e o de cripto compensa cripto, no mês ou em
  qualquer mês seguinte;
- o FII paga 20%;
- o DARF vence no último dia útil do mês seguinte; imposto abaixo de R$ 10,00 soma
  ao do período seguinte.
"""

from __future__ import annotations

import calendar
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.enum import AssetClass, EquityEventType
from backend.core.utils import is_business_day
from backend.features.tax_policy import LossPool, PolicyOn, default_policy_on
from backend.features.variable_income.entities.position import Position

ZERO = Decimal(0)
CENT = Decimal("0.01")
DARF_MINIMUM = Decimal(10)


@dataclass(frozen=True, slots=True, kw_only=True)
class DayTrade:
    ticker: str
    trade_date: date
    cost: Decimal
    proceeds: Decimal

    @property
    def result(self) -> Decimal:
        return self.proceeds - self.cost


@dataclass(frozen=True, slots=True, kw_only=True)
class PoolResult:
    taxable: Decimal
    tax: Decimal
    loss_after: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class MonthlyTax:
    """A apuração de um mês. `tax` é o imposto do próprio mês, em centavos; o
    `darf_amount` soma a ele o que vinha carregado abaixo do mínimo, e só existe
    quando o total chega ao mínimo do DARF."""

    year: int
    month: int
    stock_sales: Decimal
    crypto_sales: Decimal
    exempt_profit: Decimal
    pools: Mapping[LossPool, PoolResult]
    tax: Decimal
    darf_amount: Decimal | None
    due_date: date | None


@dataclass(slots=True)
class _Category:
    result: Decimal = ZERO
    sales: Decimal = ZERO
    # Parte do resultado que vem de setor taxado, por pontos somados à alíquota
    taxed: defaultdict[Decimal, Decimal] = field(
        default_factory=lambda: defaultdict(Decimal)
    )


def _consume(
    legs: Sequence[tuple[int, EquityEventDTO]],
    quantity: Decimal,
    matched: dict[int, Decimal],
) -> Decimal:
    """Consome `quantity` das pernas pela ordem e devolve o valor financeiro delas."""
    value = ZERO
    for index, leg in legs:
        if quantity == 0:
            break
        taken = min(leg.quantity, quantity)
        matched[index] = taken
        value += taken * leg.price
        quantity -= taken
    return value


def settle_day_trades(
    events: Sequence[EquityEventDTO],
    without_day_trade: AbstractSet[str] = frozenset(),
) -> tuple[list[EquityEventDTO], list[DayTrade]]:
    """Separa o day trade do resto: devolve os eventos com a parte pareada
    descontada, na ordem recebida (cronológica), e os day trades de cada (ativo, dia).
    Os ativos de `without_day_trade` não pareiam: toda venda deles é operação comum."""
    by_day: defaultdict[tuple[str, date], list[tuple[int, EquityEventDTO]]]
    by_day = defaultdict(list)
    for index, event in enumerate(events):
        by_day[(event.ticker, event.event_date)].append((index, event))

    matched: dict[int, Decimal] = {}
    day_trades: list[DayTrade] = []
    for (ticker, trade_date), legs in by_day.items():
        if ticker in without_day_trade:
            continue
        buys = [leg for leg in legs if leg[1].event_type is EquityEventType.BUY]
        sells = [leg for leg in legs if leg[1].event_type is EquityEventType.SELL]
        quantity = min(
            sum((event.quantity for _, event in buys), ZERO),
            sum((event.quantity for _, event in sells), ZERO),
        )
        if quantity == 0:
            continue
        day_trades.append(
            DayTrade(
                ticker=ticker,
                trade_date=trade_date,
                cost=_consume(buys, quantity, matched),
                proceeds=_consume(sells, quantity, matched),
            )
        )

    settled = [
        event.model_copy(update={"quantity": event.quantity - matched.get(index, ZERO)})
        for index, event in enumerate(events)
        if matched.get(index, ZERO) != event.quantity
    ]
    return settled, day_trades


def _sales_results(
    settled: Iterable[EquityEventDTO],
) -> Iterator[tuple[EquityEventDTO, Decimal]]:
    """Cada venda assentada com o resultado dela sobre o preço médio fiscal, que
    só as sobras do day trade movem."""
    positions: dict[str, Position] = {}
    for event in settled:
        position = positions.setdefault(event.ticker, Position(event.ticker))
        if event.event_type is EquityEventType.BUY:
            position.update_buy(event.price, event.quantity)
            continue
        yield event, (event.price - position.avg_price) * event.quantity
        position.update_sell(event.quantity)


def _pool(asset_class: AssetClass, day_trade: bool) -> LossPool:
    if asset_class is AssetClass.FII:
        return LossPool.FII
    if asset_class is AssetClass.CRYPTO:
        return LossPool.CRYPTO
    if day_trade:
        return LossPool.DAY_TRADE
    return LossPool.COMMON


def _months(first: date, last: date) -> Iterator[tuple[int, int]]:
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def darf_due_date(year: int, month: int) -> date:
    """Último dia útil do mês seguinte ao da apuração, no calendário do tick."""
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    day = date(next_year, next_month, calendar.monthrange(next_year, next_month)[1])
    while not is_business_day(day):
        day -= timedelta(days=1)
    return day


def _surcharge(members: Sequence[_Category], taxable: Decimal, net: Decimal) -> Decimal:
    """Os pontos de setor taxado sobre o ganho dele, na mesma fração em que a
    compensação de prejuízo reduziu a base do conjunto."""
    if taxable <= ZERO:
        return ZERO
    by_extra: defaultdict[Decimal, Decimal] = defaultdict(Decimal)
    for item in members:
        for extra, result in item.taxed.items():
            by_extra[extra] += result
    return sum((max(gain, ZERO) * extra for extra, gain in by_extra.items()), ZERO) * (
        taxable / net
    )


def assess(
    events: Sequence[EquityEventDTO],
    asset_classes: Mapping[str, AssetClass],
    today: date,
    policy_on: PolicyOn = default_policy_on,
    classification: Mapping[str, StockSegmentDTO] | None = None,
) -> list[MonthlyTax]:
    """Todos os meses da primeira operação até o mês de `today`, com o prejuízo e o
    saldo abaixo do mínimo atravessando de um mês para o outro. `events` vem em
    ordem cronológica, como `get_equity_events` devolve.

    As alíquotas e o teto de isenção de cada mês são os vigentes no último dia dele (ou
    em `today`, no mês corrente); a regra de setor vale pelo dia de cada venda."""
    if not events:
        return []

    # Resultado de cada (mês, classe, day trade ou não)
    by_month: defaultdict[tuple[int, int], dict[tuple[AssetClass, bool], _Category]]
    by_month = defaultdict(dict)

    def category(day: date, ticker: str, day_trade: bool) -> _Category:
        key = (asset_classes[ticker], day_trade)
        return by_month[(day.year, day.month)].setdefault(key, _Category())

    def add(
        item: _Category, ticker: str, day: date, result: Decimal, sales: Decimal
    ) -> None:
        # A venda de setor isento conta no volume do mês e sai do ganho e do prejuízo
        item.sales += sales
        located = (classification or {}).get(ticker)
        rule = policy_on(day).sector_rule(
            located.sector if located else None, located.segment if located else None
        )
        if rule is not None and rule.exempt:
            return
        item.result += result
        if rule is not None and rule.extra:
            item.taxed[rule.extra] += result

    without_day_trade = {t for t, cls in asset_classes.items() if cls.fractional}
    settled, day_trades = settle_day_trades(events, without_day_trade)
    for sale, result in _sales_results(settled):
        item = category(sale.event_date, sale.ticker, day_trade=False)
        add(
            item,
            sale.ticker,
            sale.event_date,
            result,
            sale.price * sale.quantity,
        )
    for trade in day_trades:
        item = category(trade.trade_date, trade.ticker, day_trade=True)
        add(item, trade.ticker, trade.trade_date, trade.result, trade.proceeds)

    losses: dict[LossPool, Decimal] = dict.fromkeys(LossPool, ZERO)
    carried = ZERO
    months: list[MonthlyTax] = []

    for year, month in _months(events[0].event_date, today):
        raw = by_month.get((year, month), {})
        month_end = date(year, month, calendar.monthrange(year, month)[1])
        policy = policy_on(min(month_end, today))
        limits = policy.exemption_limits
        class_sales = {
            cls: sum(
                (item.sales for (c, _), item in raw.items() if c is cls),
                ZERO,
            )
            for cls in limits
        }

        # O ganho comum de cada classe com isenção sai da base quando as vendas
        # do mês dela ficam dentro do teto
        exempt_keys = {
            (cls, False)
            for cls, limit in limits.items()
            if (item := raw.get((cls, False))) is not None
            and item.result > ZERO
            and class_sales[cls] <= limit
        }
        exempt_profit = sum((raw[key].result for key in exempt_keys), ZERO)

        # Líquido de cada conjunto de compensação, abatido do prejuízo acumulado
        pools: dict[LossPool, PoolResult] = {}
        for pool in LossPool:
            members = [
                item
                for (cls, day_trade), item in raw.items()
                if _pool(cls, day_trade) is pool and (cls, day_trade) not in exempt_keys
            ]
            net = sum((item.result for item in members), ZERO)
            if net > ZERO:
                compensated = min(losses[pool], net)
                taxable = net - compensated
                losses[pool] -= compensated
            else:
                taxable = ZERO
                losses[pool] -= net
            pools[pool] = PoolResult(
                taxable=taxable,
                tax=taxable * policy.rates[pool] + _surcharge(members, taxable, net),
                loss_after=losses[pool],
            )

        tax = sum((p.tax for p in pools.values()), ZERO).quantize(CENT, ROUND_HALF_UP)
        due = carried + tax
        emits = due >= DARF_MINIMUM
        months.append(
            MonthlyTax(
                year=year,
                month=month,
                stock_sales=class_sales[AssetClass.STOCK],
                crypto_sales=class_sales[AssetClass.CRYPTO],
                exempt_profit=exempt_profit,
                pools=pools,
                tax=tax,
                darf_amount=due if emits else None,
                due_date=darf_due_date(year, month) if emits else None,
            )
        )
        carried = ZERO if emits else due

    return months
