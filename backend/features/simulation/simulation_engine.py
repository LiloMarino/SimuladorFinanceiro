import threading
from datetime import date
from decimal import Decimal
from functools import cached_property
from uuid import UUID

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.order_preview import OrderPreviewDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PortfolioPositionDTO, PositionDTO
from backend.core.dto.sector import StockSegmentDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    CashflowEventType,
    EquityEventType,
    OrderAction,
)
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.sectors import allocate_by_sector
from backend.core.utils import ratio
from backend.core.utils.lazy_dict import LazyDict
from backend.features.credit.credit_book import CreditBook
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.fixed_broker import FixedBroker
from backend.features.fixed_income.liquidity import redeemable_today, total_redeemable
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.realtime import notify
from backend.features.realtime.schemas import CashUpdateEventDTO
from backend.features.statistics.sectors import effective_sectors
from backend.features.variable_income.broker import (
    Broker,
    affordable_quantity,
    to_money,
)
from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.order import MarketOrder
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.income_tax import (
    CRYPTO_EXEMPTION_LIMIT,
    EXEMPTION_LIMITS,
    STOCK_EXEMPTION_LIMIT,
    MonthlyTax,
    assess,
    darf_due_date,
)
from backend.features.variable_income.matching_engine import MatchingEngine


class SimulationEngine:
    """
    Motor central da simulação financeira.

    Responsável por:
    - Coordenar brokers de renda variável e fixa
    - Gerenciar saldo em caixa dos players com cache lazy
    - Atualizar dados de mercado e executar matching de ordens
    - Aplicar juros diários de renda fixa
    - Registrar eventos de cashflow (depósitos, retiradas, aportes, IR)
    """

    def __init__(
        self,
        current_date,
        starting_cash: Decimal,
        simulation_id: int,
        end_date: date,
    ):
        # Protege _cash (aqui) e _positions/_assets (Broker/FixedBroker) contra
        # mutação concorrente pela thread do loop e pelas threads de request HTTP.
        self._lock = threading.RLock()
        self.broker = Broker(self, self._lock)
        self.fixed_broker = FixedBroker(self, self._lock)
        self.credit_book = CreditBook(self, self._lock)
        self.fixed_income_market = FixedIncomeMarket(simulation_id, end_date)
        self.matching_engine = MatchingEngine(self.broker)
        self._cash: LazyDict[UUID, Decimal] = LazyDict(
            loader=repository.user.get_user_balance
        )
        self.current_date: date = current_date
        self.starting_cash = starting_cash
        self.simulation_id = simulation_id

        # Configura os alias
        self.get_positions = self.broker.get_positions

    def get_cash(self, client_id: UUID) -> Decimal:
        with self._lock:
            return self._cash[client_id]

    def _move_cash(
        self,
        client_id: UUID,
        delta: Decimal,
        event_type: CashflowEventType,
        life_event_key: str | None = None,
    ) -> None:
        with self._lock:
            self._cash[client_id] += delta
            new_cash = self._cash[client_id]
        EventManager.push_event(
            CashflowEventDTO(
                simulation_id=self.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=event_type,
                amount=abs(delta),
                event_date=self.current_date,
                life_event_key=life_event_key,
            )
        )
        notify("cash_update", CashUpdateEventDTO(cash=new_cash).to_json(), to=client_id)

    def add_cash(self, client_id: UUID, cash: Decimal) -> None:
        self._move_cash(
            client_id,
            cash,
            CashflowEventType.DEPOSIT if cash > 0 else CashflowEventType.WITHDRAW,
        )

    def add_contribution(self, client_id: UUID, amount: Decimal) -> None:
        """Adiciona aporte mensal (não conta como retorno de investimento)"""
        self._move_cash(client_id, amount, CashflowEventType.CONTRIBUTION)

    def pay_income_tax(self, client_id: UUID, amount: Decimal) -> None:
        """Debita o DARF; o caixa pode ficar negativo, como uma dívida com a Receita."""
        self._move_cash(client_id, -amount, CashflowEventType.TAX)

    def pay_salary(self, client_id: UUID, amount: Decimal) -> None:
        self._move_cash(client_id, amount, CashflowEventType.SALARY)

    def pay_expense(self, client_id: UUID, amount: Decimal) -> None:
        """Debita a despesa do mês; o caixa pode ficar negativo e cair no cheque especial."""
        self._move_cash(client_id, -amount, CashflowEventType.EXPENSE)

    def charge_unexpected(self, client_id: UUID, amount: Decimal, key: str) -> None:
        """Debita um imprevisto; a demissão entra com valor zero, para ficar no histórico."""
        self._move_cash(client_id, -amount, CashflowEventType.UNEXPECTED_EXPENSE, key)

    def charge_overdraft_interest(self, client_id: UUID, amount: Decimal) -> None:
        self._move_cash(client_id, -amount, CashflowEventType.OVERDRAFT_INTEREST)

    def receive_loan(self, client_id: UUID, amount: Decimal) -> None:
        self._move_cash(client_id, amount, CashflowEventType.LOAN_PROCEEDS)

    def pay_loan(self, client_id: UUID, amount: Decimal) -> None:
        """Debita parcela, amortização, quitação ou atraso; o caixa pode passar do saldo só quando quem chama já o conferiu."""
        self._move_cash(client_id, -amount, CashflowEventType.LOAN_PAYMENT)

    def assess_income_tax(self, user_id: int) -> list[MonthlyTax]:
        asset_classes = {ticker: s.asset_class for ticker, s in self.stocks.items()}
        return assess(
            repository.portfolio.get_equity_events(user_id),
            asset_classes,
            self.current_date,
        )

    def asset_class(self, ticker: str) -> AssetClass | None:
        stock = self.stocks.get(ticker)
        return stock.asset_class if stock else None

    def check_quantity(self, ticker: str, quantity: Decimal) -> None:
        """Fração de unidade só vale para a classe fracionável; as demais negociam inteiros."""
        asset_class = self.asset_class(ticker)
        if (
            asset_class is not None
            and not asset_class.fractional
            and quantity != quantity.to_integral_value()
        ):
            raise UnprocessableEntityError("Este ativo só negocia quantidade inteira")

    def affordable(self, ticker: str, money: Decimal, price: Decimal | None) -> Decimal:
        """O que o dinheiro paga ao preço: inteiro, ou até oito casas na cripto."""
        asset_class = self.asset_class(ticker)
        return affordable_quantity(
            money,
            price,
            fractional=asset_class is not None and asset_class.fractional,
        )

    def estimated_price(
        self, ticker: str, action: OrderAction, limit_price: float | None
    ) -> Decimal | None:
        """O limite; a mercado, o melhor do outro lado do book; sem book, o último fechamento."""
        if limit_price is not None:
            return to_money(limit_price)
        book = self.matching_engine.order_book
        best = (
            book.best_sell(ticker)
            if action == OrderAction.BUY
            else book.best_buy(ticker)
        )
        if best is not None:
            return to_money(best.price)
        last = self.matching_engine.market_data.get_last(ticker)
        return to_money(last.close) if last else None

    def size_budget_order(self, order: MarketOrder) -> None:
        """Dá à compra por valor a quantidade que o valor paga ao melhor preço de hoje."""
        assert order.budget is not None
        price = self.estimated_price(order.ticker, order.action, None)
        order.size = order.remaining = self.affordable(
            order.ticker, order.budget, price
        )
        if order.size <= 0:
            raise UnprocessableEntityError("O valor não paga uma unidade")

    def preview_order(
        self,
        client_id: UUID,
        ticker: str,
        action: OrderAction,
        quantity: Decimal | None,
        limit_price: float | None,
        amount: Decimal | None = None,
    ) -> OrderPreviewDTO:
        position = self.broker.get_positions(client_id).get(ticker)
        held = position.size if position else Decimal(0)
        reserved = position.reserved if position else Decimal(0)
        cash = self.get_cash(client_id)
        asset_class = self.asset_class(ticker)

        price = self.estimated_price(ticker, action, limit_price)
        # Por valor, a quantidade é a que o valor paga ao preço estimado
        if quantity is None:
            assert amount is not None
            quantity = self.affordable(ticker, amount, price)
        self.check_quantity(ticker, quantity)

        total = (price or Decimal(0)) * quantity
        buying = action == OrderAction.BUY
        preview = OrderPreviewDTO(
            price=price,
            quantity=quantity,
            total=total,
            cash_before=cash,
            cash_after=cash - total if buying else cash + total,
            max_quantity=self.affordable(ticker, cash, price)
            if buying
            else held - reserved,
            held=held,
            reserved=reserved,
            profit=None,
            tax=None,
            month_sales_after=None,
            exemption_limit=EXEMPTION_LIMITS.get(
                asset_class or AssetClass.STOCK, STOCK_EXEMPTION_LIMIT
            ),
            tax_due_date=None,
        )
        if buying or not position or price is None or quantity <= 0:
            return preview

        # IR da venda: o imposto do mês com a venda hipotética menos o imposto sem ela
        user_id = UserManager.get_user_id(client_id)
        events = repository.portfolio.get_equity_events(user_id)
        sale = EquityEventDTO(
            simulation_id=self.simulation_id,
            user_id=user_id,
            event_date=self.current_date,
            ticker=ticker,
            event_type=EquityEventType.SELL,
            quantity=quantity,
            price=price,
        )
        asset_classes = {ticker: s.asset_class for ticker, s in self.stocks.items()}
        today = self.current_date
        without = _month(assess(events, asset_classes, today), today)
        with_sale = _month(assess([*events, sale], asset_classes, today), today)
        return preview.model_copy(
            update={
                "profit": (price - position.avg_price) * quantity,
                "tax": (with_sale.tax if with_sale else Decimal(0))
                - (without.tax if without else Decimal(0)),
                "month_sales_after": (
                    with_sale.crypto_sales
                    if asset_class is AssetClass.CRYPTO
                    else with_sale.stock_sales
                )
                if with_sale
                else Decimal(0),
                "tax_due_date": darf_due_date(today.year, today.month),
            }
        )

    def update_market_data(self, stocks: list[CandleDTO]) -> None:
        for s in stocks:
            candle = Candle(
                ticker=s.ticker,
                price_date=s.price_date,
                open=s.open,
                high=s.high,
                low=s.low,
                close=s.close,
                volume=s.volume,
            )
            self.matching_engine.market_data.add_candle(candle)
            self.matching_engine.on_tick(s.ticker)

    def get_current_price(self, position: Position) -> Decimal:
        """Último fechamento do ativo; sem candle no buffer, o preço médio da posição."""
        candle = self.matching_engine.market_data.get_last(position.ticker)
        return to_money(candle.close) if candle else position.avg_price

    @cached_property
    def stocks(self) -> dict[str, StockDTO]:
        """Catálogo estável na partida: nomes e classes só mudam na Central, fora dela."""
        return {stock.ticker: stock for stock in repository.stock.get_stocks()}

    @cached_property
    def classification(self) -> dict[str, StockSegmentDTO]:
        """
        Setor e segmento de cada ação, lidos uma vez por partida: a classificação
        se edita na Central de dados, que só abre com a partida parada.
        """
        return repository.stock.get_classification()

    def _holdings(
        self, client_id: UUID
    ) -> tuple[list[PositionDTO], list[FixedIncomePosition], Decimal]:
        """Renda variável, renda fixa e caixa do jogador num instante só."""
        with self._lock:
            equity = [
                pos.to_dto(self.get_current_price(pos))
                for pos in self.broker.get_positions(client_id).values()
                if pos.size > 0
            ]
            fixed = list(self.fixed_broker.get_fixed_positions(client_id).values())
            return equity, fixed, self._cash[client_id]

    def balance_sheet(
        self, client_id: UUID
    ) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        """Ações, renda fixa, caixa e dívida do dia: o que o snapshot guarda, sem montar o portfólio da tela."""
        equity, fixed, cash = self._holdings(client_id)
        return (
            sum((p.current_value for p in equity), Decimal(0)),
            sum((p.current_value for p in fixed), Decimal(0)),
            cash,
            self.credit_book.debt(client_id, self.current_date),
        )

    def assets_value(self, client_id: UUID) -> Decimal:
        """Caixa, ações e renda fixa, sem descontar a dívida."""
        equity, fixed, cash = self._holdings(client_id)
        return (
            sum((p.current_value for p in equity), Decimal(0))
            + sum((p.current_value for p in fixed), Decimal(0))
            + cash
        )

    def get_portfolio(self, client_id: UUID) -> PortfolioDTO:
        equity, fixed, cash = self._holdings(client_id)

        variable_income_value = sum((p.current_value for p in equity), Decimal(0))
        fixed_income_value = sum((p.current_value for p in fixed), Decimal(0))
        invested_value = variable_income_value + fixed_income_value
        # Os percentuais de alocação são sobre os ativos; o patrimônio é o líquido da dívida
        assets_value = invested_value + cash
        debt = self.credit_book.debt(client_id, self.current_date)
        total_networth = assets_value - debt

        # Aporte mensal é capital do jogador, não rendimento
        user_id = UserManager.get_user_id(client_id)
        capital_provided = self.starting_cash + repository.user.get_total_contribution(
            user_id
        )

        # A pagar: o apurado que ainda não venceu, o saldo abaixo do mínimo do DARF
        # e o mês corrente até agora
        income_tax_paid = repository.user.get_total_cashflow(
            user_id, CashflowEventType.TAX
        )
        months = self.assess_income_tax(user_id)
        income_tax_assessed = sum((m.tax for m in months), Decimal(0))
        today = self.current_date
        this_month = next(
            (m for m in months if (m.year, m.month) == (today.year, today.month)), None
        )
        upcoming_due = [
            m.due_date
            for m in months
            if m.darf_amount and m.due_date and m.due_date >= today
        ]
        sectors = allocate_by_sector(
            {pos.ticker: pos.current_value for pos in equity}, self.classification
        )
        names = {ticker: s.name for ticker, s in self.stocks.items()}

        return PortfolioDTO(
            starting_cash=self.starting_cash,
            cash=cash,
            total_networth=total_networth,
            invested_value=invested_value,
            variable_income_value=variable_income_value,
            fixed_income_value=fixed_income_value,
            fixed_income_redeemable=total_redeemable(fixed, self.current_date),
            invested_pct=ratio(invested_value, assets_value),
            variable_income_pct=ratio(variable_income_value, invested_value),
            fixed_income_pct=ratio(fixed_income_value, invested_value),
            capital_provided=capital_provided,
            total_return_value=total_networth - capital_provided,
            total_return_pct=ratio(total_networth - capital_provided, capital_provided),
            variable_income_networth_pct=ratio(variable_income_value, assets_value),
            fixed_income_networth_pct=ratio(fixed_income_value, assets_value),
            cash_pct=ratio(cash, assets_value),
            assets_value=assets_value,
            debt=debt,
            credit_alert=self.credit_book.alert(client_id, self.current_date),
            income_tax_paid=income_tax_paid,
            income_tax_due=income_tax_assessed - income_tax_paid,
            income_tax_due_date=min(upcoming_due) if upcoming_due else None,
            month_stock_sales=this_month.stock_sales if this_month else Decimal(0),
            stock_sales_exemption=STOCK_EXEMPTION_LIMIT,
            month_crypto_sales=this_month.crypto_sales if this_month else Decimal(0),
            crypto_sales_exemption=CRYPTO_EXEMPTION_LIMIT,
            variable_income=[
                PortfolioPositionDTO(
                    **pos.model_dump(),
                    name=names.get(pos.ticker, pos.ticker),
                    portfolio_pct=ratio(pos.current_value, invested_value),
                )
                for pos in equity
            ],
            sectors=sectors,
            effective_sectors=effective_sectors(sectors),
            fixed_income=[
                FixedIncomePositionDTO(
                    asset=pos.asset,
                    total_applied=pos.total_applied,
                    current_value=pos.current_value,
                    first_applied_date=pos.first_applied_date,
                    return_value=pos.current_value - pos.total_applied,
                    return_pct=ratio(
                        pos.current_value - pos.total_applied, pos.total_applied
                    ),
                    portfolio_pct=ratio(pos.current_value, invested_value),
                    redeemable_today=redeemable_today(pos, self.current_date),
                )
                for pos in fixed
            ],
        )

    def next(self, current_date: date) -> None:
        self.current_date = current_date

        self.fixed_income_market.refresh_assets(current_date)

        # Aplica juros dos ativos de renda fixa
        self.fixed_broker.apply_daily_interest(current_date)


def _month(months: list[MonthlyTax], today: date) -> MonthlyTax | None:
    return next(
        (m for m in months if (m.year, m.month) == (today.year, today.month)), None
    )
