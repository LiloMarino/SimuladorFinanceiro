"""
Calendário das eleições: o 1º turno da primeira cai na data escolhida nas regras e as
seguintes a cada 4 anos. Data que não é dia útil passa para o dia útil seguinte.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from backend.core.utils import is_business_day, next_business_day

TERM_YEARS = 4
CAMPAIGN_YEARS = 1
# Entre o 1º e o 2º turno: 3 semanas (07 e 28 de out)
RUNOFF_DAYS = 21


@dataclass(frozen=True)
class ElectionCycle:
    """As datas de uma eleição: da abertura da campanha à posse."""

    index: int
    campaign_start: date
    ticket_deadline: date
    first_round: date
    runoff: date
    inauguration: date

    @property
    def donation_deadline(self) -> date:
        """Último dia para doar entre os turnos: a véspera do 2º turno."""
        return self.runoff - timedelta(days=1)


def election_cycle(first_election: date, index: int, start_date: date) -> ElectionCycle:
    first_round = _on_or_after_business_day(
        _add_years(first_election, TERM_YEARS * index)
    )
    runoff = _on_or_after_business_day(first_round + timedelta(days=RUNOFF_DAYS))
    campaign_start = max(_add_years(first_round, -CAMPAIGN_YEARS), start_date)
    # A inscrição das chapas fecha no último dia do mês anterior ao do 1º turno
    ticket_deadline = first_round.replace(day=1) - timedelta(days=1)
    return ElectionCycle(
        index=index,
        campaign_start=campaign_start,
        ticket_deadline=ticket_deadline,
        first_round=first_round,
        runoff=runoff,
        inauguration=date(first_round.year + 1, 1, 1),
    )


def _on_or_after_business_day(day: date) -> date:
    return day if is_business_day(day) else next_business_day(day)


def _add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        # 29 de fevereiro num ano sem ele
        return day.replace(year=day.year + years, day=28)
