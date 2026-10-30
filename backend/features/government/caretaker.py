"""
O governo do computador depois de um impeachment sem vice: assume o partido do computador
com mais cadeiras na casa, e ele propõe uma medida por vez, a que os grupos de eleitores da
bancada dele mais querem. Cada tipo de medida anda no máximo um passo por governo, então a
fila do computador acaba quando ele já tentou tudo o que os eleitores dele querem. A casa
vota como vota qualquer medida. Tudo aqui é função pura; o livro do governo emite os eventos.
"""

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from decimal import Decimal

from backend.core.enum import MeasureKind, VoterGroup
from backend.features.government import house, promises, voters

ZERO = Decimal(0)


@dataclass(frozen=True)
class Choice:
    """A medida que o governo do computador propõe: o tipo, o valor novo e o que valia."""

    kind: MeasureKind
    value: Decimal
    before: Decimal
    # Quanto a bancada quer a medida: a reação de cada grupo, pesada pela composição dela
    score: Decimal


def successor(
    current: house.House, computer_parties: Collection[int]
) -> house.Bloc | None:
    """
    A bancada do computador que assume: a de mais cadeiras entre as que têm partido na
    partida; no empate, a que vem primeiro na lista do computador (UPR, MNV, ACI).
    """
    seated = [
        bloc
        for bloc in current.seated
        if bloc.is_computer and bloc.party_id in computer_parties
    ]
    if not seated:
        return None
    # As chaves do computador são -1, -2 e -3, na ordem da lista
    return max(seated, key=lambda bloc: (bloc.seats, bloc.key))


def wanted(
    mix: Mapping[VoterGroup, Decimal],
    kind: MeasureKind,
    value: Decimal,
    before: Decimal,
) -> Decimal:
    """Quanto os eleitores da bancada querem a medida: positivo quer, negativo não quer."""
    return sum(
        (
            share * voters.measure_reaction(group, kind, value, before)
            for group, share in mix.items()
        ),
        ZERO,
    )


def pick(
    mix: Mapping[VoterGroup, Decimal],
    baselines: Mapping[MeasureKind, Decimal],
    tried: Collection[MeasureKind],
) -> Choice | None:
    """
    Das medidas gerais, um passo de referência para cima ou para baixo do valor em vigor,
    a que os eleitores da bancada mais querem. `tried` traz os tipos que este governo já
    levou à votação; sem nenhuma medida que eles queiram, o governo não propõe.
    """
    best: Choice | None = None
    for kind, before in sorted(baselines.items(), key=lambda item: item[0].value):
        if kind in tried:
            continue
        step = voters.EFFECT_STEPS[kind]
        limit = promises.limit_of(kind)
        for value in (before - step, before + step):
            if value < 0 or (limit is not None and value > limit):
                continue
            score = wanted(mix, kind, value, before)
            if score > 0 and (best is None or score > best.score):
                best = Choice(kind, value, before, score)
    return best
