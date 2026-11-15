"""As contas da partida na oferta de privatização: o caixa e a posição de cada carteira."""

from collections.abc import Callable
from decimal import Decimal
from uuid import UUID

from backend.features.simulation.simulation_engine import SimulationEngine


class EngineOfferAccounts:
    """
    A oferta lê e move o caixa pela carteira. `resolve` leva a carteira à conta que a
    opera, e é None quando a carteira não tem conta na partida: ela fica sem caixa.
    """

    def __init__(
        self,
        engine: SimulationEngine,
        resolve: Callable[[int], UUID | None],
    ) -> None:
        self._engine = engine
        self._resolve = resolve

    def cash(self, portfolio_id: int) -> Decimal:
        client_id = self._resolve(portfolio_id)
        return Decimal(0) if client_id is None else self._engine.get_cash(client_id)

    def deliver(
        self, portfolio_id: int, ticker: str, shares: int, price: Decimal
    ) -> None:
        client_id = self._resolve(portfolio_id)
        if client_id is not None:
            self._engine.broker.buy_from_fund(client_id, ticker, Decimal(shares), price)
