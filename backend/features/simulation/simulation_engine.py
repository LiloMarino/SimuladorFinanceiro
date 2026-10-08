import threading
from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.fixed_income_position import FixedIncomePositionDTO
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.position import PortfolioPositionDTO, PositionDTO
from backend.core.enum import CashflowEventType
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import ratio
from backend.core.utils.lazy_dict import LazyDict
from backend.features.fixed_income.fixed_broker import FixedBroker
from backend.features.fixed_income.market import FixedIncomeMarket
from backend.features.realtime import notify
from backend.features.realtime.schemas import CashUpdateEventDTO
from backend.features.strategy.base_strategy import BaseStrategy
from backend.features.variable_income.broker import Broker, to_money
from backend.features.variable_income.entities.candle import Candle
from backend.features.variable_income.entities.position import Position
from backend.features.variable_income.matching_engine import MatchingEngine


class SimulationEngine:
    """
    Motor central da simulação financeira.

    Responsável por:
    - Coordenar brokers de renda variável e fixa
    - Gerenciar saldo em caixa dos players com cache lazy
    - Atualizar dados de mercado e executar matching de ordens
    - Aplicar juros diários de renda fixa
    - Executar estratégias de trading a cada tick
    - Registrar eventos de cashflow (depósitos, retiradas, aportes)
    """

    def __init__(self, current_date, starting_cash: Decimal, simulation_id: int):
        # Protege _cash (aqui) e _positions/_assets (Broker/FixedBroker) contra
        # mutação concorrente pela thread do loop e pelas threads de request HTTP.
        self._lock = threading.RLock()
        self.broker = Broker(self, self._lock)
        self.fixed_broker = FixedBroker(self, self._lock)
        self.fixed_income_market = FixedIncomeMarket()
        self.matching_engine = MatchingEngine(self.broker)
        self._cash: LazyDict[UUID, Decimal] = LazyDict(
            loader=repository.user.get_user_balance
        )
        self._strategy = None
        self.current_date: date = current_date
        self.starting_cash = starting_cash
        self.simulation_id = simulation_id

        # Configura os alias
        self.get_positions = self.broker.get_positions

    def set_strategy(self, strategy_cls: type[BaseStrategy], *args, **kwargs) -> None:
        self._strategy = strategy_cls(self.matching_engine, *args, **kwargs)

    def get_cash(self, client_id: UUID) -> Decimal:
        with self._lock:
            return self._cash[client_id]

    def add_cash(self, client_id: UUID, cash: Decimal) -> None:
        with self._lock:
            self._cash[client_id] += cash
            new_cash = self._cash[client_id]
        EventManager.push_event(
            CashflowEventDTO(
                simulation_id=self.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=CashflowEventType.DEPOSIT
                if cash > 0
                else CashflowEventType.WITHDRAW,
                amount=abs(cash),
                event_date=self.current_date,
            )
        )
        notify("cash_update", CashUpdateEventDTO(cash=new_cash).to_json(), to=client_id)

    def add_contribution(self, client_id: UUID, amount: Decimal) -> None:
        """Adiciona aporte mensal (não conta como retorno de investimento)"""
        with self._lock:
            self._cash[client_id] += amount
            new_cash = self._cash[client_id]
        EventManager.push_event(
            CashflowEventDTO(
                simulation_id=self.simulation_id,
                user_id=UserManager.get_user_id(client_id),
                event_type=CashflowEventType.CONTRIBUTION,
                amount=amount,
                event_date=self.current_date,
            )
        )
        notify("cash_update", CashUpdateEventDTO(cash=new_cash).to_json(), to=client_id)

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

    def get_portfolio(self, client_id: UUID) -> PortfolioDTO:
        with self._lock:
            equity = [
                PositionDTO.from_model(pos, self.get_current_price(pos))
                for pos in self.broker.get_positions(client_id).values()
                if pos.size > 0
            ]
            fixed = list(self.fixed_broker.get_fixed_positions(client_id).values())
            cash = self._cash[client_id]

        variable_income_value = sum((p.current_value for p in equity), Decimal(0))
        fixed_income_value = sum((p.current_value for p in fixed), Decimal(0))
        invested_value = variable_income_value + fixed_income_value
        total_networth = invested_value + cash

        # Aporte mensal é capital do jogador, não rendimento
        capital_provided = self.starting_cash + repository.user.get_total_contribution(
            UserManager.get_user_id(client_id)
        )

        return PortfolioDTO(
            starting_cash=self.starting_cash,
            cash=cash,
            total_networth=total_networth,
            invested_value=invested_value,
            variable_income_value=variable_income_value,
            fixed_income_value=fixed_income_value,
            invested_pct=ratio(invested_value, total_networth),
            variable_income_pct=ratio(variable_income_value, invested_value),
            fixed_income_pct=ratio(fixed_income_value, invested_value),
            total_return_pct=ratio(total_networth - capital_provided, capital_provided),
            variable_income=[
                PortfolioPositionDTO(
                    **pos.model_dump(),
                    portfolio_pct=ratio(pos.current_value, invested_value),
                )
                for pos in equity
            ],
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
                )
                for pos in fixed
            ],
        )

    def next(self, current_date: date) -> None:
        self.current_date = current_date

        self.fixed_income_market.refresh_assets(current_date)

        # Aplica juros dos ativos de renda fixa
        self.fixed_broker.apply_daily_interest(current_date)

        # Executa a estratégia
        if not self._strategy:
            raise RuntimeError("Nenhuma estratégia configurada")
        self._strategy.next()
