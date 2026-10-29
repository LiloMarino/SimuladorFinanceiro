"""
O banco de causas dos movimentos fortes: por setor e direção, frases que completam
"o mercado atribui a alta a ...". Setor sem lista própria usa as causas gerais.
"""

from backend.features.newsroom.text import pick

GENERAL_UP = (
    "resultado do trimestre acima do esperado",
    "anúncio de recompra de ações",
    "revisão para cima das projeções dos analistas",
    "notícias de um contrato importante",
)
GENERAL_DOWN = (
    "resultado do trimestre abaixo do esperado",
    "troca inesperada no comando da empresa",
    "revisão para baixo das projeções dos analistas",
    "dúvidas sobre a dívida da companhia",
)

# Setores como a classificação da B3 os nomeia
UP: dict[str, tuple[str, ...]] = {
    "Financeiro": (
        "lucro do trimestre acima do esperado",
        "queda da inadimplência na carteira de crédito",
        "expectativa de juros mais altos por mais tempo",
    ),
    "Petróleo, Gás e Biocombustíveis": (
        "alta do petróleo no mercado internacional",
        "aumento da produção no trimestre",
        "anúncio de dividendos extraordinários",
    ),
    "Materiais Básicos": (
        "alta do minério e das commodities no exterior",
        "demanda aquecida da China",
        "dólar mais forte, que favorece quem exporta",
    ),
    "Consumo Cíclico": (
        "vendas de fim de ano acima do esperado",
        "alta na confiança do consumidor",
        "crescimento das vendas nas mesmas lojas",
    ),
    "Consumo Não Cíclico": (
        "margens melhores no trimestre",
        "queda no custo das matérias-primas",
        "avanço das vendas em novos mercados",
    ),
    "Saúde": (
        "crescimento do número de pacientes atendidos",
        "reajuste de preços acima do esperado",
        "aquisição que amplia a rede da companhia",
    ),
    "Bens Industriais": (
        "carteira de pedidos recorde",
        "dólar mais forte nas exportações",
        "novos contratos de infraestrutura",
    ),
    "Utilidade Pública": (
        "reajuste de tarifa acima da inflação",
        "chuvas favoráveis nos reservatórios",
        "leilão vencido pela companhia",
    ),
    "Tecnologia da Informação": (
        "novos contratos com grandes clientes",
        "alta das ações de tecnologia no exterior",
        "crescimento da receita recorrente",
    ),
    "Comunicações": (
        "aumento da base de assinantes",
        "reajuste de preços dos planos",
        "venda de ativos acima do valor esperado",
    ),
    "Imobiliário": (
        "queda dos juros de longo prazo",
        "vendas de imóveis acima do esperado",
        "lançamentos bem recebidos pelo mercado",
    ),
}
DOWN: dict[str, tuple[str, ...]] = {
    "Financeiro": (
        "aumento da inadimplência na carteira de crédito",
        "lucro do trimestre abaixo do esperado",
        "temor com o aumento das provisões",
    ),
    "Petróleo, Gás e Biocombustíveis": (
        "queda do petróleo no mercado internacional",
        "incerteza sobre a política de preços dos combustíveis",
        "paralisação de uma plataforma de produção",
    ),
    "Materiais Básicos": (
        "queda do minério e das commodities no exterior",
        "sinais de desaceleração da China",
        "paralisação temporária de uma operação",
    ),
    "Consumo Cíclico": (
        "vendas de fim de ano fracas",
        "queda na confiança do consumidor",
        "estoques elevados e promoções que pesam na margem",
    ),
    "Consumo Não Cíclico": (
        "pressão do custo das matérias-primas",
        "perda de participação de mercado",
        "margens menores no trimestre",
    ),
    "Saúde": (
        "aumento dos custos com atendimentos",
        "reajuste de preços abaixo do esperado",
        "investigação sobre a operação de uma unidade",
    ),
    "Bens Industriais": (
        "cancelamento de pedidos importantes",
        "atraso na entrega de contratos",
        "aumento do custo de insumos",
    ),
    "Utilidade Pública": (
        "reajuste de tarifa abaixo do esperado",
        "chuvas abaixo da média nos reservatórios",
        "multa aplicada pelo regulador",
    ),
    "Tecnologia da Informação": (
        "perda de um grande cliente",
        "queda das ações de tecnologia no exterior",
        "desaceleração da receita recorrente",
    ),
    "Comunicações": (
        "perda de assinantes no trimestre",
        "guerra de preços entre as operadoras",
        "investimentos acima do previsto",
    ),
    "Imobiliário": (
        "alta dos juros de longo prazo",
        "distratos de vendas acima do esperado",
        "adiamento de lançamentos",
    ),
}


def cause_for(sector: str | None, rising: bool, *seed: object) -> str:
    """A causa sorteada para o movimento do setor na direção dada."""
    general, by_sector = (GENERAL_UP, UP) if rising else (GENERAL_DOWN, DOWN)
    options = (*by_sector.get(sector or "", ()), *general)
    return pick(options, *seed)
