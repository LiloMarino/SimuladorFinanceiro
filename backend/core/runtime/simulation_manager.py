from datetime import date
from threading import Lock

from flask import current_app

from backend.core.exceptions import NoActiveSimulationError
from backend.features.simulation.simulation import Simulation


class SimulationManager:
    """
    Ponto único de acesso à simulação ativa.
    Thread-safe para criação/limpeza.
    """

    _lock = Lock()

    @classmethod
    def get_active_simulation(cls) -> Simulation:
        """
        Retorna a simulação ativa ou lança NoActiveSimulation.
        """
        sim = current_app.config.get("simulation")
        if not sim:
            raise NoActiveSimulationError("Não existe simulação ativa no momento.")
        return sim

    @classmethod
    def create_simulation(cls, start_date: date, end_date: date) -> Simulation:
        """
        Cria uma nova simulação e salva no Flask current_app.config.
        Substitui qualquer simulação existente.
        """
        with cls._lock:
            sim = Simulation(start_date, end_date)
            current_app.config["simulation"] = sim
            return sim

    @classmethod
    def clear_simulation(cls) -> None:
        """
        Limpa a simulação ativa.
        """
        with cls._lock:
            if "simulation" in current_app.config:
                del current_app.config["simulation"]
