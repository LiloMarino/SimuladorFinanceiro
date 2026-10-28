"""
As ações avulsas de campanha e o dado: preço, faixas do d20, ganho de cada ação, retorno
decrescente, reparação de rejeição e a queda do apoio com o tempo. Tudo aqui é função
pura sobre números; o estado da partida guarda o resultado de cada ação.
"""

import random
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from functools import cache

from backend.core.enum import CampaignActionKind, DiceBand, VoterGroup
from backend.core.indicators import inflation_factor

K = CampaignActionKind
B = DiceBand

ZERO = Decimal(0)
CENT = Decimal("0.01")

# Todo apoio de campanha (verba, doações e ações) cai pela metade em 3 meses
HALF_LIFE_DAYS = 91

# Preço fixo em reais de cada ação, para uma verba de referência de R$ 10 mil por mês
# em cada partido; com a correção pela inflação ligada, sobe pelo IPCA a cada aniversário
PRICES: dict[CampaignActionKind, Decimal] = {
    K.TV: Decimal(6000),
    K.EVENT: Decimal(2500),
    K.RALLY: Decimal(800),
    K.ATTACK: Decimal(2500),
}

# Pontos de apoio que a ação rende na faixa normal, em cada grupo que ela atinge
NORMAL_GAIN: dict[CampaignActionKind, Decimal] = {
    K.TV: Decimal("0.75"),
    K.EVENT: Decimal("1.5"),
    K.RALLY: Decimal("0.5"),
    K.ATTACK: Decimal("1.5"),
}

# A faixa de cada número do d20 e quantas vezes o ganho normal ela vale. O desastre
# perde o dobro; o ataque que sai pela culatra soma esse valor de rejeição a quem atacou
BANDS: tuple[tuple[DiceBand, int, int, Decimal], ...] = (
    (B.DISASTER, 1, 1, Decimal(-2)),
    (B.WEAK, 2, 6, Decimal("0.5")),
    (B.NORMAL, 7, 14, Decimal(1)),
    (B.GOOD, 15, 19, Decimal("1.5")),
    (B.VIRAL, 20, 20, Decimal(3)),
)

# O comício dobra os extremos: o desastre perde 4 vezes o ganho e o viral rende 6
RALLY_EXTREMES = Decimal(2)

# O evento repara 1 ponto da rejeição do partido no grupo (fora o desastre), até 6 por
# campanha em cada grupo
EVENT_REPAIR = Decimal(1)
EVENT_REPAIR_LIMIT = Decimal(6)

# Cada repetição da mesma ação no mesmo grupo, no mês, rende metade da anterior
REPEAT_KEEP = Decimal("0.5")

# O partido do computador gasta esta fatia da verba mensal em ações e contribui com o resto
COMPUTER_ACTION_SHARE = Decimal("0.6")

DICE_SIDES = 20


@dataclass(frozen=True)
class Band:
    """Uma faixa do dado vista de uma ação: onde cai, com que chance e o que muda."""

    band: DiceBand
    first_roll: int
    last_roll: int
    chance: Decimal
    # Mudança do apoio de quem a ação atinge (o próprio partido, ou o rival no ataque)
    support: Decimal
    # Mudança da rejeição do partido que age, no grupo: negativa repara, positiva é a culatra
    rejection: Decimal


@dataclass(frozen=True)
class Outcome:
    """O que uma ação rolada fez: a faixa, o retorno e as mudanças aplicadas."""

    roll: int
    band: DiceBand
    rate: Decimal
    support: Decimal
    rejection: Decimal


def price(
    kind: CampaignActionKind, start: date, day: date, inflation_adjusted: bool
) -> Decimal:
    """O preço da ação no dia, em reais e centavos."""
    factor = inflation_factor(start, day) if inflation_adjusted else Decimal(1)
    return (PRICES[kind] * factor).quantize(CENT, rounding=ROUND_HALF_EVEN)


