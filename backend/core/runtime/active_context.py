from threading import Lock

from backend.core.exceptions import NoActiveSimulationError


class ActiveContext:
    _lock = Lock()
    _simulation_id: int | None = None

    @classmethod
    def set_active_simulation_id(cls, simulation_id: int | None) -> None:
        with cls._lock:
            cls._simulation_id = simulation_id

    @classmethod
    def get_active_simulation_id(cls) -> int:
        with cls._lock:
            if cls._simulation_id is None:
                raise NoActiveSimulationError()
            return cls._simulation_id
