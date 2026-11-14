from datetime import date

from backend.core.utils import next_business_day


def window_end(start: date, sessions: int) -> date:
    """O último pregão de uma janela de `sessions` pregões que abre em `start`, contando o dia dele."""
    day = start
    for _ in range(sessions - 1):
        day = next_business_day(day)
    return day


def window_session(start: date, today: date, sessions: int) -> int:
    """O pregão da janela em `today`: 1 no dia de `start`, até `sessions`."""
    session = 1
    day = start
    while day < today and session < sessions:
        day = next_business_day(day)
        session += 1
    return session
