from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal

# O maior preço de uma compra automática de cota, em múltiplo do patrimônio por cota (P/VP)
MAX_PREMIUM = 1.2

# O prêmio da cota é duas vezes o desempenho sobre o CDI, limitado a esta fração do PL por cota
PREMIUM_LEVERAGE = 2
PREMIUM_LIMIT = 0.20


@dataclass(frozen=True)
class FundReference:
    """O que a estratégia e o runner sabem de uma cota de gestora listada, no pregão de hoje."""

    # O patrimônio líquido por cota do dia
    nav: float
    # O retorno da cota menos o do CDI na janela de pregões, em fração (0,03 é 3 pontos acima)
    performance: float
    # O preço da venda do emissor (oferta de abertura ou sobra da emissão); nulo sem venda aberta
    fixed_price: float | None
    # Se hoje é o último pregão da janela do preço fixo
    fixed_price_last_session: bool
    # O fechamento da cota na sessão anterior ao anúncio da emissão; nulo = sem ágio
    book_price: float | None = None

    @property
    def premium(self) -> float:
        """O ágio da cota: o preço da foto sobre o PL por cota do dia, menos 1 (0,10 é 10% de ágio)."""
        if self.book_price is None or self.nav <= 0:
            return 0.0
        return self.book_price / self.nav - 1


def price_ceiling(nav: float) -> float:
    """O preço máximo de compra automática da cota: `MAX_PREMIUM` vezes o patrimônio por cota."""
    return round(nav * MAX_PREMIUM, 2)


def performance_premium(performance: float) -> float:
    """O prêmio que o desempenho sobre o CDI dá à cota, em fração do PL por cota, entre -`PREMIUM_LIMIT` e +`PREMIUM_LIMIT`."""
    return max(-PREMIUM_LIMIT, min(PREMIUM_LIMIT, PREMIUM_LEVERAGE * performance))


def maker_attractiveness(fund: FundReference) -> float:
    """O quanto a cota atrai o Mercado na sobra da emissão: o maior entre o prêmio do desempenho e o ágio."""
    return max(performance_premium(fund.performance), fund.premium)


def maker_leftover(leftover: Decimal, attractiveness: float) -> Decimal:
    """As cotas da sobra que o Mercado compra: a fração `attractiveness / PREMIUM_LIMIT` dela, até a sobra inteira.

    Sem atratividade positiva o Mercado não compra.
    """
    if attractiveness <= 0 or leftover <= 0:
        return Decimal(0)
    share = Decimal(str(round(min(1.0, attractiveness / PREMIUM_LIMIT), 6)))
    return (leftover * share).to_integral_value(rounding=ROUND_FLOOR)
