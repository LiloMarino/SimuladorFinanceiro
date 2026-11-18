from dataclasses import dataclass

# O maior preço de uma compra automática de cota, em múltiplo do patrimônio por cota (P/VP)
MAX_PREMIUM = 1.2


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


def price_ceiling(nav: float) -> float:
    """O preço máximo de compra automática da cota: `MAX_PREMIUM` vezes o patrimônio por cota."""
    return round(nav * MAX_PREMIUM, 2)
