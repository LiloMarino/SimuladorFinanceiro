"""Contas do controle de preço das estatais: pontos de IPCA, teto, degraus bloqueados e represa."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from backend.core.enum import StateControl, StateLever
from backend.core.periods import MONTHS_PER_YEAR

# Quanto do IPCA cada ponto percentual segurado vira, por alavanca
LEVER_WEIGHT: dict[StateLever, Decimal] = {
    StateLever.FUEL: Decimal("0.05"),
    StateLever.ENERGY: Decimal("0.04"),
    StateLever.BANK: Decimal(0),
}

# Quanto o juro do crédito cai por ponto percentual segurado no banco estatal, em ponto
# percentual: P20 tira 1 ponto
CREDIT_WEIGHT: dict[StateLever, Decimal] = {
    StateLever.FUEL: Decimal(0),
    StateLever.ENERGY: Decimal(0),
    StateLever.BANK: Decimal("0.05"),
}

# Soma máxima de pontos de IPCA que as ordens de todas as estatais seguram juntas
IPCA_CAP_POINTS = Decimal("1.5")


@dataclass(frozen=True)
class StepAvailability:
    """Um degrau do controle: os pontos que ele segura e, se passa do teto, o motivo."""

    control: StateControl
    points: Decimal
    blocked_reason: str | None

    @property
    def blocked(self) -> bool:
        return self.blocked_reason is not None


def held_points(lever: StateLever, control: StateControl) -> Decimal:
    """Pontos de IPCA que o degrau segura: percentual do degrau vezes o peso da alavanca."""
    return Decimal(control.percent) * LEVER_WEIGHT[lever]


def credit_points(lever: StateLever, control: StateControl) -> Decimal:
    """Pontos de juro do crédito que o degrau tira: percentual do degrau vezes o peso da alavanca."""
    return Decimal(control.percent) * CREDIT_WEIGHT[lever]


def total_credit_points(orders: Iterable[tuple[StateLever, StateControl]]) -> Decimal:
    """Soma dos pontos de juro do crédito que as ordens em vigor tiram."""
    return sum((credit_points(lever, control) for lever, control in orders), Decimal(0))


def total_held_points(orders: Iterable[tuple[StateLever, StateControl]]) -> Decimal:
    """Soma dos pontos segurados por todas as ordens em vigor."""
    return sum((held_points(lever, control) for lever, control in orders), Decimal(0))


def _points_text(points: Decimal) -> str:
    return f"{points.normalize():f}".replace(".", ",")


def step_availability(
    lever: StateLever, other_points: Decimal
) -> list[StepAvailability]:
    """Os cinco degraus da alavanca, dado o que as outras estatais já seguram.
    Degrau que levaria a soma acima do teto vem bloqueado, com o motivo."""
    steps: list[StepAvailability] = []
    for control in StateControl:
        points = held_points(lever, control)
        reason = None
        if other_points + points > IPCA_CAP_POINTS:
            reason = (
                f"Passaria do teto de {_points_text(IPCA_CAP_POINTS)} ponto de IPCA "
                f"({_points_text(other_points)} já em uso pelas outras estatais)."
            )
        steps.append(StepAvailability(control, points, reason))
    return steps


def inflation_path(held: Sequence[Decimal]) -> list[Decimal]:
    """Efeito mensal no IPCA, em pontos, de uma série de pontos segurados por mês.
    Durante o controle o efeito é o negativo do que se segura e a diferença vai para
    a represa; no primeiro mês sem controle a represa inteira volta de uma vez."""
    path: list[Decimal] = []
    backlog = Decimal(0)
    for points in held:
        if points > 0:
            backlog += points
            path.append(-points)
        else:
            path.append(backlog)
            backlog = Decimal(0)
    return path


def price_level_points(annualized: Decimal) -> Decimal:
    """Pontos de nível de preços de uma soma de pontos anualizados: o IPCA de 12 meses acumula 12 meses."""
    return annualized / MONTHS_PER_YEAR


def backlog_points(held: Sequence[Decimal]) -> Decimal:
    """Inflação represada hoje, em pontos de nível de preços: o que se segurou desde o último mês sem controle."""
    backlog = Decimal(0)
    for points in held:
        backlog = backlog + points if points > 0 else Decimal(0)
    return price_level_points(backlog)
