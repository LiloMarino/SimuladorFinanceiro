from __future__ import annotations

from threading import Lock
from typing import TYPE_CHECKING, ClassVar

from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import NotFoundError

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation


class SimulationManager:
    """
    Gerenciador singleton do lifecycle da simulação ativa.

    Responsável por:
    - Registrar e manter referência à simulação em execução
    - Fornecer acesso thread-safe à simulação e ao simulation_id

    O backtest roda no mesmo motor, e por isso é a simulação registrada; para a sala
    ele não é partida: `has_active_simulation` responde só pela partida de jogadores,
    e `has_running_simulation` pelo motor ocupado, com partida ou backtest.
    """

    _lock = Lock()
    _active_simulation: Simulation | None = None
    _simulation_id: int | None = None
    _backtest = False
    # user_id -> portfolio_id das carteiras da partida em `_simulation_id`
    _portfolios: ClassVar[dict[int, int]] = {}

    @classmethod
    def register_simulation(cls, sim: Simulation, *, backtest: bool = False) -> None:
        with cls._lock:
            if cls._simulation_id != sim.settings.id:
                cls._portfolios = {}
            cls._active_simulation = sim
            cls._simulation_id = sim.settings.id
            cls._backtest = backtest

    @classmethod
    def get_active_simulation(cls) -> Simulation:
        sim = cls._active_simulation
        if not sim:
            raise NoActiveSimulationError()
        return sim

    @classmethod
    def has_active_simulation(cls) -> bool:
        """Há uma partida de jogadores em andamento."""
        return cls._active_simulation is not None and not cls._backtest

    @classmethod
    def has_backtest(cls) -> bool:
        return cls._active_simulation is not None and cls._backtest

    @classmethod
    def has_running_simulation(cls) -> bool:
        """O motor está ocupado, com partida ou com backtest."""
        return cls._active_simulation is not None

    @classmethod
    def find_active_simulation_id(cls) -> int | None:
        """O id da partida ativa, ou None sem partida: o caminho quente das leituras."""
        return cls._simulation_id

    @classmethod
    def get_active_simulation_id(cls) -> int:
        with cls._lock:
            if cls._simulation_id is None:
                raise NoActiveSimulationError()
            return cls._simulation_id

    @classmethod
    def get_portfolio_id(cls, user_id: int) -> int:
        """A carteira do jogador na partida ativa."""
        portfolio_id = cls._portfolios.get(user_id)
        if portfolio_id is None:
            raise NotFoundError(f"Carteira não encontrada para user_id={user_id}")
        return portfolio_id

    @classmethod
    def add_portfolios(cls, portfolios: dict[int, int]) -> None:
        """Soma carteiras abertas com a partida em andamento (user_id -> portfolio_id)."""
        with cls._lock:
            cls._portfolios = {**cls._portfolios, **portfolios}

    @classmethod
    def set_simulation_id(
        cls, simulation_id: int, portfolios: dict[int, int] | None = None
    ) -> None:
        """Fixa a partida ativa com as carteiras dela; o mapa de outra partida não sobrevive."""
        with cls._lock:
            cls._simulation_id = simulation_id
            cls._portfolios = dict(portfolios or {})

    @classmethod
    def clear_simulation(cls) -> None:
        with cls._lock:
            cls._active_simulation = None
            cls._simulation_id = None
            cls._portfolios = {}
            cls._backtest = False
