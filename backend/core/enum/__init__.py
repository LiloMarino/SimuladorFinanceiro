from decimal import Decimal
from enum import Enum


class FixedIncomeType(Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_DIRETO = "Tesouro Direto"

    @property
    def db_value(self) -> str:
        return {
            FixedIncomeType.CDB: "CDB",
            FixedIncomeType.LCI: "LCI",
            FixedIncomeType.LCA: "LCA",
            FixedIncomeType.TESOURO_DIRETO: "TESOURO_DIRETO",
        }[self]

    @classmethod
    def from_db(cls, value: str) -> "FixedIncomeType":
        mapping = {
            "CDB": cls.CDB,
            "LCI": cls.LCI,
            "LCA": cls.LCA,
            "TESOURO_DIRETO": cls.TESOURO_DIRETO,
        }
        return mapping[value]


class RateIndexType(Enum):
    CDI = "CDI"
    IPCA = "IPCA"
    SELIC = "SELIC"
    PREFIXADO = "Prefixado"

    @property
    def db_value(self) -> str:
        return {
            RateIndexType.CDI: "CDI",
            RateIndexType.IPCA: "IPCA",
            RateIndexType.SELIC: "SELIC",
            RateIndexType.PREFIXADO: "PREFIXADO",
        }[self]

    @classmethod
    def from_db(cls, value: str) -> "RateIndexType":
        mapping = {
            "CDI": cls.CDI,
            "IPCA": cls.IPCA,
            "SELIC": cls.SELIC,
            "PREFIXADO": cls.PREFIXADO,
        }
        return mapping[value]


class CashflowEventType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    DIVIDEND = "DIVIDEND"
    CONTRIBUTION = "CONTRIBUTION"
    TAX = "TAX"
    SALARY = "SALARY"
    EXPENSE = "EXPENSE"
    UNEXPECTED_EXPENSE = "UNEXPECTED_EXPENSE"
    OVERDRAFT_INTEREST = "OVERDRAFT_INTEREST"
    LOAN_PROCEEDS = "LOAN_PROCEEDS"
    LOAN_PAYMENT = "LOAN_PAYMENT"
    CAMPAIGN_CONTRIBUTION = "CAMPAIGN_CONTRIBUTION"
    CAMPAIGN_DONATION = "CAMPAIGN_DONATION"
    CAMPAIGN_ACTION = "CAMPAIGN_ACTION"

    @property
    def sign(self) -> int:
        """+1 quando o evento entra no caixa, -1 quando sai: o valor gravado é sempre positivo."""
        return CASH_SIGN[self]

    @property
    def is_contribution(self) -> bool:
        """Conta no capital aportado do jogador, não no rendimento nem na perda."""
        return self in CONTRIBUTION_TYPES


CASH_SIGN: dict[CashflowEventType, int] = {
    CashflowEventType.DEPOSIT: 1,
    CashflowEventType.WITHDRAW: -1,
    CashflowEventType.DIVIDEND: 1,
    CashflowEventType.CONTRIBUTION: 1,
    CashflowEventType.TAX: -1,
    CashflowEventType.SALARY: 1,
    CashflowEventType.EXPENSE: -1,
    CashflowEventType.UNEXPECTED_EXPENSE: -1,
    CashflowEventType.OVERDRAFT_INTEREST: -1,
    CashflowEventType.LOAN_PROCEEDS: 1,
    CashflowEventType.LOAN_PAYMENT: -1,
    CashflowEventType.CAMPAIGN_CONTRIBUTION: -1,
    CashflowEventType.CAMPAIGN_DONATION: -1,
    CashflowEventType.CAMPAIGN_ACTION: -1,
}

# Aporte, salário, despesa e imprevisto são o dinheiro da vida do jogador; o juro
# do cheque especial é perda dele, como o IR
CONTRIBUTION_TYPES = frozenset(
    {
        CashflowEventType.CONTRIBUTION,
        CashflowEventType.SALARY,
        CashflowEventType.EXPENSE,
        CashflowEventType.UNEXPECTED_EXPENSE,
    }
)


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderAction(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    EXECUTED = "executed"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELED = "canceled"


class EquityEventType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class AssetClass(Enum):
    STOCK = "STOCK"
    FII = "FII"
    ETF = "ETF"
    BDR = "BDR"
    CRYPTO = "CRYPTO"

    @property
    def fractional(self) -> bool:
        """Só a cripto negocia fração de unidade."""
        return self is AssetClass.CRYPTO


class SimulationStatus(Enum):
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


class VictoryCriterion(Enum):
    SCORE = "SCORE"
    RETURN = "RETURN"
    NETWORTH = "NETWORTH"
    SHARPE = "SHARPE"


class GameType(Enum):
    """O que decide a partida: o critério de vitória (Clássica) ou chegar a uma meta de patrimônio."""

    CLASSIC = "CLASSIC"
    GOAL_RACE = "GOAL_RACE"
    FINANCIAL_INDEPENDENCE = "FINANCIAL_INDEPENDENCE"
    # Da expansão Governo & Política: vence o partido com a maior soma de patrimônio dos filiados
    POLITICAL = "POLITICAL"

    @property
    def has_goal(self) -> bool:
        """A partida acaba quando alguém chega a um patrimônio-alvo."""
        return self in (GameType.GOAL_RACE, GameType.FINANCIAL_INDEPENDENCE)


class BacktestPriceImpact(Enum):
    """Os níveis do impacto de preço que o backtest oferece: desligado, ou um dos dois ajustes prontos."""

    OFF = "OFF"
    REALISTIC = "REALISTIC"
    STRONG = "STRONG"


class PresetRuleGroup(Enum):
    """As regras de um preset agrupadas como o painel as mostra."""

    PERIOD = "PERIOD"
    STARTING_CASH = "STARTING_CASH"
    MONTHLY_CONTRIBUTION = "MONTHLY_CONTRIBUTION"
    GROUPING = "GROUPING"
    GAME_TYPE = "GAME_TYPE"
    VICTORY = "VICTORY"
    GOAL = "GOAL"
    LIFE = "LIFE"
    ASSISTANCES = "ASSISTANCES"
    PRICE_IMPACT = "PRICE_IMPACT"
    EXPANSIONS = "EXPANSIONS"


class AchievementCategory(Enum):
    FIRST_STEPS = "FIRST_STEPS"
    WEALTH = "WEALTH"
    MARKET = "MARKET"
    MATCH = "MATCH"
    SECRET = "SECRET"  # noqa: S105


class AchievementIcon(Enum):
    """Nomes dos ícones do `lucide-react`; o front tem um ícone para cada valor."""

    SHOPPING_CART = "SHOPPING_CART"
    LANDMARK = "LANDMARK"
    HAND_COINS = "HAND_COINS"
    HAMMER = "HAMMER"
    TRENDING_UP = "TRENDING_UP"
    PIGGY_BANK = "PIGGY_BANK"
    GEM = "GEM"
    CROWN = "CROWN"
    EGG = "EGG"
    CLOUD_LIGHTNING = "CLOUD_LIGHTNING"
    SNOWFLAKE = "SNOWFLAKE"
    PERCENT = "PERCENT"
    TARGET = "TARGET"
    SHIELD_CHECK = "SHIELD_CHECK"
    TROPHY = "TROPHY"
    USERS = "USERS"
    FLAG = "FLAG"
    ROCKET = "ROCKET"
    HOURGLASS = "HOURGLASS"
    SUNRISE = "SUNRISE"
    WALLET = "WALLET"
    FLAME = "FLAME"
    CHART_CANDLESTICK = "CHART_CANDLESTICK"
    RECEIPT = "RECEIPT"
    ZAP = "ZAP"
    LAYERS = "LAYERS"
    ACTIVITY = "ACTIVITY"
    MOUNTAIN = "MOUNTAIN"
    HANDSHAKE = "HANDSHAKE"
    TELESCOPE = "TELESCOPE"
    MEDAL = "MEDAL"


class AchievementUnit(Enum):
    """Como o progresso da conquista é escrito: dinheiro, contagem, meses, dias ou pontos."""

    BRL = "BRL"
    COUNT = "COUNT"
    MONTHS = "MONTHS"
    DAYS = "DAYS"
    POINTS = "POINTS"


class LifeEventEffect(Enum):
    # Sai do caixa o múltiplo da despesa mensal do dia
    CASH_OUT = "CASH_OUT"
    # O salário do mês seguinte não entra
    SKIP_NEXT_SALARY = "SKIP_NEXT_SALARY"


class LifeHistorySort(Enum):
    DATE = "date"
    TYPE = "type"
    DESCRIPTION = "description"
    AMOUNT = "amount"
    CASH = "cash"


class LifeHistoryCategory(Enum):
    """Os filtros do histórico do viver de renda."""

    UNEXPECTED = "UNEXPECTED"
    LAYOFF = "LAYOFF"
    OVERDRAFT = "OVERDRAFT"


class LifeHistoryKind(Enum):
    UNEXPECTED_EXPENSE = "UNEXPECTED_EXPENSE"
    LAYOFF = "LAYOFF"
    OVERDRAFT_STARTED = "OVERDRAFT_STARTED"
    OVERDRAFT_ENDED = "OVERDRAFT_ENDED"
    # Soma do juro cobrado por pregão no mês
    OVERDRAFT_INTEREST = "OVERDRAFT_INTEREST"


class PlayerGrouping(Enum):
    """Como a sala compete: cada um por si ou em equipes."""

    INDIVIDUAL = "INDIVIDUAL"
    TEAMS = "TEAMS"


class TeamNaming(Enum):
    """Como a equipe é chamada: pelo nome da cor (Índigo) ou pelo número."""

    COLOR = "COLOR"
    NUMBER = "NUMBER"


class PlayerActivity(Enum):
    """O que o jogador está fazendo na sala: a tela em que está, ou fora da aba do jogo."""

    LOBBY = "lobby"
    IMPORT_ASSETS = "import_assets"
    COMPARE_SIMULATIONS = "compare_simulations"
    MATCH_RESULT = "match_result"
    SETTINGS = "settings"
    # Qualquer outra tela
    MENUS = "menus"
    AWAY = "away"


class FixedIncomeEventType(Enum):
    BUY = "BUY"
    REDEEM = "REDEEM"


class CreditEventType(Enum):
    CONTRACT = "CONTRACT"
    INSTALLMENT_PAID = "INSTALLMENT_PAID"
    INSTALLMENT_LATE = "INSTALLMENT_LATE"
    OVERDUE_PAID = "OVERDUE_PAID"
    PREPAYMENT = "PREPAYMENT"
    PAYOFF = "PAYOFF"


class PrepaymentMode(Enum):
    """O que a amortização faz com a sobra: encurta o prazo ou reduz a parcela."""

    SHORTEN_TERM = "SHORTEN_TERM"
    REDUCE_INSTALLMENT = "REDUCE_INSTALLMENT"


class CreditGrade(Enum):
    """Nota de risco do jogador, da melhor (AAA) à que fecha o crédito (D)."""

    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    D = "D"


class IndicatorSeries(Enum):
    CDI = "CDI"
    SELIC = "SELIC"
    IPCA = "IPCA"
    IBOV = "IBOV"


class DataOrigin(Enum):
    REAL = "REAL"
    GENERATED = "GENERATED"


class MarketRegime(Enum):
    """Bioma de um trecho do mercado, pelo tercil da volatilidade do Ibovespa."""

    CALM = "CALM"
    NORMAL = "NORMAL"
    AGITATED = "AGITATED"


class StrategyLogKind(Enum):
    """Linha do registro da estratégia: uma ordem ou uma mudança de modo."""

    ORDER = "order"
    ENABLED = "enabled"
    SWITCHED = "switched"
    PARAMS = "params"
    DISABLED = "disabled"
    ERROR = "error"
    ERROR_SEEN = "error_seen"
    RESUMED = "resumed"


class StrategyAction(Enum):
    BUY = "buy"
    SELL = "sell"
    CANCEL = "cancel"
    INVEST = "invest"
    REDEEM = "redeem"


class StrategyOrderStatus(Enum):
    EXECUTED = "executed"
    PARTIAL = "partial"
    OPEN = "open"
    CANCELED = "canceled"
    REFUSED = "refused"


class StrategyGroup(Enum):
    REFERENCE = "reference"
    TACTIC = "tactic"


class StrategyParamKind(Enum):
    INT = "int"
    PERCENT = "percent"
    TICKER = "ticker"
    TICKERS = "tickers"


class StrategyView(Enum):
    """O bloco que a página mostra no detalhe da estratégia."""

    SIGNAL = "signal"
    RANKING = "ranking"
    ALLOCATION = "allocation"
    NONE = "none"


class SignalLineStyle(Enum):
    PRICE = "price"
    FAST = "fast"
    SLOW = "slow"
    CHANNEL = "channel"
    OSCILLATOR = "oscillator"


class SignalPane(Enum):
    PRICE = "price"
    OSCILLATOR = "oscillator"


class InitialAccount(Enum):
    """A conta do governo no primeiro dia: a dívida real com receita igual ao gasto, ou com o déficit real."""

    PLAYABLE = "PLAYABLE"
    REALISTIC = "REALISTIC"


class ComputerDifficulty(Enum):
    """A verba de cada partido do computador, em múltiplo da média dos partidos de jogadores."""

    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"

    @property
    def budget_factor(self) -> Decimal:
        return {
            ComputerDifficulty.EASY: Decimal("0.5"),
            ComputerDifficulty.NORMAL: Decimal(1),
            ComputerDifficulty.HARD: Decimal("1.5"),
        }[self]


class GovernmentEventType(Enum):
    """Tudo o que muda o estado político da partida; o estado é o replay desses eventos."""

    PARTY_FOUNDED = "PARTY_FOUNDED"
    # O fundador de um partido sem bandeiras escolhe as 3
    PARTY_VALUES_SET = "PARTY_VALUES_SET"
    COMPUTER_PARTY_ADDED = "COMPUTER_PARTY_ADDED"
    COMPUTER_PARTY_REMOVED = "COMPUTER_PARTY_REMOVED"
    PARTY_JOINED = "PARTY_JOINED"
    PARTY_LEFT = "PARTY_LEFT"
    MEMBER_EXPELLED = "MEMBER_EXPELLED"
    CONTRIBUTION_SET = "CONTRIBUTION_SET"
    TICKET_SET = "TICKET_SET"
    VICE_ANSWERED = "VICE_ANSWERED"
    CAMPAIGN_SPENT = "CAMPAIGN_SPENT"
    DONATION_MADE = "DONATION_MADE"
    # Ação avulsa de campanha (TV, evento, comício ou ataque) com o dado já rolado
    CAMPAIGN_ACTION = "CAMPAIGN_ACTION"
    ELECTION_ROUND = "ELECTION_ROUND"
    TERM_STARTED = "TERM_STARTED"
    MEASURE_PROPOSED = "MEASURE_PROPOSED"
    MEASURE_WITHDRAWN = "MEASURE_WITHDRAWN"
    MEASURE_VOTED = "MEASURE_VOTED"
    APPROVAL_MEASURED = "APPROVAL_MEASURED"
    IMPEACHED = "IMPEACHED"
    # A chapa anuncia, troca ou retira promessas
    PROMISES_SET = "PROMISES_SET"
    # Com as chapas fechadas, metade do efeito das promessas em vigor passa a pesar no voto
    PROMISES_WEIGHED = "PROMISES_WEIGHED"
    # O balanço do fim do mandato: o que cada promessa cumpriu deixa afinidade e rejeição
    PROMISES_SETTLED = "PROMISES_SETTLED"
    # Entre os turnos: o partido eliminado declara apoio a um finalista, ou neutralidade
    RUNOFF_ENDORSED = "RUNOFF_ENDORSED"
    # Entre os turnos: a contribuição única de um filiado do finalista
    RUNOFF_CONTRIBUTION = "RUNOFF_CONTRIBUTION"
    # Entre os turnos: a pesquisa semanal, com o voto exato do dia
    RUNOFF_POLL = "RUNOFF_POLL"
    # A casa de 101 cadeiras, eleita no 1º turno com o presidente
    HOUSE_ELECTED = "HOUSE_ELECTED"
    # O líder orienta a bancada numa votação
    BLOC_GUIDED = "BLOC_GUIDED"
    # O líder muda a regra de orientação de um valor
    GUIDANCE_RULE_SET = "GUIDANCE_RULE_SET"
    # O pedido de impeachment abre e, no dia de votação, a casa decide
    IMPEACHMENT_REQUESTED = "IMPEACHMENT_REQUESTED"
    IMPEACHMENT_VOTED = "IMPEACHMENT_VOTED"
    # O governo propõe um acordo de apoio por emenda e o partido responde, ou o prazo vence
    DEAL_PROPOSED = "DEAL_PROPOSED"
    DEAL_ANSWERED = "DEAL_ANSWERED"
    # O governo cancela a proposta antes da resposta
    DEAL_WITHDRAWN = "DEAL_WITHDRAWN"
    # Um dos lados rompe o acordo em vigor
    DEAL_BROKEN = "DEAL_BROKEN"


class ElectionPhase(Enum):
    """Onde a partida está no ciclo eleitoral."""

    # Antes da campanha abrir: o governo é do computador e nada muda
    BEFORE_CAMPAIGN = "BEFORE_CAMPAIGN"
    # Partidos, chapas e verba abertos, até o 1º turno
    CAMPAIGN = "CAMPAIGN"
    # Entre os turnos: a partida pausa no resultado e quem ficou de fora pode doar
    BETWEEN_ROUNDS = "BETWEEN_ROUNDS"
    # Eleito, esperando a posse de 1º de janeiro
    AWAITING_TERM = "AWAITING_TERM"
    # Governo empossado, até a campanha da eleição seguinte
    TERM = "TERM"


class VicePhase(Enum):
    NONE = "NONE"
    # Convidado, ainda sem resposta
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class PauseReason(Enum):
    """Por que a partida está parada; o host pausa, e o calendário do governo também."""

    HOST = "HOST"
    CAMPAIGN_OPENED = "CAMPAIGN_OPENED"
    FIRST_ROUND_RESULT = "FIRST_ROUND_RESULT"
    RUNOFF_RESULT = "RUNOFF_RESULT"
    IMPEACHMENT = "IMPEACHMENT"


class GovernmentNoticeKind(Enum):
    """O que o aviso em tempo real conta; o front escolhe o toast pelo tipo."""

    UPDATED = "UPDATED"
    CAMPAIGN_OPENED = "CAMPAIGN_OPENED"
    TICKETS_CLOSING = "TICKETS_CLOSING"
    ELECTION_EVE = "ELECTION_EVE"
    PARTY_FOUNDED = "PARTY_FOUNDED"
    EXPELLED = "EXPELLED"
    VICE_INVITED = "VICE_INVITED"
    VICE_ANSWERED = "VICE_ANSWERED"
    DONATION = "DONATION"
    ELECTION_RESULT = "ELECTION_RESULT"
    TERM_STARTED = "TERM_STARTED"
    MEASURE_PROPOSED = "MEASURE_PROPOSED"
    MEASURE_WITHDRAWN = "MEASURE_WITHDRAWN"
    MEASURE_VOTED = "MEASURE_VOTED"
    MEASURE_IN_FORCE = "MEASURE_IN_FORCE"
    IMPEACHMENT = "IMPEACHMENT"
    IMPEACHMENT_WARNING = "IMPEACHMENT_WARNING"
    MONTH_CLOSED = "MONTH_CLOSED"
    CAMPAIGN_ACTION = "CAMPAIGN_ACTION"
    PROMISES_SET = "PROMISES_SET"
    PROMISES_SETTLED = "PROMISES_SETTLED"
    ENDORSEMENT = "ENDORSEMENT"
    HOUSE_ELECTED = "HOUSE_ELECTED"
    IMPEACHMENT_REQUESTED = "IMPEACHMENT_REQUESTED"
    IMPEACHMENT_VOTED = "IMPEACHMENT_VOTED"
    DEAL_PROPOSED = "DEAL_PROPOSED"
    DEAL_ANSWERED = "DEAL_ANSWERED"
    DEAL_BROKEN = "DEAL_BROKEN"
    DEAL_ENDED = "DEAL_ENDED"


class CampaignActionKind(Enum):
    """As quatro ações avulsas que um filiado dispara na campanha."""

    # Todos os grupos de uma vez, com dois dados (vale o maior)
    TV = "TV"
    # Um grupo; também repara um pouco da rejeição do partido nele
    EVENT = "EVENT"
    # Um grupo, barato, com os extremos do dado dobrados
    RALLY = "RALLY"
    # Um grupo e um partido rival: tira apoio do rival
    ATTACK = "ATTACK"


class DiceBand(Enum):
    """A faixa em que o d20 de uma ação caiu."""

    DISASTER = "DISASTER"
    WEAK = "WEAK"
    NORMAL = "NORMAL"
    GOOD = "GOOD"
    VIRAL = "VIRAL"


class CampaignEntryKind(Enum):
    """O que uma linha do histórico de campanha do partido conta."""

    TV = "TV"
    EVENT = "EVENT"
    RALLY = "RALLY"
    ATTACK = "ATTACK"
    BASE_BUDGET = "BASE_BUDGET"
    # Ataque que outro partido fez ao partido de quem vê: sem o dado do rival
    ATTACK_RECEIVED = "ATTACK_RECEIVED"


class MeasureKind(Enum):
    """O que uma medida muda: um imposto geral, a regra de um setor ou segmento ou um gasto público."""

    # Alíquota do ganho comum nas vendas de ações
    STOCK_PROFIT_RATE = "STOCK_PROFIT_RATE"
    DAY_TRADE_RATE = "DAY_TRADE_RATE"
    # Teto mensal de vendas de ações com ganho isento; zero acaba com a isenção
    STOCK_EXEMPTION = "STOCK_EXEMPTION"
    # Tabela única: a mesma alíquota em qualquer prazo
    FIXED_INCOME_TABLE = "FIXED_INCOME_TABLE"
    LCI_LCA_RATE = "LCI_LCA_RATE"
    SECTOR_EXEMPT = "SECTOR_EXEMPT"
    # Soma pontos à alíquota do ganho do setor
    SECTOR_TAX = "SECTOR_TAX"
    # Gasto público: o auxílio e as obras em fração do PIB por ano, os reajustes em fração ao ano
    WELFARE_SPENDING = "WELFARE_SPENDING"
    SERVANT_RAISE = "SERVANT_RAISE"
    RETIREE_RAISE = "RETIREE_RAISE"
    PUBLIC_WORKS = "PUBLIC_WORKS"

    @property
    def is_sector(self) -> bool:
        return self in (MeasureKind.SECTOR_EXEMPT, MeasureKind.SECTOR_TAX)

    @property
    def is_spending(self) -> bool:
        return self in (
            MeasureKind.WELFARE_SPENDING,
            MeasureKind.SERVANT_RAISE,
            MeasureKind.RETIREE_RAISE,
            MeasureKind.PUBLIC_WORKS,
        )


class EffectPhase(Enum):
    """Onde está o efeito de uma medida de gasto na economia."""

    # A medida foi aprovada e ainda não vale
    WAITING = "WAITING"
    # Vale e o efeito ainda enche
    RISING = "RISING"
    # Passou do cheio e cai pela metade a cada meia-vida
    FALLING = "FALLING"
    # Restou tão pouco que já não pesa
    FADED = "FADED"


class MeasureStatus(Enum):
    QUEUED = "QUEUED"
    # Aprovada, esperando a vigência ou já valendo
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    # A fila não votada sai quando o governo muda
    DROPPED = "DROPPED"


class DealStatus(Enum):
    """Onde está um acordo de apoio por emenda entre o governo e a bancada de um partido."""

    # Proposto, esperando a resposta do partido
    PENDING = "PENDING"
    # Aceito: a bancada orienta Sim e a emenda corre até o fim do prazo
    ACTIVE = "ACTIVE"
    DECLINED = "DECLINED"
    # O governo cancelou a proposta antes da resposta
    WITHDRAWN = "WITHDRAWN"
    # Um dos lados rompeu o acordo em vigor
    BROKEN = "BROKEN"
    # Encerrado antes do prazo sem quebra: o governo mudou
    CUT = "CUT"


class DealBreaker(Enum):
    """Quem rompeu o acordo."""

    GOVERNMENT = "GOVERNMENT"
    ALLY = "ALLY"


class ApprovalFactorKind(Enum):
    """O que empurra o alvo de satisfação de um grupo; BASE é o ponto neutro."""

    BASE = "BASE"
    INFLATION = "INFLATION"
    SELIC = "SELIC"
    STOCKS = "STOCKS"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    RISK_PREMIUM = "RISK_PREMIUM"
    MEASURE = "MEASURE"


class PromiseState(Enum):
    """Como uma promessa está diante do que vale hoje na política do país."""

    # Chegou ao alvo
    FULFILLED = "FULFILLED"
    # Andou parte do caminho até o alvo
    IN_PROGRESS = "IN_PROGRESS"
    # Nada mudou desde o anúncio
    UNTOUCHED = "UNTOUCHED"
    # A política andou no sentido oposto ao do alvo
    CONTRARY = "CONTRARY"


class GroupVerdict(Enum):
    """Como um grupo fecha o mês: acima da faixa neutra aprova, abaixo reprova."""

    APPROVES = "APPROVES"
    NEUTRAL = "NEUTRAL"
    REPROVES = "REPROVES"


class VoterGroup(Enum):
    """Os grupos em que o eleitorado se divide; cada um vota pelo que acha de cada partido."""

    INVESTORS = "INVESTORS"
    ENTREPRENEURS = "ENTREPRENEURS"
    FORMAL_WORKERS = "FORMAL_WORKERS"
    PUBLIC_SERVANTS = "PUBLIC_SERVANTS"
    RETIREES = "RETIREES"
    WELFARE = "WELFARE"


class VoterValue(Enum):
    """As bandeiras de um partido e os eixos do perfil dele."""

    FREE_MARKET = "FREE_MARKET"
    SOCIAL_JUSTICE = "SOCIAL_JUSTICE"
    STABILITY = "STABILITY"
    DEVELOPMENT = "DEVELOPMENT"
    SAVER_PROTECTION = "SAVER_PROTECTION"
    PUBLIC_SERVICE = "PUBLIC_SERVICE"


class GroupReading(Enum):
    """Um resultado do governo que o grupo de eleitores lê."""

    INFLATION = "INFLATION"
    SELIC = "SELIC"
    STOCKS = "STOCKS"
    CAPITAL_GAINS_TAX = "CAPITAL_GAINS_TAX"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    RISK_PREMIUM = "RISK_PREMIUM"


class SummaryKind(Enum):
    """O que o resumo entregue na virada do período conta."""

    MONTH_SUMMARY = "MONTH_SUMMARY"
    YEAR_REVIEW = "YEAR_REVIEW"


class NewsSection(Enum):
    """A seção do jornal da partida; a ordem é a da importância numa rajada."""

    ECONOMY = "ECONOMY"
    COMPANIES = "COMPANIES"
    POLITICS = "POLITICS"
    HISTORY = "HISTORY"


class NewsType(Enum):
    """Um tipo de manchete do jornal; cada um tem seção, texto e nível padrão no registro."""

    ELECTION_CALENDAR = "ELECTION_CALENDAR"
    # Resultado de turno e impeachment: a sala pausa e a janela abre para todos
    ELECTION_RESULT = "ELECTION_RESULT"
    TERM_STARTED = "TERM_STARTED"
    MEASURE_PROPOSED = "MEASURE_PROPOSED"
    MEASURE_VOTED = "MEASURE_VOTED"
    PARTY_LIFE = "PARTY_LIFE"
    CAMPAIGN = "CAMPAIGN"
    COPOM_DECISION = "COPOM_DECISION"
    MONTHLY_INFLATION = "MONTHLY_INFLATION"
    IBOVESPA_EXTREME = "IBOVESPA_EXTREME"
    STRONG_MOVE = "STRONG_MOVE"
    WEEK_HIGH = "WEEK_HIGH"
    HISTORICAL_MILESTONE = "HISTORICAL_MILESTONE"


class NewsLevel(Enum):
    """Como uma manchete chega a um jogador, escolhido por tipo."""

    # No centro da tela, sem pausar, fechando sozinha
    WINDOW = "WINDOW"
    # No cartão do canto ou na faixa
    JOURNAL = "JOURNAL"
    HISTORY_ONLY = "HISTORY_ONLY"
    OFF = "OFF"


class NewsPosition(Enum):
    """Onde o jornal aparece na tela; os toasts ficam embaixo, no lado oposto."""

    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    TOP_LEFT = "TOP_LEFT"
    # Faixa de manchetes abaixo da topbar
    STRIP = "STRIP"


class PendingType(Enum):
    """Um tipo de pendência: o que pede ação do jogador e fica à vista até a condição acabar."""

    OVERDUE_INSTALLMENT = "OVERDUE_INSTALLMENT"
    NEGATIVE_CASH = "NEGATIVE_CASH"
    IMPEACHMENT_RISK = "IMPEACHMENT_RISK"
    CASH_SHORT = "CASH_SHORT"
    STRATEGY_ERROR = "STRATEGY_ERROR"
    VICE_INVITE = "VICE_INVITE"
    CAMPAIGN_OPEN = "CAMPAIGN_OPEN"
    UNGUIDED_VOTE = "UNGUIDED_VOTE"
    DEAL_PROPOSAL = "DEAL_PROPOSAL"


class PendingSeverity(Enum):
    """Grave já custa dinheiro ou trava algo; aviso ainda dá tempo."""

    SEVERE = "SEVERE"
    WARNING = "WARNING"


class ToastType(Enum):
    """Um aviso do que acontece com o próprio jogador, ligado ou desligado por tipo."""

    ORDER_EXECUTED = "ORDER_EXECUTED"
    ORDER_PARTIAL = "ORDER_PARTIAL"
    STRATEGY_ORDERS = "STRATEGY_ORDERS"
    PLAYER_PRESENCE = "PLAYER_PRESENCE"
    CREDIT_PAYMENTS = "CREDIT_PAYMENTS"
    CREDIT_RATING = "CREDIT_RATING"
    LIFE_EVENT = "LIFE_EVENT"
    MONTH_SUMMARY = "MONTH_SUMMARY"
    VICE_ANSWER = "VICE_ANSWER"
