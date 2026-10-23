"""
Taxas dos indexadores (CDI, SELIC, IPCA) lidas das séries históricas.

As séries guardam o valor como o Banco Central publica: CDI e SELIC em % ao dia,
um valor por dia útil; IPCA em % ao mês, um valor por mês (datado no dia 1).
"""

from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.enum import IndicatorSeries
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.repository.series_version import reading_version
from backend.core.utils import business_days_in_month
from backend.features.government.economy import macro_effect, state_on

BUSINESS_DAYS_PER_YEAR = 252
IPCA_WINDOW_MONTHS = 12

# Indexadores que a renda fixa usa; a partida só nasce com os três cobertos
RATE_SERIES = (IndicatorSeries.CDI, IndicatorSeries.SELIC, IndicatorSeries.IPCA)


def index_value_on(series: IndicatorSeries, day: date) -> Decimal | None:
    """
    Valor publicado que vale para o dia útil `day`.

    Dentro da série, um dia sem valor de CDI/SELIC é dia sem pregão (feriado) e
    devolve None. Depois do fim da série vale o último valor conhecido, como no
    preço das ações. O IPCA vale para todos os dias do mês.
    """
    history = repository.economic.get_history(series)
    if series is IndicatorSeries.IPCA:
        return history.last_known(day.replace(day=1))
    if history.end is not None and day <= history.end:
        return history.value_on(day)
    return history.last_known(day)


def last_known_value(series: IndicatorSeries, on: date) -> Decimal | None:
    """Último valor publicado até `on`: o que um investidor conhece naquele dia."""
    history = repository.economic.get_history(series)
    if series is IndicatorSeries.IPCA:
        return history.last_known(on.replace(day=1))
    value = history.last_known(on)
    if series is IndicatorSeries.IBOV and value is not None:
        effect = macro_effect(state_on(reading_version(), on), on)
        return value * Decimal(str(max(0.1, 1 - 2.9 * effect.selic)))
    return value


def daily_rate(series: IndicatorSeries, value: Decimal, day: date) -> Decimal:
    """
    Fração que `value` rende num dia útil: CDI/SELIC já são diários; o IPCA do
    mês se distribui pelos dias úteis do mês, que juntos fecham a taxa mensal.
    """
    if series is IndicatorSeries.IPCA:
        days = business_days_in_month(day)
        return (1 + value / 100) ** (Decimal(1) / days) - 1
    return value / 100


def index_daily_rate(series: IndicatorSeries, day: date) -> Decimal | None:
    """Fração que o indexador rende no dia útil `day`; None em dia sem pregão."""
    value = index_value_on(series, day)
    if value is None:
        return None
    base = daily_rate(series, value, day)
    state = state_on(reading_version(), day)
    if state is None:
        return base
    effect = macro_effect(state, day)
    if series is IndicatorSeries.IPCA:
        if effect.inflation == 0:
            return base
        annual = raw_annual_index_rate(series, day)
        ratio = (1 + annual + Decimal(str(effect.inflation))) / (1 + annual)
        return (1 + base) * max(Decimal("0.01"), ratio) ** (Decimal(1) / 252) - 1
    if state and state.rules.manual_selic:
        decisions = [d for d in state.selic_decisions if d.on <= day]
        if decisions:
            # A mesma meta remunera SELIC e CDI no modelo simplificado.
            return (1 + Decimal(str(decisions[-1].rate))) ** (Decimal(1) / 252) - 1
    annual = (1 + base) ** 252 - 1 + Decimal(str(effect.selic))
    return (1 + max(Decimal(0), annual)) ** (Decimal(1) / 252) - 1


def raw_annual_index_rate(series: IndicatorSeries, on: date) -> Decimal:
    """
    Taxa anual do indexador conhecida em `on` (0.149 = 14,9% a.a.).

    CDI/SELIC: a taxa do dia composta por 252 dias úteis. IPCA: o acumulado dos
    últimos 12 meses.
    """
    if series is IndicatorSeries.IPCA:
        history = repository.economic.get_history(series)
        growth = Decimal(1)
        for value in history.values_until(on.replace(day=1), IPCA_WINDOW_MONTHS):
            growth *= 1 + value / 100
        return growth - 1

    value = last_known_value(series, on)
    if value is None:
        return Decimal(0)
    return (1 + value / 100) ** BUSINESS_DAYS_PER_YEAR - 1


def annual_index_rate(series: IndicatorSeries, on: date) -> Decimal:
    base = raw_annual_index_rate(series, on)
    state = state_on(reading_version(), on)
    if not state:
        return base
    effect = macro_effect(state, on)
    if series is IndicatorSeries.IPCA:
        return base + Decimal(str(effect.inflation))
    decisions = [d for d in state.selic_decisions if d.on <= on]
    if state.rules.manual_selic and decisions:
        return Decimal(str(decisions[-1].rate))
    return max(Decimal(0), base + Decimal(str(effect.selic)))


def ensure_indicator_coverage(start_date: date) -> None:
    """A partida só começa num dia que CDI, SELIC e IPCA já cobrem com dado real."""
    missing = [
        series.value
        for series in RATE_SERIES
        if last_known_value(series, start_date) is None
    ]

    if missing:
        raise ConflictError(
            f"Sem dado de {', '.join(missing)} em {start_date:%d/%m/%Y}. "
            "Atualize os indicadores na Central de dados ou escolha outra data inicial."
        )
