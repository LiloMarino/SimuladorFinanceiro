from datetime import date
from decimal import Decimal

from pydantic import Field, SerializeAsAny

from backend.core.clt import (
    OVERTIME_HEALTH_MULTIPLE,
    OVERTIME_INCOME_RATE,
)
from backend.core.dates import add_months
from backend.core.dto.base import BaseDTO
from backend.core.enum import LockedAssetKind, Profession
from backend.core.locked_assets import LOCKED_EXITS
from backend.core.welfare import COURSE_INCOME_FACTOR


class LockedAssetDTO(BaseDTO):
    """Um patrimônio da profissão que fica fora do caixa, com a regra de saída dele."""

    kind: LockedAssetKind
    value: Decimal
    # A fração do patrimônio que este saldo é; o motor preenche ao montar a carteira
    networth_pct: Decimal = Decimal(0)
    exit_rule: str
    # Desde quando o saldo está travado; só o tipo cuja saída conta o tempo preenche
    since: date | None = None


class MechanicState(BaseDTO):
    """
    O estado da mecânica de uma profissão para um jogador numa partida. O tipo base é o
    da profissão sem mecânica: não guarda nada e não mexe na renda. Cada mecânica
    herda dele, dá valor inicial a todos os campos e sobrescreve `income_factor`.
    """

    @property
    def income_factor(self) -> Decimal:
        """O quanto o estado multiplica a renda exposta do mês (o benefício fica fora); 1 deixa a renda da profissão como está."""
        return Decimal(1)

    @property
    def health_factor(self) -> Decimal:
        """Quantas vezes o estado multiplica o imprevisto de saúde; 1 deixa o valor da profissão como está."""
        return Decimal(1)

    @property
    def locked_assets(self) -> list[LockedAssetDTO]:
        """Os patrimônios travados do jogador, cada um com a regra de saída; vazio sem conta travada."""
        return []

    @property
    def locked_value(self) -> Decimal:
        """O saldo das contas travadas do jogador, que entra no patrimônio: a soma dos patrimônios travados."""
        return sum((asset.value for asset in self.locked_assets), Decimal(0))


class CltState(MechanicState):
    """O estado do CLT: a conta do FGTS e a hora extra, ligada ou não."""

    fgts_balance: Decimal = Decimal(0)
    overtime: bool = False
    # Verdadeiro quando a recessão desligou a hora extra e o PIB de 12 meses ainda não voltou a zero
    overtime_waiting: bool = False

    @property
    def income_factor(self) -> Decimal:
        return 1 + OVERTIME_INCOME_RATE if self.overtime else Decimal(1)

    @property
    def health_factor(self) -> Decimal:
        return OVERTIME_HEALTH_MULTIPLE if self.overtime else Decimal(1)

    @property
    def locked_assets(self) -> list[LockedAssetDTO]:
        return [
            LockedAssetDTO(
                kind=LockedAssetKind.FGTS,
                value=self.fgts_balance,
                exit_rule=LOCKED_EXITS[LockedAssetKind.FGTS].rule,
            )
        ]


class ExchangeLock(BaseDTO):
    """A trava de câmbio do Exportador: o dólar combinado para uma fração da receita exportada e o que ela já rendeu."""

    # A fração da receita exportada que a trava cobre (0.5 = metade)
    share: Decimal
    months: int
    locked_dollar: Decimal
    contracted_on: date
    # Quantos pagamentos já usaram a trava e quanto ela rendeu a mais (ou a menos) neles
    paid_months: int = 0
    gain: Decimal = Decimal(0)

    @property
    def expires_on(self) -> date:
        return add_months(self.contracted_on, self.months)


class ExporterState(MechanicState):
    """O estado do Exportador: a fração exportada da receita, a última mudança do mix e a trava de câmbio."""

    export_share: Decimal = Decimal(1)
    mix_changed_on: date | None = None
    lock: ExchangeLock | None = None


class FreelancerState(MechanicState):
    """O estado do Autônomo: o preço por atendimento e o dia do último ajuste."""

    # Nulo é o preço inicial da partida: a referência do mercado na data de início
    price: Decimal | None = None
    price_set_on: date | None = None