@cache
def decay_factor(days: int) -> Decimal:
    """Quanto do apoio de campanha sobra depois de `days` dias: metade em 3 meses."""
    if days <= 0:
        return Decimal(1)
    return Decimal(2) ** (-Decimal(days) / HALF_LIFE_DAYS)


def roll_dice(seed: int, action_id: int, kind: CampaignActionKind) -> tuple[int, ...]:
    """Os dados da ação, sorteados pela semente da partida; a TV rola dois."""
    rng = random.Random(f"{seed}:campaign:{action_id}")
    count = 2 if kind is K.TV else 1
    return tuple(rng.randint(1, DICE_SIDES) for _ in range(count))


def chosen_roll(kind: CampaignActionKind, rolls: tuple[int, ...]) -> int:
    """A TV vale o maior de dois dados; as outras ações, o único."""
    return max(rolls) if kind is K.TV else rolls[0]


def band_of(roll: int) -> DiceBand:
    return next(band for band, first, last, _ in BANDS if first <= roll <= last)


def repeat_rate(uses: int) -> Decimal:
    """Retorno da mesma ação no mesmo grupo no mês: 100%, 50%, 25%..."""
    return REPEAT_KEEP**uses


def _multiplier(kind: CampaignActionKind, band: DiceBand) -> Decimal:
    value = next(m for b, _, _, m in BANDS if b is band)
    if kind is K.RALLY and band in (B.DISASTER, B.VIRAL):
        return value * RALLY_EXTREMES
    return value


def _chance(kind: CampaignActionKind, first: int, last: int) -> Decimal:
    """Chance de o dado cair entre `first` e `last`; na TV, do maior dos dois."""
    faces = last - first + 1
    if kind is not K.TV:
        return Decimal(faces) / DICE_SIDES
    return Decimal(last**2 - (first - 1) ** 2) / DICE_SIDES**2


def outcome(
    kind: CampaignActionKind,
    rolls: tuple[int, ...],
    uses: int,
    repair_left: Decimal,
    rejection_now: Decimal,
) -> Outcome:
    """
    O efeito da ação: `uses` é quantas vezes o partido já fez a mesma ação no mesmo
    grupo no mês; `repair_left` e `rejection_now` limitam o que o evento repara.
    """
    roll = chosen_roll(kind, rolls)
    band = band_of(roll)
    rate = repeat_rate(uses)
    gain = NORMAL_GAIN[kind] * _multiplier(kind, band) * rate
    support, rejection = gain, ZERO
    if kind is K.ATTACK:
        # O ataque tira do rival; o tiro que sai pela culatra soma rejeição a quem atacou
        support, rejection = (ZERO, -gain) if band is B.DISASTER else (-gain, ZERO)
    elif kind is K.EVENT and band is not B.DISASTER:
        rejection = -max(ZERO, min(EVENT_REPAIR, repair_left, rejection_now))
    return Outcome(roll, band, rate, support, rejection)


def table(
    kind: CampaignActionKind, uses: int, repair_left: Decimal, rejection_now: Decimal
) -> list[Band]:
    """As cinco faixas de uma ação antes de rolar, com a chance e o efeito de cada uma."""
    bands = []
    for band, first, last, _ in BANDS:
        # Qualquer número da faixa dá o mesmo efeito
        result = outcome(
            kind,
            (first,) * (2 if kind is K.TV else 1),
            uses,
            repair_left,
            rejection_now,
        )
        bands.append(
            Band(
                band=band,
                first_roll=first,
                last_roll=last,
                chance=_chance(kind, first, last),
                support=result.support,
                rejection=result.rejection,
            )
        )
    return bands


def average(bands: list[Band]) -> Decimal:
    """O efeito médio no apoio de quem a ação atinge, ponderado pela chance de cada faixa."""
    return sum((b.chance * b.support for b in bands), ZERO)


def eligible_groups(kind: CampaignActionKind) -> list[VoterGroup | None]:
    """Onde a ação se aplica: a TV atinge todos de uma vez; as outras escolhem um grupo."""
    return [None] if kind is K.TV else list(VoterGroup)
