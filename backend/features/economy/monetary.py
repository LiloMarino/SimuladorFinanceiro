"""
A política monetária da partida: o calendário das reuniões do Copom, o teto de cada
decisão, o efeito defasado do juro real na inflação e a credibilidade do Banco Central.
As decisões tomadas ficam no quadro da SELIC; sem nenhuma, a SELIC é a do Banco Central
autônomo e a credibilidade fica cheia. Os números calibram no playtest.
"""

from bisect import bisect_left
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from typing import Protocol

from backend.core.utils import is_business_day, next_business_day

# O Copom se reúne 8 vezes por ano, a cada 45 dias; a reunião cai no dia útil seguinte
MEETINGS_PER_YEAR = 8
MEETING_SPACING_DAYS = 45
# A SELIC anda em passos de 0,25 ponto, até 0,75 por reunião. Com o IPCA em 12 meses acima
# do teto da meta o passo vai a 1,5; acima de 15%, a 3 (o Copom de 2021 subiu 1,5 por reunião)
SELIC_STEP = Decimal("0.0025")
NORMAL_CAP = Decimal("0.0075")
TOLERANCE_CAP = Decimal("0.015")
CRISIS_CAP = Decimal("0.03")
CRISIS_INFLATION = Decimal("0.15")

# Cada ponto de juro real abaixo da história soma 0,3 ponto ao IPCA em 12 meses, um ano
# depois (a ordem de grandeza do modelo Samba do Banco Central). O efeito de cada mês se
# espalha pelos 12 meses seguintes, com o pico no 2º e no 3º trimestres
RATE_INFLATION = 0.3
LAG_MONTHS = 12
QUARTER_WEIGHTS = (0.15, 0.35, 0.35, 0.15)
# Sem credibilidade, o mercado reajusta preço antes: o peso vai para o 1º e o 2º trimestres
HURRIED_WEIGHTS = (0.35, 0.35, 0.2, 0.1)

FULL_CREDIBILITY = 100.0
# Cada reunião com o juro real abaixo do da história e o IPCA acima da meta mais a
# tolerância tira 4 pontos de credibilidade por ponto abaixo da história, até 20; cada
# alta da SELIC, ou juro real na história, devolve 3. A SELIC decide em passos de 0,25 e
# a da história é fracionária: meio passo de diferença ainda é a história
CREDIBILITY_LOSS = 4.0
MAX_CREDIBILITY_LOSS = 20.0
CREDIBILITY_GAIN = 3.0
HISTORY_MARGIN = SELIC_STEP / 2
# Sem credibilidade nenhuma, a dívida paga 2 pontos de prêmio a mais
CREDIBILITY_PREMIUM = Decimal("0.02")


def meeting_days(year: int) -> list[date]:
    """As reuniões do ano: os dias 45, 90, …, 360, no dia útil seguinte quando caem no fim de semana."""
    first = date(year, 1, 1)
    days = (
        first + timedelta(days=MEETING_SPACING_DAYS * k - 1)
        for k in range(1, MEETINGS_PER_YEAR + 1)
    )
    return [d if is_business_day(d) else next_business_day(d) for d in days]


def next_meeting(day: date) -> date:
    """A primeira reunião em `day` ou depois."""
    for year in (day.year, day.year + 1):
        for meeting in meeting_days(year):
            if meeting >= day:
                return meeting
    raise AssertionError("o ano seguinte sempre tem reunião")


def is_meeting_day(day: date) -> bool:
    return day in meeting_days(day.year)


def meeting_cap(ipca: Decimal, target: Decimal, tolerance: Decimal) -> Decimal:
    """O quanto a SELIC pode andar numa reunião com o IPCA em 12 meses `ipca` (frações)."""
    if ipca > CRISIS_INFLATION:
        return CRISIS_CAP
    if ipca > target + tolerance:
        return TOLERANCE_CAP
    return NORMAL_CAP


def to_step(selic: Decimal) -> Decimal:
    """A taxa no passo de 0,25 ponto mais próximo."""
    return (selic / SELIC_STEP).quantize(Decimal(1), ROUND_HALF_UP) * SELIC_STEP


def cap_window(current: Decimal, cap: Decimal) -> tuple[Decimal, Decimal]:
    """
    Os passos de 0,25 que a reunião alcança: a SELIC guardada é a efetiva (13,65% com a meta
    em 13,75%), fora da grade, e a janela fica nos passos dentro de `cap` dela, sem passar de zero.
    """
    low = ((current - cap) / SELIC_STEP).quantize(
        Decimal(1), ROUND_CEILING
    ) * SELIC_STEP
    high = ((current + cap) / SELIC_STEP).quantize(Decimal(1), ROUND_FLOOR) * SELIC_STEP
    return max(Decimal(0), low), high


