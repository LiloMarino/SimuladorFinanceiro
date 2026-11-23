"""As regras do Exportador: o dólar do câmbio futuro, o calendário do mix e as constantes da política dos bots, em Decimal e sem estado."""

from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.dates import add_months, quarter_start

MONTHS_PER_YEAR = 12

# Os prazos que o câmbio futuro aceita, em meses
LOCK_TERMS_MONTHS = (6, 12)
# A fração da receita exportada que a trava cobre
MIN_LOCK_SHARE = Decimal("0.01")
MAX_LOCK_SHARE = Decimal(1)
# O dólar travado e a fração do mix andam em passos fixos
DOLLAR_STEP = Decimal("0.0001")
SHARE_STEP = Decimal("0.01")
# O mix muda no máximo uma vez a cada trimestre do calendário
MIX_CHANGE_QUARTER_MONTHS = 3

# Política dos bots: a trava cobre metade da receita exportada por 12 meses, quando o
# dólar do dia está acima da média dos dólares de virada de mês dos últimos 12 meses
BOT_LOCK_SHARE = Decimal("0.5")
BOT_LOCK_MONTHS = 12
BOT_DOLLAR_AVERAGE_MONTHS = 12
# O mix do bot parte de 50/50 e pende para 70/30 ou 30/70 pelo indicador acima do neutro
BOT_MIX_BALANCED = Decimal("0.5")
BOT_MIX_DOLLAR_LEAN = Decimal("0.7")
BOT_MIX_GDP_LEAN = Decimal("0.3")


def forward_dollar(
    spot: Decimal, cdi: Decimal, fed_funds: Decimal, months: int
) -> Decimal:
    """
    O dólar do câmbio futuro: o do dia vezes ((1 + CDI) / (1 + Fed Funds)) elevado a
    meses/12, com os juros ao ano em fração; arredondado ao centésimo de centavo.
    """
    ratio = (1 + cdi) / (1 + fed_funds)
    exponent = Decimal(months) / MONTHS_PER_YEAR
    return (spot * ratio**exponent).quantize(DOLLAR_STEP, rounding=ROUND_HALF_EVEN)


def next_quarter_start(day: date) -> date:
    """O 1º dia do trimestre do calendário seguinte ao de `day`."""
    return add_months(quarter_start(day), MIX_CHANGE_QUARTER_MONTHS)
