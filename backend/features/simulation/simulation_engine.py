from datetime import datetime
from decimal import Decimal

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PositionDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import CashflowEventType
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.realtime import notify
from backend.features.simulation.broker import Broker
from backend.features.simulation.entities.candle import Candle
from backend.features.simulation.fixed_broker import FixedBroker
from backend.features.strategy.base_strategy import BaseStrategy


class SimulationEngine:
    def __init__(self, current_date):
        self.broker = Broker(self)
        self.fixed_broker = FixedBroker(self)
        self.fixed_income_market = FixedIncomeMarket()
        self._cash: LazyDict[str, float] = LazyDict(
            loader=repository.user.get_user_balance
        )
        self._strategy = None
        self.current_date: datetime = current_date

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
                event_date=self.current_date.date(),
            )
        )
        notify("cash_update", {"cash": self._cash[client_id]}, to=client_id)

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

    def get_portfolio(self, client_id: str) -> PortfolioDTO:
        positions = self.broker.get_positions(client_id).values()
        variable_income = [
            PositionDTO(
                ticker=pos.ticker,
                size=pos.size,
                total_cost=pos.total_cost,
                avg_price=pos.avg_price,
            )
            for pos in positions
            if pos.size > 0
        ]

        fixed_income_positions = self.fixed_broker.get_fixed_positions(
            client_id
        ).values()
        fixed_income = [
            FixedIncomePositionDTO(
                asset=pos.asset,
                total_applied=pos.total_applied,
                current_value=pos.current_value,
            )
            for pos in fixed_income_positions
        ]

        return PortfolioDTO(
            cash=self._cash[client_id],
            variable_income=variable_income,
            fixed_income=fixed_income,
            patrimonial_history=repository.portfolio.get_patrimonial_history(
                UserManager.get_user_id(client_id)
            ),
        )

    def next(self, current_date: datetime):
        self.current_date = current_date

        self.fixed_income_market.refresh_assets(current_date)

        # Aplica juros dos ativos de renda fixa
        # self.fixed_broker.apply_daily_interest(current_date)

        # Executa a estratégia
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
