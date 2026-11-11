"""
Regras do viver de renda, puras: os imprevistos sorteados e o juro do cheque
especial. Renda, despesa e meta ficam no `LifeBudget`.

Os imprevistos vêm da lista de tipos das regras da partida (`life_events`): quem
sorteia recebe a lista, então um tipo novo é uma entrada nova nela. A frequência de
cada família (`life_frequencies`) escala a chance dos tipos dela; o sorteio do pregão,
o da demissão do mês e o do status leem a mesma lista e os mesmos níveis.
"""

import random
from collections.abc import Callable, Sequence
from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.life import LifeEventTypeDTO, LifeFrequenciesDTO
from backend.core.enum import LifeEventEffect
from backend.core.life_budget import cents
from backend.core.periods import BUSINESS_DAYS_PER_YEAR, MONTHS_PER_YEAR
from backend.core.rates import compound
from backend.core.utils import is_business_day, next_business_day
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT

# Todas as famílias em Normal: a frequência geral vale como escrita
NORMAL_FREQUENCIES = LifeFrequenciesDTO()


def layoff_factor_of(unemployment: Decimal) -> float:
    """
    Quantas vezes a chance de demissão do neutro: o desemprego da partida sobre o
    neutro. Com 18% de desemprego é o dobro; com 4%, menos da metade.
    """
    return float(unemployment / NEUTRAL_UNEMPLOYMENT)


def neutral_layoff_factor(day: date) -> float:
    return 1.0


def unexpected_on(
    seed: int,
    day: date,
    per_year: int,
    events: Sequence[LifeEventTypeDTO],
    layoff_factor: float = 1.0,
    frequencies: LifeFrequenciesDTO = NORMAL_FREQUENCIES,
) -> LifeEventTypeDTO | None:
    """
    O imprevisto do pregão `day`, ou None. O gerador nasce da semente da partida e
    do dia: todos os jogadores recebem o mesmo, e a retomada sorteia igual.
    A chance de um tipo por pregão é `per_year / 252` na fatia do seu peso entre os
    tipos ligados, vezes o multiplicador da família dele; a da demissão, vezes também
    `layoff_factor`. A fatia não depende do multiplicador: família em Frequente não
    tira chance das outras.
    """
    # A fatia da demissão (a que cresce com o desemprego) é a última: os outros tipos
    # mantêm o dia e o tipo sorteados quando só o desemprego muda
    events = sorted(
        (event for event in events if event.enabled),
        key=lambda event: event.effect is LifeEventEffect.SKIP_NEXT_SALARY,
    )
    if per_year <= 0 or not events:
        return None
    draw = random.Random(f"{seed}:{day.isoformat()}").random()
    per_weight = per_year / BUSINESS_DAYS_PER_YEAR / sum(e.weight for e in events)
    threshold = 0.0
    for event in events:
        factor = (
            layoff_factor if event.effect is LifeEventEffect.SKIP_NEXT_SALARY else 1
        )
        multiplier = frequencies.of(event.family).multiplier
        threshold += per_weight * event.weight * factor * multiplier
        if draw < threshold:
            return event
    return None


def layoff_in(
    seed: int,
    month: date,
    per_year: int,
    start_date: date,
    events: Sequence[LifeEventTypeDTO],
    until: date | None = None,
    layoff_factor_on: Callable[[date], float] = neutral_layoff_factor,
    frequencies: LifeFrequenciesDTO = NORMAL_FREQUENCIES,
) -> date | None:
    """O pregão do mês de `month` (a partir do início da partida e até `until`) em que saiu uma demissão."""
    first = month.replace(day=1)
    day = max(first, start_date)
    day = day if is_business_day(day) else next_business_day(day)
    while (day.year, day.month) == (first.year, first.month) and (
        until is None or day <= until
    ):
        event = unexpected_on(
            seed, day, per_year, events, layoff_factor_on(day), frequencies
        )
        if event is not None and event.effect is LifeEventEffect.SKIP_NEXT_SALARY:
            return day
        day = next_business_day(day)
    return None


def salary_skipped(
    seed: int,
    month: date,
    per_year: int,
    start_date: date,
    events: Sequence[LifeEventTypeDTO],
    layoff_factor_on: Callable[[date], float] = neutral_layoff_factor,
    frequencies: LifeFrequenciesDTO = NORMAL_FREQUENCIES,
) -> bool:
    """O salário de `month` não entra quando saiu uma demissão em algum pregão do mês anterior."""
    previous = month.replace(day=1) - timedelta(days=1)
    return (
        layoff_in(
            seed,
            previous,
            per_year,
            start_date,
            events=events,
            layoff_factor_on=layoff_factor_on,
            frequencies=frequencies,
        )
        is not None
    )


def overdraft_interest(cash: Decimal, monthly_rate: Decimal) -> Decimal:
    """Juro de um pregão sobre o caixa negativo; a taxa mensal vira diária na base de 252 pregões."""
    if cash >= 0:
        return Decimal(0)
    daily = compound(monthly_rate, Decimal(MONTHS_PER_YEAR) / BUSINESS_DAYS_PER_YEAR)
    return cents(-cash * daily)
