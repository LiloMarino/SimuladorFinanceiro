"""
O catálogo de conquistas. Uma conquista é uma linha: aponta para uma métrica
(`metrics.py`) e diz a meta que a desbloqueia. Com `unit`, mostra a barra de
progresso (atual de meta); sem ele, a conquista é de tudo ou nada.

Acrescentar uma conquista é acrescentar uma linha aqui; se a medida não existe,
uma função `@metric` nova em `metrics.py`. O `code` é a chave gravada no banco e
nunca muda; nome, descrição, ícone e categoria podem mudar quando quiser.
"""

from dataclasses import dataclass
from decimal import Decimal

from backend.core.enum import AchievementCategory, AchievementIcon, AchievementUnit

Category = AchievementCategory
Icon = AchievementIcon
Unit = AchievementUnit


@dataclass(frozen=True)
class Achievement:
    code: str
    name: str
    description: str
    icon: AchievementIcon
    category: AchievementCategory
    metric: str
    goal: Decimal = Decimal(1)
    unit: AchievementUnit | None = None
    secret: bool = False


CATALOG: tuple[Achievement, ...] = (
    # Primeiros passos
    Achievement(
        "first_buy",
        "Primeira compra",
        "Comprou a primeira ação.",
        Icon.SHOPPING_CART,
        Category.FIRST_STEPS,
        "equity_buys",
    ),
    Achievement(
        "first_fixed_income",
        "Renda fixa também conta",
        "Investiu pela primeira vez num título de renda fixa.",
        Icon.LANDMARK,
        Category.FIRST_STEPS,
        "fixed_income_buys",
    ),
    Achievement(
        "first_sale",
        "Primeira venda",
        "Vendeu uma ação.",
        Icon.HAND_COINS,
        Category.FIRST_STEPS,
        "equity_sells",
    ),
    Achievement(
        "hands_on",
        "Mão na massa",
        "Deu 100 ordens numa partida.",
        Icon.HAMMER,
        Category.FIRST_STEPS,
        "order_count",
        Decimal(100),
        Unit.COUNT,
    ),
    Achievement(
        "first_candle_read",
        "Primeira leitura",
        "Acertou um desafio da vela.",
        Icon.CHART_CANDLESTICK,
        Category.FIRST_STEPS,
        "candle_challenge_hits",
    ),
    # Patrimônio
    Achievement(
        "doubled_capital",
        "Dobrou a aposta",
        "Dobrou o dinheiro que colocou numa partida.",
        Icon.TRENDING_UP,
        Category.WEALTH,
        "capital_multiple",
        Decimal(2),
    ),
    Achievement(
        "networth_100k",
        "Primeiros R$ 100 mil",
        "Chegou a R$ 100.000 de patrimônio.",
        Icon.PIGGY_BANK,
        Category.WEALTH,
        "networth",
        Decimal(100_000),
        Unit.BRL,
    ),
    Achievement(
        "networth_1m",
        "Primeiro milhão",
        "Chegou a R$ 1.000.000 de patrimônio.",
        Icon.GEM,
        Category.WEALTH,
        "networth",
        Decimal(1_000_000),
        Unit.BRL,
    ),
    Achievement(
        "networth_1b",
        "Primeiro bilhão",
        "Chegou a R$ 1.000.000.000 de patrimônio.",
        Icon.CROWN,
        Category.WEALTH,
        "networth",
        Decimal(1_000_000_000),
        Unit.BRL,
    ),
    Achievement(
        "many_baskets",
        "Ovos em várias cestas",
        "Manteve 8 ativos diferentes ao mesmo tempo.",
        Icon.EGG,
        Category.WEALTH,
        "held_assets",
        Decimal(8),
        Unit.COUNT,
    ),
    Achievement(
        "every_sector",
        "Em todo setor",
        "Manteve ações de 5 setores diferentes ao mesmo tempo.",
        Icon.LAYERS,
        Category.WEALTH,
        "held_sectors",
        Decimal(5),
        Unit.COUNT,
    ),
    # Mercado
    Achievement(
        "outperformed_storm",
        "Atravessou a tempestade",
        "Atravessou uma queda de 30% do Ibovespa perdendo menos que ele.",
        Icon.CLOUD_LIGHTNING,
        Category.MARKET,
        "outperformed_storm",
    ),
    Achievement(
        "cold_blood",
        "Sangue frio",
        "Não vendeu nada durante uma queda de 20% do Ibovespa.",
        Icon.SNOWFLAKE,
        Category.MARKET,
        "held_through_downturn",
    ),
    Achievement(
        "bought_the_dip",
        "Comprou no pânico",
        "Comprou ações durante uma queda de 20% do Ibovespa.",
        Icon.SHIELD_CHECK,
        Category.MARKET,
        "bought_in_downturn",
    ),
    Achievement(
        "above_cdi",
        "Acima do CDI",
        "Bateu o CDI 12 meses seguidos.",
        Icon.PERCENT,
        Category.MARKET,
        "months_above_cdi",
        Decimal(12),
        Unit.MONTHS,
    ),
    Achievement(
        "beat_ibov_year",
        "Mais que o Ibovespa",
        "Rendeu mais que o Ibovespa em 12 meses.",
        Icon.TARGET,
        Category.MARKET,
        "beat_ibov_year",
    ),
    Achievement(
        "candle_reader",
        "Leitor de velas",
        "Acertou 10 desafios da vela numa partida.",
        Icon.CHART_CANDLESTICK,
        Category.MARKET,
        "candle_challenge_hits",
        Decimal(10),
        Unit.COUNT,
    ),
    Achievement(
        "within_exemption",
        "Dentro da isenção",
        "Fechou um mês vendendo ações com lucro e sem pagar imposto, por ficar abaixo do limite de isenção.",
        Icon.RECEIPT,
        Category.MARKET,
        "exempt_month",
    ),
    Achievement(
        "day_trader",
        "Day trader",
        "Comprou e vendeu o mesmo ativo no mesmo dia.",
        Icon.ZAP,
        Category.MARKET,
        "day_traded",
    ),
    Achievement(
        "moved_the_market",
        "Mexeu o mercado",
        "Fez uma ordem grande o bastante para mover o preço do ativo, numa partida com impacto de preço.",
        Icon.ACTIVITY,
        Category.MARKET,
        "moved_market",
    ),
    # Partida
    Achievement(
        "first_win",
        "Primeira vitória",
        "Venceu uma partida com pelo menos mais um jogador.",
        Icon.TROPHY,
        Category.MATCH,
        "matches_won",
    ),
    Achievement(
        "full_room",
        "Sala cheia",
        "Venceu uma sala com 8 jogadores.",
        Icon.USERS,
        Category.MATCH,
        "won_room_size",
        Decimal(8),
    ),
    Achievement(
        "finished_match",
        "Partida até o fim",
        "Jogou uma partida até a data final.",
        Icon.FLAG,
        Category.MATCH,
        "finished_to_end",
    ),
    Achievement(
        "goal_race_win",
        "Primeiro na meta",
        "Venceu uma corrida à meta de patrimônio.",
        Icon.ROCKET,
        Category.MATCH,
        "won_goal_race",
    ),
    Achievement(
        "financial_independence",
        "Viveu de renda",
        "Alcançou a independência financeira.",
        Icon.SUNRISE,
        Category.MATCH,
        "won_financial_independence",
    ),
    Achievement(
        "no_crutches",
        "Sem muletas",
        "Venceu uma partida no modo Especialista, sem nenhuma ajuda.",
        Icon.MOUNTAIN,
        Category.MATCH,
        "won_expert_mode",
    ),
    Achievement(
        "winning_team",
        "Time vencedor",
        "Venceu uma partida em equipes.",
        Icon.HANDSHAKE,
        Category.MATCH,
        "won_as_team",
    ),
    Achievement(
        "beyond_the_horizon",
        "Além do horizonte",
        "Jogou um dia depois do último com dado real: daqui em diante o mercado é gerado.",
        Icon.TELESCOPE,
        Category.MATCH,
        "beyond_horizon",
    ),
    Achievement(
        "ace_score",
        "Nota de craque",
        "Chegou a 250 pontos na nota geral.",
        Icon.MEDAL,
        Category.MATCH,
        "overall_score",
        Decimal(250),
        Unit.POINTS,
    ),
    # Secretas
    Achievement(
        "monk_patience",
        "Paciência de monge",
        "Ficou 2 anos sem vender nenhuma ação.",
        Icon.HOURGLASS,
        Category.SECRET,
        "days_without_selling",
        Decimal(730),
        secret=True,
    ),
    Achievement(
        "punctual",
        "Pontual",
        "Comprou uma ação no primeiro pregão da partida.",
        Icon.FLAME,
        Category.SECRET,
        "bought_on_first_day",
        secret=True,
    ),
    Achievement(
        "empty_cash",
        "Caixa zerado",
        "Investiu tudo, com menos de 1% do patrimônio em caixa.",
        Icon.WALLET,
        Category.SECRET,
        "fully_invested",
        secret=True,
    ),
)

BY_CODE: dict[str, Achievement] = {a.code: a for a in CATALOG}