class EntrepreneurState(MechanicState):
    """O estado do Empreendedor: a fração do lucro reinvestida, o capital da empresa e o que a política do bot lembra."""

    reinvest_share: Decimal = Decimal(0)
    capital: Decimal = Decimal(0)
    # O capital antes de cada um dos últimos pagamentos, do mais antigo ao mais recente
    capital_history: list[Decimal] = Field(default_factory=list)
    # Verdadeiro depois que a política vendeu na recessão em curso; um trimestre sem queda do PIB zera
    recession_sold: bool = False

    @property
    def locked_assets(self) -> list[LockedAssetDTO]:
        return [
            LockedAssetDTO(
                kind=LockedAssetKind.COMPANY_CAPITAL,
                value=self.capital,
                exit_rule=LOCKED_EXITS[LockedAssetKind.COMPANY_CAPITAL].rule,
            )
        ]


class PensionConversion(BaseDTO):
    """Uma parcela convertida em renda vitalícia: o dia, o valor que saiu do saldo, o juro real do dia e a renda mensal que ela rende."""

    converted_on: date
    amount: Decimal
    real_rate: Decimal
    # A renda do mês em reais do dia da conversão; a sala com correção a sobe pelo IPCA
    income: Decimal


class RetireeState(MechanicState):
    """O estado do Aposentado: o saldo da previdência, desde quando está no plano e as parcelas convertidas em renda."""

    # Nulo é o saldo que a partida ainda não abriu: a primeira leitura o fixa em 24 rendas do mês
    balance: Decimal | None = None
    # O dia em que o saldo abriu; o tempo no plano conta daqui
    since: date | None = None
    conversions: list[PensionConversion] = Field(default_factory=list)

    @property
    def locked_assets(self) -> list[LockedAssetDTO]:
        return [
            LockedAssetDTO(
                kind=LockedAssetKind.PENSION,
                value=self.balance or Decimal(0),
                since=self.since,
                exit_rule=LOCKED_EXITS[LockedAssetKind.PENSION].rule,
            )
        ]


class WelfareState(MechanicState):
    """O estado do Auxílio: o saldo do Pé-de-Meia, a conta das liberações, o caixa do início do mês e a matrícula no curso técnico."""

    balance: Decimal = Decimal(0)
    # Quantas datas de liberação já passaram, pagas ou adiadas
    releases_done: int = 0
    # Verdadeiro quando o caixa ficou negativo em algum dia desde a última liberação ou adiamento
    cash_was_negative: bool = False
    # O caixa somado à renda fixa e ao Tesouro no início do mês, antes da renda cair; nulo até a primeira virada
    month_start_wealth: Decimal | None = None
    # O dia da matrícula no curso técnico; nulo sem curso em andamento
    course_enrolled_on: date | None = None

    @property
    def in_course(self) -> bool:
        return self.course_enrolled_on is not None

    @property
    def income_factor(self) -> Decimal:
        return COURSE_INCOME_FACTOR if self.in_course else Decimal(1)

    @property
    def locked_assets(self) -> list[LockedAssetDTO]:
        return [
            LockedAssetDTO(
                kind=LockedAssetKind.WELFARE_SAVINGS,
                value=self.balance,
                exit_rule=LOCKED_EXITS[LockedAssetKind.WELFARE_SAVINGS].rule,
            )
        ]


class MechanicAction(BaseDTO):
    """Uma ação do jogador (ou da política do bot) sobre a mecânica; `kind` é o nome dela no histórico da vida."""

    kind: str = Field(min_length=1, max_length=40)


# O nome de cada lançamento da hora extra no histórico da vida
OVERTIME_ON = "overtime_on"
OVERTIME_OFF = "overtime_off"
OVERTIME_ENDED = "overtime_ended"
OVERTIME_AVAILABLE = "overtime_available"


class SetOvertime(MechanicAction):
    """Liga (`overtime_on`) ou desliga (`overtime_off`) a hora extra do CLT."""

    kind: str = Field(pattern=r"^overtime_(on|off)$")

    @property
    def enabled(self) -> bool:
        return self.kind == OVERTIME_ON


# O nome de cada lançamento do Exportador no histórico da vida
EXCHANGE_LOCK = "exchange_lock"
EXPORT_MIX = "export_mix"
EXCHANGE_LOCK_ENDED = "exchange_lock_ended"


class ExporterAction(MechanicAction):
    """Uma ação do Exportador; é o tipo que a mecânica aceita."""