def within_cap(wanted: Decimal, current: Decimal, cap: Decimal) -> Decimal:
    """A taxa pedida no passo de 0,25 mais próximo dentro da janela da reunião."""
    low, high = cap_window(current, cap)
    return max(low, min(high, to_step(wanted)))


def lag_weights(credibility: float) -> tuple[float, ...]:
    """O peso de cada um dos 12 meses de defasagem, do 1º ao 12º; somam 1."""
    hurry = (FULL_CREDIBILITY - credibility) / FULL_CREDIBILITY
    quarters = [
        (1 - hurry) * calm + hurry * hurried
        for calm, hurried in zip(QUARTER_WEIGHTS, HURRIED_WEIGHTS, strict=True)
    ]
    return tuple(quarter / 3 for quarter in quarters for _ in range(3))


def rate_inflation_points(gaps: Sequence[Decimal], credibility: float) -> float:
    """
    Os pontos de IPCA em 12 meses que o juro real soma no mês seguinte. `gaps` é o juro
    real da partida menos o da história em cada mês fechado, do mais antigo ao mais
    novo, em fração; o mais novo pesa como defasagem de 1 mês. Credibilidade baixa
    multiplica o efeito, até o dobro em zero.
    """
    weights = lag_weights(credibility)
    recent = list(reversed(gaps[-LAG_MONTHS:]))
    points = sum(
        -float(gap) * 100 * weight for gap, weight in zip(recent, weights, strict=False)
    )
    multiplier = 1 + (FULL_CREDIBILITY - credibility) / FULL_CREDIBILITY
    return RATE_INFLATION * points * multiplier


def next_credibility(
    credibility: float,
    real_rate: Decimal,
    history_real_rate: Decimal,
    ipca: Decimal,
    target: Decimal,
    tolerance: Decimal,
    *,
    raised: bool,
) -> float:
    """
    A credibilidade depois de uma reunião, de 0 a 100. O juro real da partida abaixo do
    da história com o IPCA em 12 meses acima da meta mais a tolerância custa caro; subir
    a SELIC ou manter o juro real da história devolve um pouco por vez.
    """
    below = history_real_rate - real_rate
    if below > HISTORY_MARGIN and not raised:
        if ipca > target + tolerance:
            credibility -= min(
                MAX_CREDIBILITY_LOSS, CREDIBILITY_LOSS * float(below) * 100
            )
    else:
        credibility += CREDIBILITY_GAIN
    return round(max(0.0, min(FULL_CREDIBILITY, credibility)), 2)


def credibility_premium(credibility: float) -> Decimal:
    """O prêmio de risco que a dívida paga a mais pela credibilidade perdida, em fração."""
    lost = Decimal(str((FULL_CREDIBILITY - credibility) / FULL_CREDIBILITY))
    return CREDIBILITY_PREMIUM * lost


@dataclass(frozen=True)
class SelicDecision:
    """A SELIC anual que uma reunião fixou (fração) e a credibilidade depois dela; valem do dia seguinte."""

    day: date
    selic: Decimal
    credibility: float


class Monetary(Protocol):
    """
    A SELIC que o governo fixou e a credibilidade em cada dia, desde o primeiro dia em
    que alguma decisão vale; SELIC nula é a do Banco Central autônomo.
    """

    def first_day(self) -> date | None: ...

    def selic_on(self, day: date) -> Decimal | None: ...

    def credibility_on(self, day: date) -> float: ...


class SelicBoard:
    """
    As decisões das reuniões em ordem. Cada uma vale a partir do dia seguinte ao da
    reunião, porque os preços do dia saem antes de o governo agir nele. Lê sem trava:
    a lista das decisões cresce antes da dos dias.
    """

    def __init__(self) -> None:
        self._decisions: list[SelicDecision] = []
        self._days: list[date] = []

    def record(self, decision: SelicDecision) -> None:
        self._decisions.append(decision)
        self._days.append(decision.day)

    def clear(self) -> None:
        self._days = []
        self._decisions = []

    def first_day(self) -> date | None:
        return self._days[0] + timedelta(days=1) if self._days else None

    def decisions(self) -> list[SelicDecision]:
        return list(self._decisions)

    def last_before(self, day: date) -> SelicDecision | None:
        index = bisect_left(self._days, day)
        return self._decisions[index - 1] if index else None

    def selic_on(self, day: date) -> Decimal | None:
        last = self.last_before(day)
        return None if last is None else last.selic

    def credibility_on(self, day: date) -> float:
        last = self.last_before(day)
        return FULL_CREDIBILITY if last is None else last.credibility


class AutonomousBank:
    """O Banco Central autônomo: nenhuma SELIC fixada e credibilidade cheia."""

    def first_day(self) -> date | None:
        return None

    def selic_on(self, day: date) -> Decimal | None:
        return None

    def credibility_on(self, day: date) -> float:
        return FULL_CREDIBILITY
