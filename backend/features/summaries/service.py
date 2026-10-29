from collections.abc import Callable, Mapping
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.statistics_report import OverviewReportDTO
from backend.core.dto.summaries import SummaryDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import IndicatorSeries
from backend.core.indicators import last_known_value
from backend.features.realtime import notify
from backend.features.summaries.summary import (
    month_summary,
    position_results,
    ranking_move,
    year_review,
)

# Quanto antes do mês o último fechamento é procurado: cobre feriados e meses sem pregão do ativo
CLOSE_LOOKBACK = timedelta(days=31)


class SummaryDelivery:
    """
    Entrega a cada pessoa da partida o que ela tem a ler: na virada do mês o resumo do
    mês que fechou e, na virada do ano, a retrospectiva. Bot não lê, então não recebe.
    """

    def __init__(
        self,
        simulation_id: int,
        start_date: date,
        starting_cash: Decimal,
        ranking: Callable[[], OverviewReportDTO],
        names: Callable[[], Mapping[str, str]],
    ):
        self._simulation_id = simulation_id
        self._start_date = start_date
        self._starting_cash = starting_cash
        self._ranking = ranking
        self._names = names

    def on_month_turn(self, users: list[UserDTO], today: date) -> None:
        """Roda no 1º pregão do mês, com os snapshots do mês anterior já gravados."""
        month_end = today.replace(day=1) - timedelta(days=1)
        month = month_end.replace(day=1)
        people = [user for user in users if not user.is_bot]
        # O 1º pregão da partida também vira o mês, mas não há mês jogado para resumir
        if not people or month_end < self._start_date:
            return

        overview = self._ranking()
        positions = {p.player_nickname: p.position for p in overview.players}
        ibov = _ibov_change(month, month_end)
        for user in people:
            for entry in self._deliver(user, today, month, month_end, ibov, positions):
                notify("summary_delivered", entry.to_json(), to=user.client_id)

    def _deliver(
        self,
        user: UserDTO,
        today: date,
        month: date,
        month_end: date,
        ibov: Decimal | None,
        positions: Mapping[str, int],
    ) -> list[SummaryDTO]:
        store = repository.summaries
        history = store.history_between(self._simulation_id, user.id, month, month_end)
        position = positions.get(user.nickname)
        previous = store.last_month_summary(self._simulation_id, user.id)
        summary = month_summary(
            month,
            history,
            self._starting_cash,
            store.cashflow_totals(self._simulation_id, user.id, month, month_end),
            self._positions(user, month, month_end),
            ibov,
            ranking_move(position, len(positions), previous)
            if position is not None
            else None,
        )
        if summary is None:
            return []

        entries = [store.create(self._simulation_id, user.id, today, summary)]
        if today.month == 1:
            months = store.month_summaries(
                self._simulation_id, user.id, after=date(month.year, 1, 1)
            )
            if review := year_review(month.year, months):
                entries.append(
                    store.create(self._simulation_id, user.id, today, review)
                )
        return entries

    def _positions(self, user: UserDTO, month: date, month_end: date):
        events = repository.portfolio.get_equity_events(user.id)
        tickers = sorted({event.ticker for event in events})
        if not tickers:
            return []
        closes = repository.stock.get_closes_between(
            tickers, month - CLOSE_LOOKBACK, month_end, self._simulation_id
        )
        return position_results(
            events,
            month,
            month_end,
            _last_closes(closes, month - timedelta(days=1)),
            _last_closes(closes, month_end),
            self._names(),
        )


def _last_closes(
    closes: Mapping[str, Mapping[date, float]], on: date
) -> dict[str, Decimal]:
    """O último fechamento de cada ativo até `on`."""
    last = {}
    for ticker, by_day in closes.items():
        days = [day for day in by_day if day <= on]
        if days:
            last[ticker] = Decimal(str(by_day[max(days)]))
    return last


def _ibov_change(month: date, month_end: date) -> Decimal | None:
    before = last_known_value(IndicatorSeries.IBOV, month - timedelta(days=1))
    end = last_known_value(IndicatorSeries.IBOV, month_end)
    if not before or end is None:
        return None
    return end / before - 1
