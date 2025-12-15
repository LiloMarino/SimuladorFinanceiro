from datetime import datetime
from decimal import Decimal

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO, CashflowEventType
from backend.core.dto.stock import StockDTO
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.realtime import notify
from backend.features.simulation.broker import Broker
from backend.features.simulation.entities.candle import Candle
from backend.features.simulation.entities.portfolio import Portfolio
from backend.features.simulation.fixed_broker import FixedBroker
from backend.features.strategy.base_strategy import BaseStrategy


class SimulationEngine:
    def __init__(self):
        self.broker = Broker(self)
        self.fixed_broker = FixedBroker(self)
        self.fixed_income_market = FixedIncomeMarket()
        self._cash: LazyDict[str, float] = LazyDict(
            loader=repository.user.get_user_balance
        )
        self._strategy = None

        # Configura os alias
        self.get_positions = self.broker.get_positions

    def set_strategy(self, strategy_cls: type[BaseStrategy], *args, **kwargs):
        self._strategy = strategy_cls(self.broker, *args, **kwargs)

    def get_cash(self, client_id: str) -> float:
        return self._cash[client_id]

    def add_cash(self, client_id: str, cash: float):
        self._cash[client_id] += cash
        EventManager.push_event(
            CashflowEventDTO(
                user_id=UserManager.get_user_id(client_id),
                event_type=CashflowEventType.DEPOSIT
                if cash > 0
                else CashflowEventType.WITHDRAW,
                amount=Decimal(abs(cash)),
                event_date=datetime.now().date(),
            )
        )
        notify("cash_update", {"cash": self._cash[client_id]})

    def update_market_data(self, stocks: list[StockDTO]):
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
            self.broker.data_buffer.add_candle(candle)

    def get_portfolio(self, client_id: str) -> Portfolio:
        return Portfolio(
            cash=self._cash[client_id],
            variable_income=list(self.broker.get_positions().values()),
            fixed_income=list(self.fixed_broker.get_assets().values()),
            patrimonial_history=[],
        )

    def next(self, current_date: datetime):
        self.fixed_income_market.refresh_assets(current_date)

        # Aplica juros dos ativos de renda fixa
        self.fixed_broker.apply_daily_interest(current_date)

        # Executa a estratégia
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
