import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_FLOOR, Decimal
from uuid import UUID, uuid4

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fund import (
    FundDayDTO,
    FundDTO,
    FundOfferSaleDTO,
    FundReportDTO,
    FundSummaryDTO,
    FundTermsDTO,
)
from backend.core.dto.stock import StockDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import AssetClass, IndicatorSeries
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.indicators import index_daily_rate
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import next_business_day, next_month_turn
from backend.features.funds import headlines
from backend.features.funds.fees import management_fee, performance_charge
from backend.features.funds.fund_account import DayTrades, FundAccount
from backend.features.funds.fund_ledger import PERFORMANCE_PERIOD_MONTHS
from backend.features.funds.fund_maker import STOCK_SHARE, FundMaker
from backend.features.funds.fund_offer import FundOffer
from backend.features.funds.ranking_price import (
    RANKING_WINDOW,
    TradedDay,
    ranking_price,
)
from backend.features.notifications.news import Headline
from backend.features.simulation.simulation_engine import SimulationEngine

# O PL por cota da primeira integralização
FIRST_NAV = Decimal(100)

# Pregões da oferta pública, contando o da abertura: ao fim do último ela fecha sozinha
OFFER_SESSIONS = 5


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


def offer_ends_on(listed_on: date) -> date:
    """O último pregão da oferta: o quinto dia útil a partir da abertura, contando o dia dela."""
    day = listed_on
    for _ in range(OFFER_SESSIONS - 1):
        day = next_business_day(day)
    return day


def offer_session(listed_on: date, today: date) -> int:
    """O pregão da oferta em `today`: 1 no dia da abertura, até `OFFER_SESSIONS`."""
    session = 1
    day = listed_on
    while day < today and session < OFFER_SESSIONS:
        day = next_business_day(day)
        session += 1
    return session


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


def _decimal_or_none(value: float | None) -> Decimal | None:
    return None if value is None else Decimal(str(value))


