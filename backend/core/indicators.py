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
from backend.core.utils import business_days_in_month

BUSINESS_DAYS_PER_YEAR = 252
IPCA_WINDOW_MONTHS = 12

# Indexadores que a renda fixa usa; a partida só nasce com os três cobertos
RATE_SERIES = (IndicatorSeries.CDI, IndicatorSeries.SELIC, IndicatorSeries.IPCA)

# Meta de inflação do CMN em cada ano; fora da tabela vale a última
INFLATION_TARGETS: dict[int, Decimal] = {
    2000: Decimal("6.0"),
    2001: Decimal("4.0"),
    2002: Decimal("3.5"),
    2003: Decimal("4.0"),
    2004: Decimal("5.5"),
    **dict.fromkeys(range(2005, 2019), Decimal("4.5")),
    2019: Decimal("4.25"),
    2020: Decimal("4.0"),
    2021: Decimal("3.75"),
    2022: Decimal("3.5"),
    2023: Decimal("3.25"),
    2024: Decimal("3.0"),
}
DEFAULT_TARGET = Decimal("3.0")

# Tolerância em pontos acima e abaixo da meta, em cada ano; fora da tabela vale a última
INFLATION_TOLERANCES: dict[int, Decimal] = {
    2000: Decimal("2.0"),
    2001: Decimal("2.0"),
    2002: Decimal("2.0"),
    2003: Decimal("2.5"),
    2004: Decimal("2.5"),
    **dict.fromkeys(range(2005, 2017), Decimal("2.0")),
}
DEFAULT_TOLERANCE = Decimal("1.5")


# Dívida bruta do governo geral no fim de cada ano, em % do PIB (BCB, SGS 13762)
GROSS_DEBT: dict[int, Decimal] = {
    2006: Decimal("55.48"),
    2007: Decimal("56.72"),
    2008: Decimal("55.98"),
    2009: Decimal("59.21"),
    2010: Decimal("51.77"),
    2011: Decimal("51.27"),
    2012: Decimal("53.67"),
    2013: Decimal("51.54"),
    2014: Decimal("56.28"),
    2015: Decimal("65.50"),
    2016: Decimal("69.84"),
    2017: Decimal("73.72"),
    2018: Decimal("75.27"),
    2019: Decimal("74.44"),
    2020: Decimal("86.94"),
    2021: Decimal("77.31"),
    2022: Decimal("71.68"),
    2023: Decimal("73.83"),
    2024: Decimal("76.27"),
    2025: Decimal("78.64"),
}

# Resultado primário do setor público consolidado no ano, em % do PIB; negativo é déficit (BCB, SGS 5793, que publica o déficit como positivo)
PRIMARY_RESULT: dict[int, Decimal] = {
    2002: Decimal("3.19"),
    2003: Decimal("3.24"),
    2004: Decimal("3.69"),
    2005: Decimal("3.74"),
    2006: Decimal("3.15"),
    2007: Decimal("3.24"),
    2008: Decimal("3.33"),
    2009: Decimal("1.94"),
    2010: Decimal("2.62"),
    2011: Decimal("2.94"),
    2012: Decimal("2.18"),
    2013: Decimal("1.71"),
    2014: Decimal("-0.56"),
    2015: Decimal("-1.86"),
    2016: Decimal("-2.48"),
    2017: Decimal("-1.68"),
    2018: Decimal("-1.55"),
    2019: Decimal("-0.84"),
    2020: Decimal("-9.24"),
    2021: Decimal("0.72"),
    2022: Decimal("1.25"),
    2023: Decimal("-2.28"),
    2024: Decimal("-0.40"),
    2025: Decimal("-0.43"),
}

# PIB nominal de cada ano, em R$ bilhões (IBGE, pelo BCB, SGS 4382)
NOMINAL_GDP: dict[int, Decimal] = {
    2000: Decimal("1199.1"),
    2001: Decimal("1315.8"),
    2002: Decimal("1488.8"),
    2003: Decimal("1718.0"),
    2004: Decimal("1957.8"),
    2005: Decimal("2170.6"),
    2006: Decimal("2409.4"),
    2007: Decimal("2720.3"),
    2008: Decimal("3109.8"),
    2009: Decimal("3333.0"),
    2010: Decimal("3885.8"),
    2011: Decimal("4376.4"),
    2012: Decimal("4814.8"),
    2013: Decimal("5331.6"),
    2014: Decimal("5779.0"),
    2015: Decimal("5995.8"),
    2016: Decimal("6269.3"),
    2017: Decimal("6585.5"),
    2018: Decimal("7004.1"),
    2019: Decimal("7389.1"),
    2020: Decimal("7609.6"),
    2021: Decimal("9012.1"),
    2022: Decimal("10079.7"),
    2023: Decimal("10943.3"),
    2024: Decimal("11779.3"),
    2025: Decimal("12738.6"),
}


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


