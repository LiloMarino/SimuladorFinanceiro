"""
As regras da previdência do Aposentado: o saldo inicial, o rendimento, o juro real, a
renda vitalícia e o IR regressivo do resgate, em Decimal e sem estado.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backend.core.clt import MONTHS_PER_YEAR, cents
from backend.core.dates import add_months
from backend.core.rates import period_rate

# O saldo de quem entra na profissão são 24 rendas do mês
OPENING_MONTHS = 24

# O plano rende o CDI menos esta taxa de administração ao ano
ADMIN_FEE = Decimal("0.01")

# Política dos bots: converte metade do saldo, uma vez, quando o juro real passa de 6% ao ano
BOT_CONVERT_SHARE = Decimal("0.5")
BOT_CONVERT_MIN_REAL_RATE = Decimal("0.06")


@dataclass(frozen=True)
class RedeemBracket:
    """Uma faixa do IR regressivo: a alíquota vale a partir de `from_months` no plano."""

    from_months: int
    rate: Decimal
    label: str


# A tabela do IR regressivo do resgate pelo tempo no plano; a faixa começa no mês em que o
# tempo no plano alcança `from_months` e vai até a faixa seguinte
REDEEM_BRACKETS: tuple[RedeemBracket, ...] = (
    RedeemBracket(0, Decimal("0.35"), "até 2 anos"),
    RedeemBracket(24, Decimal("0.30"), "2 a 4 anos"),
    RedeemBracket(48, Decimal("0.25"), "4 a 6 anos"),
    RedeemBracket(72, Decimal("0.20"), "6 a 8 anos"),
    RedeemBracket(96, Decimal("0.15"), "8 a 10 anos"),
    RedeemBracket(120, Decimal("0.10"), "mais de 10 anos"),
)

# A partir daqui o resgate paga a menor alíquota da tabela
LOWEST_RATE_MONTHS = REDEEM_BRACKETS[-1].from_months


def opening_balance(monthly_income: Decimal) -> Decimal:
    """O saldo de quem entra: `OPENING_MONTHS` rendas do mês."""
    return cents(monthly_income * OPENING_MONTHS)


def annual_yield(cdi: Decimal) -> Decimal:
    """A taxa anual do plano: o CDI do dia menos a taxa de administração."""
    return cdi - ADMIN_FEE


def monthly_yield_rate(cdi: Decimal) -> Decimal:
    """A taxa do mês do plano: a taxa anual levada a um mês."""
    return period_rate(annual_yield(cdi), MONTHS_PER_YEAR)


def balance_after_month(balance: Decimal, cdi: Decimal) -> Decimal:
    """O saldo depois do pagamento do mês, com o rendimento do plano sem IR."""
    return cents(balance * (1 + monthly_yield_rate(cdi)))


def real_rate(selic: Decimal, expected_ipca: Decimal) -> Decimal:
    """O juro real ao ano: quanto a SELIC rende acima do IPCA esperado, (1 + SELIC) ÷ (1 + IPCA) - 1."""
    return (1 + selic) / (1 + expected_ipca) - 1


def income_rate(rate: Decimal) -> Decimal:
    """A fração do valor convertido que vira renda a cada mês: o juro real ao ano levado a um mês."""
    return period_rate(rate, MONTHS_PER_YEAR)


def converted_income(amount: Decimal, rate: Decimal) -> Decimal:
    """A renda mensal que `amount` convertido rende para sempre ao juro real `rate`."""
    return cents(amount * income_rate(rate))


def amount_valid(amount: Decimal, balance: Decimal) -> bool:
    """O valor de converter ou resgatar vai de R$ 0,01 até o saldo, em centavos."""
    return Decimal("0.01") <= amount <= balance and amount == cents(amount)


def months_in_plan(since: date, day: date) -> int:
    """Os meses completos que o saldo está no plano em `day`."""
    months = (day.year - since.year) * MONTHS_PER_YEAR + day.month - since.month
    if add_months(since, months) > day:
        months -= 1
    return max(months, 0)


def redeem_bracket(months: int) -> RedeemBracket:
    """A faixa da tabela que o tempo no plano `months` alcança."""
    return max(
        (bracket for bracket in REDEEM_BRACKETS if bracket.from_months <= months),
        key=lambda bracket: bracket.from_months,
    )


def redeem_rate(months: int) -> Decimal:
    """A alíquota do IR do resgate com `months` meses no plano."""
    return redeem_bracket(months).rate


def next_bracket(months: int) -> RedeemBracket | None:
    """A faixa seguinte da tabela, de alíquota menor; nulo na última."""
    later = [b for b in REDEEM_BRACKETS if b.from_months > months]
    return min(later, key=lambda bracket: bracket.from_months, default=None)


def redeem_net(amount: Decimal, months: int) -> Decimal:
    """O que cai no caixa com o resgate de `amount` depois do IR da faixa, aplicado sobre o valor inteiro."""
    return amount - redeem_tax(amount, months)


def redeem_tax(amount: Decimal, months: int) -> Decimal:
    """O IR do resgate de `amount`, em centavos."""
    return cents(amount * redeem_rate(months))
