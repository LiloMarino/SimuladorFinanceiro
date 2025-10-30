from datetime import datetime

from flask import current_app

from backend.simulation.simulation import Simulation


def get_simulation() -> Simulation:
    if "simulation" not in current_app.config:
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2026, 8, 18)
        current_app.config["simulation"] = Simulation(from_date, to_date)
    return current_app.config["simulation"]