def last_known_value(
    series: IndicatorSeries, on: date, *, stored: bool = False
) -> Decimal | None:
    """Último valor publicado até `on`: o que um investidor conhece naquele dia; com `stored`, o da série guardada."""
    history = repository.economic.get_history(series, stored=stored)
    if series is IndicatorSeries.IPCA:
        return history.last_known(on.replace(day=1))
    return history.last_known(on)


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
    return None if value is None else daily_rate(series, value, day)


def annualize_daily(value: Decimal) -> Decimal:
    """Taxa anual (0.149) de uma taxa diária em % (0.0551), composta por 252 dias úteis."""
    return (1 + value / 100) ** BUSINESS_DAYS_PER_YEAR - 1


def annual_index_rate(
    series: IndicatorSeries, on: date, *, stored: bool = False
) -> Decimal:
    """
    Taxa anual do indexador conhecida em `on` (0.149 = 14,9% a.a.); com `stored`, a da série guardada, sem o efeito das medidas do governo.

    CDI/SELIC: a taxa do dia composta por 252 dias úteis. IPCA: o acumulado dos
    últimos 12 meses.
    """
    if series is IndicatorSeries.IPCA:
        history = repository.economic.get_history(series, stored=stored)
        growth = Decimal(1)
        for value in history.values_until(on.replace(day=1), IPCA_WINDOW_MONTHS):
            growth *= 1 + value / 100
        return growth - 1

    value = last_known_value(series, on, stored=stored)
    if value is None:
        return Decimal(0)
    return annualize_daily(value)


def inflation_target(day: date) -> Decimal:
    if day.year in INFLATION_TARGETS:
        return INFLATION_TARGETS[day.year] / 100
    return DEFAULT_TARGET / 100


def inflation_tolerance(day: date) -> Decimal:
    """Folga da meta do ano, em fração: 0.015 vale 1,5 ponto para cima e para baixo."""
    return INFLATION_TOLERANCES.get(day.year, DEFAULT_TOLERANCE) / 100


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


def anniversaries(start: date, day: date) -> list[date]:
    """Os aniversários de `start` até `day`, inclusive; 29/02 vira 28/02 nos anos comuns."""
    result = []
    year = start.year + 1
    while True:
        try:
            anniversary = start.replace(year=year)
        except ValueError:
            anniversary = start.replace(year=year, day=28)
        if anniversary > day:
            return result
        result.append(anniversary)
        year += 1


def inflation_factor(start: date, day: date) -> Decimal:
    """
    Quanto os valores fixos em reais da partida subiram desde `start`: o IPCA de 12
    meses acumulado em cada aniversário. É o fator do salário, da despesa, da meta e
    dos preços das ações de campanha.
    """
    factor = Decimal(1)
    for anniversary in anniversaries(start, day):
        factor *= 1 + annual_index_rate(IndicatorSeries.IPCA, anniversary)
    return factor


def nearest_year_value(table: dict[int, Decimal], year: int) -> Decimal:
    """O valor da tabela anual no ano; fora dela vale o ano mais próximo dentro dela."""
    return table[min(table, key=lambda known: abs(known - year))]


def gross_debt_ratio(year: int) -> Decimal:
    """Dívida bruta do governo geral no fim do ano, em fração do PIB (0.698)."""
    return nearest_year_value(GROSS_DEBT, year) / 100


def primary_result_ratio(year: int) -> Decimal:
    """Resultado primário do ano, em fração do PIB por ano; negativo é déficit."""
    return nearest_year_value(PRIMARY_RESULT, year) / 100


def nominal_gdp(year: int) -> Decimal:
    """PIB nominal do ano, em reais."""
    return nearest_year_value(NOMINAL_GDP, year) * 1_000_000_000
