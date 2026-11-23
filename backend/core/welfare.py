"""
As regras do Auxílio: o depósito do Pé-de-Meia, as datas de liberação e o curso técnico,
em Decimal e sem estado.
"""

from datetime import date
from decimal import Decimal

from backend.core.clt import MONTHS_PER_YEAR, cents
from backend.core.dates import add_months
from backend.core.professions import REFERENCE_WELFARE_SPENDING

# O governo deposita esta fração da sobra do mês no Pé-de-Meia, até esta fração da renda líquida do mês
DEPOSIT_RATE = Decimal("0.2")
DEPOSIT_CAP_RATE = Decimal("0.1")

# O gasto do governo com auxílio escala o depósito pelo gasto de hoje sobre o de referência, entre estes limites
SPENDING_FACTOR_MIN = Decimal("0.5")
SPENDING_FACTOR_MAX = Decimal(2)

# O saldo tem uma data de liberação a cada tantos meses, contados do início da partida
RELEASE_MONTHS = 2 * MONTHS_PER_YEAR

# O curso técnico dura tantos meses e, enquanto dura, a renda do bico vale esta fração
COURSE_MONTHS = 12
COURSE_INCOME_FACTOR = Decimal("0.5")

# Política dos bots: o curso só compensa na partida com pelo menos esta duração, em anos
BOT_COURSE_MIN_YEARS = 10


def spending_factor(welfare_spending: Decimal) -> Decimal:
    """O quanto o gasto com auxílio de hoje escala o depósito: o gasto sobre o de referência, de meio a dobro."""
    ratio = welfare_spending / REFERENCE_WELFARE_SPENDING
    return min(max(ratio, SPENDING_FACTOR_MIN), SPENDING_FACTOR_MAX)


def deposit_rate(factor: Decimal) -> Decimal:
    """A fração da sobra que o governo deposita, com o fator do gasto."""
    return DEPOSIT_RATE * factor


def deposit_cap(net_income: Decimal, factor: Decimal) -> Decimal:
    """O teto do depósito: a fração da renda líquida do mês, com o fator do gasto."""
    return cents(net_income * DEPOSIT_CAP_RATE * factor)


def deposit_amount(surplus: Decimal, net_income: Decimal, factor: Decimal) -> Decimal:
    """O depósito do mês: a fração da sobra limitada ao teto; sobra zero ou negativa não deposita."""
    if surplus <= 0:
        return Decimal(0)
    return min(cents(surplus * deposit_rate(factor)), deposit_cap(net_income, factor))


def releases_reached(start: date, day: date) -> int:
    """Quantas datas de liberação já chegaram em `day`: uma a cada 2 anos a partir de `start`."""
    count = 0
    while add_months(start, RELEASE_MONTHS * (count + 1)) <= day:
        count += 1
    return count


def next_release_on(start: date, reached: int) -> date:
    """A data da liberação seguinte, depois das `reached` que já chegaram."""
    return add_months(start, RELEASE_MONTHS * (reached + 1))


def course_months_done(enrolled_on: date, day: date) -> int:
    """Os meses do curso que passaram em `day`, pela virada do calendário, de 0 até a duração do curso."""
    months = (
        (day.year - enrolled_on.year) * MONTHS_PER_YEAR + day.month - enrolled_on.month
    )
    return min(max(months, 0), COURSE_MONTHS)


def course_ends_on(enrolled_on: date) -> date:
    """O dia em que os meses do curso fecham."""
    return add_months(enrolled_on, COURSE_MONTHS)


def course_concluded(enrolled_on: date, day: date) -> bool:
    """O curso conclui na virada do mês em que os meses fecham: o mesmo mês do calendário, daqui a `COURSE_MONTHS`."""
    return course_months_done(enrolled_on, day) >= COURSE_MONTHS
