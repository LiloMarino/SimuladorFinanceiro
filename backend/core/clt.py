"""As regras do CLT: o FGTS (a conta travada) e a hora extra, em Decimal e sem estado."""

from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.rates import compose, period_rate

CENT = Decimal("0.01")
MONTHS_PER_YEAR = 12

# Todo mês com salário pago, o empregador deposita esta fração do salário bruto na conta
FGTS_DEPOSIT_RATE = Decimal("0.08")
# Na demissão sem justa causa, a multa é esta fração do saldo e cai no caixa junto com ele
FGTS_FINE_RATE = Decimal("0.4")
# O saldo rende este juro ao ano mais a TR do mês
FGTS_ANNUAL_RATE = Decimal("0.03")
# Ligada, a hora extra soma esta fração à renda bruta
OVERTIME_INCOME_RATE = Decimal("0.25")
# Ligada, o imprevisto de saúde custa este múltiplo do valor
OVERTIME_HEALTH_MULTIPLE = Decimal(2)
# A hora extra só existe com o PIB de 12 meses a partir deste valor, em fração
OVERTIME_MIN_GROWTH = Decimal(0)


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)


def fgts_deposit(gross: Decimal) -> Decimal:
    """O depósito do mês sobre o salário bruto, com a hora extra."""
    return cents(gross * FGTS_DEPOSIT_RATE)


def fgts_yield(balance: Decimal, tr: Decimal) -> Decimal:
    """O rendimento do mês: o saldo vezes o juro anual de 3% levado a um mês, composto com a TR do mês (em fração)."""
    monthly = compose(period_rate(FGTS_ANNUAL_RATE, MONTHS_PER_YEAR), tr)
    return cents(balance * monthly)


def fgts_payout(balance: Decimal) -> Decimal:
    """O que cai no caixa na demissão: o saldo e a multa de 40% sobre ele."""
    return cents(balance * (1 + FGTS_FINE_RATE))
