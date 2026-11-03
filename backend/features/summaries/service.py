from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import last_known_value
from backend.features.realtime import notify
from backend.features.summaries.summary import year_review


class SummaryDelivery:
    """
    Entrega a cada pessoa da partida o que ela tem a ler: na virada do ano, a
    retrospectiva do ano que fechou. Bot não lê, então não recebe.
    """

    def __init__(self, simulation_id: int, start_date: date, starting_cash: Decimal):
        self._simulation_id = simulation_id
        self._start_date = start_date
        self._starting_cash = starting_cash

    def on_year_turn(self, users: list[UserDTO], today: date) -> None:
        """Roda no 1º pregão do ano, com os snapshots do ano anterior já gravados."""
        year_end = today.replace(month=1, day=1) - timedelta(days=1)
        year_start = year_end.replace(month=1, day=1)
        people = [user for user in users if not user.is_bot]
        # O 1º pregão da partida também vira o ano, mas não há ano jogado para rever
        if not people or year_end < self._start_date:
            return

        ibov = _ibov_change(year_start, year_end)
        for user in people:
            history = repository.summaries.history_between(
                self._simulation_id, user.id, year_start, year_end
            )
            review = year_review(year_end.year, history, self._starting_cash, ibov)
            if review is None:
                continue
            entry = repository.summaries.create(
                self._simulation_id, user.id, today, review
            )
            notify("summary_delivered", entry.to_json(), to=user.client_id)


def _ibov_change(start: date, end_date: date) -> Decimal | None:
    before = last_known_value(IndicatorSeries.IBOV, start - timedelta(days=1))
    end = last_known_value(IndicatorSeries.IBOV, end_date)
    if not before or end is None:
        return None
    return end / before - 1