@dataclass
class Fund:
    """O estado vivo de uma gestora: os termos gravados, a conta do motor e o último PL."""

    terms: FundDTO
    account: FundAccount
    # Os últimos pregões negociados, em ordem cronológica, para o preço de ranking
    days: list[TradedDay] = field(default_factory=list)
    nav: Decimal | None = None
    last_close: float | None = None
    # O preço do último negócio da cota, de pregões já fechados; nulo se nunca negociou
    last_trade_price: Decimal | None = None
    # O relatório mensal do último fechamento de mês, guardado pelo dia da virada que o gerou
    report: tuple[date, FundReportDTO] | None = None

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
    os negócios do pregão, fecha a oferta que chegou ao último pregão, grava e deixa o preço de
    ranking pronto para o snapshot.

    A gestora congela enquanto o gestor governa o país: `frozen_until` devolve o último dia do
    mandato dele, lido do governo a cada consulta. A sala segue negociando a cota; só a conta da
    gestora e o que o gestor decide nela (aporte, oferta, taxas) param, e as taxas não correm.
    """

    def __init__(
        self,
        simulation_id: int,
        engine: SimulationEngine,
        client_of_user: Callable[[int], UUID],
        publish: Callable[[date, Headline], None] | None = None,
        frozen_until: Callable[[int], date | None] | None = None,
        participants: Callable[[], list[UserDTO]] | None = None,
    ) -> None:
        self._simulation_id = simulation_id
        self._engine = engine
        self._client_of_user = client_of_user
        self._publish = publish
        # O último dia do mandato do gestor que governa, por id de usuário; nulo se ele não governa
        self._manager_frozen_until = frozen_until or (lambda _user_id: None)
        # Os jogadores e bots da partida, lidos a cada consulta
        self.participants = participants or (lambda: [])
        self._funds: dict[str, Fund] = {}
        accounts = engine.broker.fund_accounts
        self._maker = FundMaker(engine.matching_engine, accounts)
        self._offer = FundOffer(engine.matching_engine, accounts)
        engine.broker.on_fund_offer_sale = self._record_offer_sale
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

    def by_id(self, fund_id: int) -> Fund:
        for fund in self._funds.values():
            if fund.terms.id == fund_id:
                return fund
        raise NotFoundError("Gestora não encontrada")

    def founder_of(self, ticker: str) -> int | None:
        """O fundador da gestora que já tem este ticker na partida."""
        fund = self._funds.get(ticker)
        return fund.terms.founder_user_id if fund else None

    def of_client(self, client_id: UUID) -> Fund | None:
        """A gestora dona da conta `client_id` no motor."""
        for fund in self._funds.values():
            if fund.account.client_id == client_id:
                return fund
        return None

    def frozen_until(self, fund: Fund) -> date | None:
        """O último dia em que a gestora fica congelada: o fim do mandato do gestor presidente."""
        return self._manager_frozen_until(fund.terms.manager_user_id)

    def price(self, fund: Fund) -> Decimal | None:
        """O preço do último negócio da cota: o de hoje se já negociou, senão o do último pregão com negócio."""
        today = fund.account.day
        return today.close if today.open is not None else fund.last_trade_price

    def summary(
        self, fund: Fund, nicknames: Mapping[int, str] | None = None
    ) -> FundSummaryDTO:
        """A gestora com o PL por cota de agora, o preço de ranking, o último negócio, a oferta e o congelamento.

        `nicknames` são os apelidos por id de usuário; sem eles a consulta lê os participantes.
        """
        if nicknames is None:
            nicknames = {user.id: user.nickname for user in self.participants()}
        listed_on = fund.terms.listed_on
        open_on = listed_on if fund.account.offer_remaining is not None else None
        return FundSummaryDTO(
            **fund.terms.model_dump(include=set(FundTermsDTO.model_fields)),
            nav=self._nav(fund),
            ranking_price=self._engine.ranking_prices.get(fund.ticker),
            price=self.price(fund),
            manager_nickname=nicknames.get(fund.terms.manager_user_id),
            offer_session=(
                offer_session(open_on, self._engine.current_date) if open_on else None
            ),
            offer_ends_on=offer_ends_on(open_on) if open_on else None,
            frozen_until=self.frozen_until(fund),
        )

    def summaries(self) -> list[FundSummaryDTO]:
        """A lista de gestoras da partida, com os apelidos lidos uma vez."""
        nicknames = {user.id: user.nickname for user in self.participants()}
        return [self.summary(fund, nicknames) for fund in self._funds.values()]

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
        if ticker in self._funds:
            raise ConflictError("Já existe uma gestora com este ticker na partida")
        stock = repository.fund.claim_stock(ticker, name)
        if stock is None:
            raise ConflictError("As quatro letras deste ticker já são de um ativo")
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

    def contribute(
        self,
        ticker: str,
        manager: UUID,
        cash: Decimal,
        stocks: Mapping[str, Decimal],
    ) -> Decimal:
        """Integraliza caixa e ações do gestor na gestora e devolve as cotas emitidas a ele.

        As cotas valem o que foi levado a preço de mercado, ao PL do dia (R$ 100 na primeira
        integralização), arredondadas para baixo; a sobra fica na gestora. O custo médio das
        ações vai junto e as cotas nascem com o custo contábil do que foi levado, de modo que a
        integralização não gera venda nem DARF.
        """
        fund = self._funds[ticker]
        if fund.listed:
            raise ConflictError("A integralização só vale antes da oferta pública")
        if cash <= 0 and not stocks:
            raise UnprocessableEntityError("Informe o que integralizar")
        engine = self._engine
        if engine.get_cash(manager) < cash:
            raise UnprocessableEntityError("Caixa insuficiente para integralizar")

        # Confere tudo antes de mover qualquer coisa
        value = cost = cash
        positions = engine.broker.get_positions(manager)
        for held_ticker, quantity in stocks.items():
            stock = engine.stocks.get(held_ticker)
            if stock is None or stock.asset_class is AssetClass.FUND:
                raise UnprocessableEntityError(
                    f"{held_ticker} não pode ser integralizado"
                )
            if quantity <= 0:
                raise UnprocessableEntityError(
                    "A quantidade precisa ser maior que zero"
                )
            engine.check_quantity(held_ticker, quantity)
            position = positions.get(held_ticker)
            if position is None or position.size - position.reserved < quantity:
                raise UnprocessableEntityError(f"Posição insuficiente em {held_ticker}")
            value += engine.get_current_price(position) * quantity
            cost += position.avg_price * quantity

        nav = self._nav(fund) if fund.account.quotas > 0 else FIRST_NAV
        if nav is None or nav <= 0:
            raise ConflictError("A gestora não tem patrimônio para emitir cotas")
        issued = (value / nav).to_integral_value(rounding=ROUND_FLOOR)
        if issued <= 0:
            raise UnprocessableEntityError("O valor não chega a uma cota")

        fund_client = fund.account.client_id
        if cash > 0:
            engine.transfer_cash(manager, fund_client, cash)
        for held_ticker, quantity in stocks.items():
            engine.broker.transfer_position(manager, fund_client, held_ticker, quantity)
        fund.account.quotas += issued
        engine.broker.receive_position(manager, ticker, issued, cost / issued)
        # O preço de ranking da cota já vale na carteira do gestor
        fund.nav = self._nav(fund)
        if fund.nav is not None:
            engine.ranking_prices[ticker] = ranking_price(fund.days, fund.nav)
        self._save(fund)
        return issued

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
                "offer_quotas": size,
                "offer_price": Decimal(str(round(float(nav), 2))),
                "high_water_mark": nav,
                "high_water_mark_on": today,
            }
        )
        self._refresh_orders(fund, today)
        self._save(fund)
        self._announce(today, headlines.offer_opened(ticker, size))

    def close_offer(self, ticker: str) -> None:
        """Encerra a oferta: o que não vendeu não é emitido."""
        self._close_offer(self._funds[ticker], self._engine.current_date)

    def on_office(self, manager_user_id: int) -> None:
        """O gestor assumiu a presidência: as ordens abertas das gestoras dele saem do livro."""
        for fund in self._funds.values():
            if fund.terms.manager_user_id == manager_user_id:
                self._engine.matching_engine.cancel_all(fund.account.client_id)

    def set_fees(
        self, ticker: str, management_fee: Decimal, performance_fee: Decimal
    ) -> None:
        """Pede as taxas novas, que valem no primeiro dia útil do mês seguinte.

        Pedir as taxas de hoje desfaz o pedido pendente. Cada taxa que muda vira manchete quando
        a gestora já é pública.
        """
        fund = self._funds[ticker]
        terms = fund.terms
        today = self._engine.current_date
        management_changed = management_fee != terms.management_fee
        performance_changed = performance_fee != terms.performance_fee
        changed = management_changed or performance_changed
        fund.terms = terms.model_copy(
            update={
                "pending_management_fee": management_fee if changed else None,
                "pending_performance_fee": performance_fee if changed else None,
                "pending_from": next_month_turn(today) if changed else None,
            }
        )
        self._save(fund)
        if not fund.listed:
            return
        if management_changed:
            self._announce(
                today, headlines.management_fee_changed(ticker, management_fee)
            )
        if performance_changed:
            self._announce(
                today, headlines.performance_fee_changed(ticker, performance_fee)
            )

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

    def on_close(self, today: date) -> list[CandleDTO]:
        """Fecha o pregão das gestoras listadas: vela, fechamento do dia, preço de ranking e estado.

        Devolve as velas do dia, para o tempo real das cotas.
        """
        candles: list[CandleDTO] = []
        for fund in self._funds.values():
            if fund.nav is None or not fund.listed:
                continue
            trades = fund.account.take_day()
            stock = self._engine.stocks[fund.ticker]
            candle = close_candle(stock, today, trades, fund.last_close, fund.nav)
            fund.last_close = candle.close
            if trades.open is not None:
                fund.last_trade_price = trades.close
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
            # A oferta vale até o fim do último pregão dela; o que não vendeu não nasce
            listed_on = fund.terms.listed_on
            if (
                listed_on is not None
                and fund.account.offer_remaining is not None
                and today >= offer_ends_on(listed_on)
            ):
                self._close_offer(fund, today)
            self._save(fund)
            candles.append(candle)
        return candles

    def on_month(self, today: date) -> None:
        """Vira as taxas pedidas e cobra as do mês: administração todo mês e performance a cada semestre."""
        for fund in self._funds.values():
            self._apply_pending(fund, today)
            if (
                not fund.listed
                or fund.nav is None
                or self.frozen_until(fund) is not None
            ):
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
        repository.fund.drop_offer_sales_from(terms.id, after)
        days = repository.fund.days(terms.id, after, RANKING_WINDOW)
        fund = Fund(
            terms=terms,
            account=account,
            days=[TradedDay(d.traded_quantity, d.traded_value) for d in days],
            last_close=repository.fund.last_close(
                self._simulation_id, terms.stock_id, self._engine.current_date
            ),
            last_trade_price=_decimal_or_none(
                repository.fund.last_traded_close(
                    self._simulation_id, terms.stock_id, self._engine.current_date
                )
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

    def _announce(self, day: date, headline: Headline) -> None:
        if self._publish is not None:
            self._publish(day, headline)

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

    def _close_offer(self, fund: Fund, day: date) -> None:
        """Fecha a oferta e grava o dia em que fechou."""
        self._offer.close(fund.ticker)
        fund.terms = fund.terms.model_copy(update={"offer_closed_on": day})
        self._save(fund)

    def _record_offer_sale(
        self,
        ticker: str,
        buyer_user_id: int | None,
        quotas: Decimal,
        price: Decimal,
    ) -> None:
        """Grava a venda da oferta no dia dela, junto das cotas emitidas; a que zera o saldo
        fecha a oferta nesse mesmo dia."""
        fund = self._funds[ticker]
        today = self._engine.current_date
        repository.fund.record_offer_sale(
            fund.terms.id,
            FundOfferSaleDTO(
                day=today, buyer_user_id=buyer_user_id, quotas=quotas, price=price
            ),
        )
        if fund.account.offer_remaining is None:
            fund.terms = fund.terms.model_copy(update={"offer_closed_on": today})
        self._save(fund)

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
