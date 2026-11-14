import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fund import FundDayDTO, FundDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import AssetClass, IndicatorSeries
from backend.core.indicators import index_daily_rate
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import next_business_day
from backend.features.funds.fees import management_fee, performance_charge
from backend.features.funds.fund_account import DayTrades, FundAccount
from backend.features.funds.fund_maker import STOCK_SHARE, FundMaker
from backend.features.funds.fund_offer import FundOffer
from backend.features.funds.ranking_price import (
    RANKING_WINDOW,
    TradedDay,
    ranking_price,
)
from backend.features.simulation.simulation_engine import SimulationEngine

# Meses entre duas cobranças de performance, contados da oferta
PERFORMANCE_PERIOD_MONTHS = 6


def nav_per_quota(
    cash: Decimal,
    equity: Decimal,
    fixed: Decimal,
    debt: Decimal,
    quotas: Decimal,
) -> Decimal | None:
    """O patrimônio líquido (PL) por cota: (caixa + ações + renda fixa - dívida) / cotas.

    Sem cota em circulação o PL por cota não existe.
    """
    if quotas <= 0:
        return None
    return (cash + equity + fixed - debt) / quotas


def cdi_growth(start: date, end: date) -> Decimal:
    """O fator do CDI acumulado nos dias úteis depois de `start` até `end` (1,05 é 5% acumulados)."""
    factor = Decimal(1)
    day = next_business_day(start)
    while day <= end:
        rate = index_daily_rate(IndicatorSeries.CDI, day)
        if rate is not None:
            factor *= 1 + rate
        day = next_business_day(day)
    return factor


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def close_candle(
    stock: StockDTO,
    day: date,
    trades: DayTrades,
    previous_close: float | None,
    nav: Decimal,
) -> CandleDTO:
    """A vela do pregão: primeiro negócio, máxima, mínima, último negócio e volume.

    Sem negócio, a vela repete o último fechamento (ou o PL, na estreia) e o volume é zero.
    """
    if trades.open is None:
        close = previous_close if previous_close is not None else float(nav)
        open_ = high = low = close
    else:
        open_, high, low, close = (
            float(trades.open),
            float(trades.high),
            float(trades.low),
            float(trades.close),
        )
    change = close - open_
    return CandleDTO(
        id=stock.id,
        ticker=stock.ticker,
        name=stock.name,
        asset_class=stock.asset_class,
        origin=stock.origin,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=int(trades.quantity),
        price_date=day,
        change=round(change, 2),
        change_pct=change / open_ if open_ else 0,
    )


@dataclass
class Fund:
    """O estado vivo de uma gestora: os termos gravados, a conta do motor e o último PL."""

    terms: FundDTO
    account: FundAccount
    # Os últimos pregões negociados, em ordem cronológica, para o preço de ranking
    days: list[TradedDay] = field(default_factory=list)
    nav: Decimal | None = None
    last_close: float | None = None

    @property
    def ticker(self) -> str:
        return self.terms.ticker

    @property
    def listed(self) -> bool:
        return self.terms.listed_on is not None


