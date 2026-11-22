from datetime import date
from decimal import Decimal

from pydantic import Field, SerializeAsAny

from backend.core.clt import (
    OVERTIME_HEALTH_MULTIPLE,
    OVERTIME_INCOME_RATE,
)
from backend.core.dto.base import BaseDTO
from backend.core.enum import Profession


class MechanicState(BaseDTO):
    """
    O estado da mecânica de uma profissão para um jogador numa partida. O tipo base é o
    da profissão sem mecânica: não guarda nada e não mexe na renda. Cada mecânica
    herda dele, dá valor inicial a todos os campos e sobrescreve `income_factor`.
    """

    @property
    def income_factor(self) -> Decimal:
        """O quanto o estado multiplica a renda do mês; 1 deixa a renda da profissão como está."""
        return Decimal(1)

    @property
    def health_factor(self) -> Decimal:
        """Quantas vezes o estado multiplica o imprevisto de saúde; 1 deixa o valor da profissão como está."""
        return Decimal(1)

    @property
    def locked_value(self) -> Decimal:
        """O saldo das contas travadas do jogador, que entra no patrimônio; zero sem conta travada."""
        return Decimal(0)


class CltState(MechanicState):
    """O estado do CLT: a conta do FGTS e a hora extra, ligada ou não."""

    fgts_balance: Decimal = Decimal(0)
    overtime: bool = False

    @property
    def income_factor(self) -> Decimal:
        return 1 + OVERTIME_INCOME_RATE if self.overtime else Decimal(1)

    @property
    def health_factor(self) -> Decimal:
        return OVERTIME_HEALTH_MULTIPLE if self.overtime else Decimal(1)

    @property
    def locked_value(self) -> Decimal:
        return self.fgts_balance


class MechanicAction(BaseDTO):
    """Uma ação do jogador (ou da política do bot) sobre a mecânica; `kind` é o nome dela no histórico da vida."""

    kind: str = Field(min_length=1, max_length=40)


# O nome de cada lançamento da hora extra no histórico da vida
OVERTIME_ON = "overtime_on"
OVERTIME_OFF = "overtime_off"
OVERTIME_ENDED = "overtime_ended"


class SetOvertime(MechanicAction):
    """Liga (`overtime_on`) ou desliga (`overtime_off`) a hora extra do CLT."""

    kind: str = Field(pattern=r"^overtime_(on|off)$")

    @property
    def enabled(self) -> bool:
        return self.kind == OVERTIME_ON


class ProfessionPeriodDTO(BaseDTO):
    """A profissão que o jogador exerce a partir de `start`, até o início do período seguinte."""

    profession: Profession
    start: date


class ProfessionStateDTO(BaseDTO):
    """A profissão do jogador e o estado da mecânica dela."""

    profession: Profession
    state: SerializeAsAny[MechanicState]


# O tipo do estado de cada profissão com mecânica; as demais usam o tipo base
STATE_TYPES: dict[Profession, type[MechanicState]] = {Profession.CLT: CltState}


def state_type_of(profession: Profession) -> type[MechanicState]:
    return STATE_TYPES.get(profession, MechanicState)


def initial_state(profession: Profession) -> MechanicState:
    """O estado de quem começa na profissão: cada campo no valor inicial do tipo."""
    return state_type_of(profession)()


def state_from_json(profession: Profession, data: dict) -> MechanicState:
    return state_type_of(profession).model_validate(data)
