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


class AchievementCategory(Enum):
    FIRST_STEPS = "FIRST_STEPS"
    WEALTH = "WEALTH"
    MARKET = "MARKET"
    MATCH = "MATCH"
    SECRET = "SECRET"


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


class AchievementUnit(Enum):
    """Como o progresso da conquista é escrito: dinheiro, contagem ou meses."""

    BRL = "BRL"
    COUNT = "COUNT"
    MONTHS = "MONTHS"
    DAYS = "DAYS"


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
    TICKERS = "tickers"