class FundBook:
    """As gestoras da partida, ligadas ao motor: o PL do dia, o formador de mercado, a oferta
    pública, a vela da cota e as taxas.

    O dia tem duas pontas, na ordem do tick: `on_open` recalcula o PL e refaz as ordens do
    formador e da oferta antes de qualquer jogador ou bot operar; `on_close` fecha a vela com
    os negócios do pregão, grava e deixa o preço de ranking pronto para o snapshot.
    """

    def __init__(
        self,
        simulation_id: int,
        engine: SimulationEngine,
        client_of_user: Callable[[int], UUID],
    ) -> None:
        self._simulation_id = simulation_id
        self._engine = engine
        self._client_of_user = client_of_user
        self._funds: dict[str, Fund] = {}
        accounts = engine.broker.fund_accounts
        self._maker = FundMaker(engine.matching_engine, accounts)
        self._offer = FundOffer(engine.matching_engine, accounts)
        for terms in repository.fund.of_simulation(simulation_id):
            self._load(terms)

    @property
    def client_ids(self) -> list[UUID]:
        """As contas das gestoras no motor."""
        return [fund.account.client_id for fund in self._funds.values()]

    def funds(self) -> list[Fund]:
        return list(self._funds.values())

    def get(self, ticker: str) -> Fund:
        return self._funds[ticker]

    # =========================
    # Criação e oferta
    # =========================

    def found(
        self,
        *,
        ticker: str,
        name: str,
        founder_user_id: int,
        manager_user_id: int,
        management_fee: Decimal,
        performance_fee: Decimal,
    ) -> Fund:
        """Cria a gestora vazia: a cota entra no catálogo da partida e a carteira dela, no motor."""
        stock = repository.stock.add_stock(ticker, name, AssetClass.FUND)
        terms = repository.fund.create(
            simulation_id=self._simulation_id,
            stock_id=stock.id,
            ticker=ticker,
            client_id=uuid4(),
            founder_user_id=founder_user_id,
            manager_user_id=manager_user_id,
            name=name,
            management_fee=management_fee,
            performance_fee=performance_fee,
        )
        return self._load(terms)

    def open_offer(self, ticker: str, size: Decimal) -> None:
        """Abre a oferta pública de `size` cotas novas ao PL de hoje.

        O formador subscreve `STOCK_SHARE x (cotas + size)` ao PL de antes da subscrição e paga
        as cotas dele ao PL em dinheiro sintético, que entra no caixa da gestora: o PL por cota segue o
        mesmo e é ele que vale dali em diante, na oferta, nas ordens e na marca d'água da
        performance.
        """
        fund = self._funds[ticker]
        nav = self._nav(fund)
        if nav is None or fund.listed:
            raise ValueError("A oferta abre uma vez, numa gestora com cotas")
        today = self._engine.current_date
        account = fund.account
        account.offer_remaining = size
        stake = Decimal(math.floor(float(account.quotas + size) * STOCK_SHARE))
        account.subscribe_maker(stake, nav)
        self._engine.credit_fund_subscription(account.client_id, stake * nav)
        fund.nav = nav
        fund.terms = fund.terms.model_copy(
            update={
                "listed_on": today,
                "high_water_mark": nav,
                "high_water_mark_on": today,
            }
        )
        self._refresh_orders(fund, today)
        self._save(fund)

    def close_offer(self, ticker: str) -> None:
        """Encerra a oferta: o que não vendeu não é emitido."""
        fund = self._funds[ticker]
        self._offer.close(ticker)
        self._save(fund)

    # =========================
    # Dia
    # =========================

    def on_open(self, today: date) -> None:
        """O PL de cada gestora com cota e as ordens do formador e da oferta, refeitas em volta dele.

        O preço de ranking vale desde já na carteira de quem tem a cota.
        """
        for fund in self._funds.values():
            nav = self._nav(fund)
            if nav is None:
                continue
            fund.nav = nav
            self._engine.ranking_prices[fund.ticker] = ranking_price(fund.days, nav)
            if fund.listed:
                self._refresh_orders(fund, today)

    def on_close(self, today: date) -> None:
        """Fecha o pregão das gestoras listadas: vela, fechamento do dia, preço de ranking e estado."""
        for fund in self._funds.values():
            if fund.nav is None or not fund.listed:
                continue
            trades = fund.account.take_day()
            stock = self._engine.stocks[fund.ticker]
            candle = close_candle(stock, today, trades, fund.last_close, fund.nav)
            fund.last_close = candle.close
            fund.days = [*fund.days, TradedDay(trades.quantity, trades.value)][
                -RANKING_WINDOW:
            ]
            ranking = ranking_price(fund.days, fund.nav)
            self._engine.ranking_prices[fund.ticker] = ranking

            repository.fund.save_candle(self._simulation_id, candle)
            repository.fund.save_day(
                fund.terms.id,
                FundDayDTO(
                    day=today,
                    nav=fund.nav,
                    quotas=fund.account.quotas,
                    traded_quantity=trades.quantity,
                    traded_value=trades.value,
                    ranking_price=ranking,
                ),
            )
            self._engine.update_market_data([candle])
            self._save(fund)

    def on_month(self, today: date) -> None:
        """Vira as taxas pedidas e cobra as do mês: administração todo mês e performance a cada semestre."""
        for fund in self._funds.values():
            self._apply_pending(fund, today)
            if not fund.listed or fund.nav is None:
                continue
            self._charge_management(fund)
            self._charge_performance(fund, today)
            self._save(fund)

    # =========================
    # Taxas
    # =========================

    def _apply_pending(self, fund: Fund, today: date) -> None:
        terms = fund.terms
        if terms.pending_from is None or terms.pending_from > today:
            return
        fund.terms = terms.model_copy(
            update={
                "management_fee": terms.pending_management_fee
                if terms.pending_management_fee is not None
                else terms.management_fee,
                "performance_fee": terms.pending_performance_fee
                if terms.pending_performance_fee is not None
                else terms.performance_fee,
                "pending_management_fee": None,
                "pending_performance_fee": None,
                "pending_from": None,
            }
        )
        self._save(fund)

    def _charge_management(self, fund: Fund) -> None:
        if fund.nav is None:
            return
        fee = management_fee(
            fund.nav, fund.account.outside_quotas, fund.terms.management_fee
        )
        self._pay(fund, fee, performance=False)

    def _charge_performance(self, fund: Fund, today: date) -> None:
        terms = fund.terms
        if (
            fund.nav is None
            or terms.listed_on is None
            or terms.high_water_mark is None
            or terms.high_water_mark_on is None
        ):
            return
        base = terms.last_performance_on or terms.listed_on
        if months_between(base, today) < PERFORMANCE_PERIOD_MONTHS:
            return
        charge = performance_charge(
            nav=fund.nav,
            quotas=fund.account.quotas,
            outside_quotas=fund.account.outside_quotas,
            rate=terms.performance_fee,
            high_water_mark=terms.high_water_mark,
            high_water_mark_on=terms.high_water_mark_on,
            today=today,
            cdi_growth=cdi_growth(terms.high_water_mark_on, today),
        )
        self._pay(fund, charge.fee, performance=True)
        fund.terms = terms.model_copy(
            update={
                "high_water_mark": charge.high_water_mark,
                "high_water_mark_on": charge.high_water_mark_on,
                "last_performance_on": today,
            }
        )

    def _pay(self, fund: Fund, fee: Decimal, *, performance: bool) -> None:
        """A taxa sai do caixa da gestora e entra no caixa pessoal do gestor."""
        if fee <= 0:
            return
        manager = self._client_of_user(fund.terms.manager_user_id)
        self._engine.charge_fund_fee(fund.account.client_id, fee, performance)
        self._engine.receive_fund_fee(manager, fee, performance)

    # =========================
    # Apoio
    # =========================

    def _load(self, terms: FundDTO) -> Fund:
        """Põe a gestora no motor: conta, carteira, cota no catálogo e a janela do preço de ranking."""
        account = FundAccount(
            client_id=terms.client_id,
            quotas=terms.quotas,
            maker_quotas=terms.maker_quotas,
            maker_cash=terms.maker_cash,
            offer_remaining=terms.offer_remaining,
        )
        # Os dias depois do último processado são refeitos pelo tick
        after = self._engine.current_date + timedelta(days=1)
        repository.fund.drop_days_from(terms.id, after)
        days = repository.fund.days(terms.id, after, RANKING_WINDOW)
        fund = Fund(
            terms=terms,
            account=account,
            days=[TradedDay(d.traded_quantity, d.traded_value) for d in days],
            last_close=repository.fund.last_close(
                self._simulation_id, terms.stock_id, self._engine.current_date
            ),
        )
        self._funds[terms.ticker] = fund
        self._engine.broker.fund_accounts[terms.ticker] = account
        SimulationManager.add_fund_portfolios({terms.client_id: terms.portfolio_id})
        self._engine.add_fund_stock(
            StockDTO(
                id=terms.stock_id,
                ticker=terms.ticker,
                name=terms.name,
                asset_class=AssetClass.FUND,
            )
        )
        return fund

    def _nav(self, fund: Fund) -> Decimal | None:
        """O PL por cota pelo balanço da carteira da gestora."""
        balance = self._engine.balance_sheet(fund.account.client_id)
        return nav_per_quota(
            balance.total_cash,
            balance.total_equity,
            balance.total_fixed,
            balance.total_debt,
            fund.account.quotas,
        )

    def _refresh_orders(self, fund: Fund, today: date) -> None:
        """A escada do formador e a ordem da oferta, ao PL do dia."""
        if fund.nav is None:
            return
        self._maker.refresh(fund.ticker, float(fund.nav), fund.account.quotas, today)
        self._offer.refresh(fund.ticker, float(fund.nav), today)

    def _save(self, fund: Fund) -> None:
        account = fund.account
        fund.terms = fund.terms.model_copy(
            update={
                "quotas": account.quotas,
                "maker_quotas": account.maker_quotas,
                "maker_cash": account.maker_cash,
                "offer_remaining": account.offer_remaining,
            }
        )
        repository.fund.save(fund.terms)