class LockExchange(ExporterAction):
    """Contrata a trava de câmbio; o dólar travado é o da cotação do servidor no dia da ação."""

    kind: str = Field(default=EXCHANGE_LOCK, pattern=rf"^{EXCHANGE_LOCK}$")
    share: Decimal
    months: int
    locked_dollar: Decimal


class SetExportMix(ExporterAction):
    """Muda a fração exportada da receita."""

    kind: str = Field(default=EXPORT_MIX, pattern=rf"^{EXPORT_MIX}$")
    share: Decimal


# O nome do lançamento do Autônomo no histórico da vida
SET_PRICE = "set_price"


class FreelancerAction(MechanicAction):
    """Uma ação do Autônomo; é o tipo que a mecânica aceita."""


class SetPrice(FreelancerAction):
    """Salva o preço por atendimento; `reference` é a referência do mercado do servidor no dia da ação."""

    kind: str = Field(default=SET_PRICE, pattern=rf"^{SET_PRICE}$")
    price: Decimal
    reference: Decimal


# O nome dos lançamentos do Empreendedor no histórico da vida
SET_REINVEST_SHARE = "set_reinvest_share"
SELL_CAPITAL = "sell_capital"


class EntrepreneurAction(MechanicAction):
    """Uma ação do Empreendedor; é o tipo que a mecânica aceita."""


class SetReinvestShare(EntrepreneurAction):
    """Salva a fração do lucro que volta para a empresa, valendo a partir do próximo pagamento."""

    kind: str = Field(default=SET_REINVEST_SHARE, pattern=rf"^{SET_REINVEST_SHARE}$")
    share: Decimal


class SellCapital(EntrepreneurAction):
    """Vende uma fração do capital da empresa, com o desconto da venda."""

    kind: str = Field(default=SELL_CAPITAL, pattern=rf"^{SELL_CAPITAL}$")
    share: Decimal


# O nome dos lançamentos do Aposentado no histórico da vida
CONVERT_PENSION = "convert_pension"
REDEEM_PENSION = "redeem_pension"


class RetireeAction(MechanicAction):
    """Uma ação do Aposentado; é o tipo que a mecânica aceita."""


class ConvertPension(RetireeAction):
    """Converte `amount` do saldo em renda vitalícia; `real_rate` é o juro real do servidor no dia da ação."""

    kind: str = Field(default=CONVERT_PENSION, pattern=rf"^{CONVERT_PENSION}$")
    amount: Decimal
    real_rate: Decimal


class RedeemPension(RetireeAction):
    """Resgata `amount` do saldo para o caixa, com o IR regressivo da faixa do tempo no plano."""

    kind: str = Field(default=REDEEM_PENSION, pattern=rf"^{REDEEM_PENSION}$")
    amount: Decimal


# O nome dos lançamentos do Auxílio no histórico da vida
ENROLL_COURSE = "enroll_course"
SAVINGS_RELEASED = "savings_released"
SAVINGS_POSTPONED = "savings_postponed"


class WelfareAction(MechanicAction):
    """Uma ação do Auxílio; é o tipo que a mecânica aceita."""


class EnrollCourse(WelfareAction):
    """Matricula o jogador no curso técnico, que começa hoje."""

    kind: str = Field(default=ENROLL_COURSE, pattern=rf"^{ENROLL_COURSE}$")


class ProfessionPeriodDTO(BaseDTO):
    """A profissão que o jogador exerce a partir de `start`, até o início do período seguinte."""

    profession: Profession
    start: date


class ProfessionStateDTO(BaseDTO):
    """A profissão do jogador e o estado da mecânica dela."""

    profession: Profession
    state: SerializeAsAny[MechanicState]


# O tipo do estado de cada profissão com mecânica; as demais usam o tipo base
STATE_TYPES: dict[Profession, type[MechanicState]] = {
    Profession.CLT: CltState,
    Profession.ENTREPRENEUR: EntrepreneurState,
    Profession.EXPORTER: ExporterState,
    Profession.FREELANCER: FreelancerState,
    Profession.RETIREE: RetireeState,
    Profession.WELFARE: WelfareState,
}


def state_type_of(profession: Profession) -> type[MechanicState]:
    return STATE_TYPES.get(profession, MechanicState)


def initial_state(profession: Profession) -> MechanicState:
    """O estado de quem começa na profissão: cada campo no valor inicial do tipo."""
    return state_type_of(profession)()


def state_from_json(profession: Profession, data: dict) -> MechanicState:
    return state_type_of(profession).model_validate(data)
