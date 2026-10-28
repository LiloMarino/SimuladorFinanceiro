"""
O eleitorado em grupos: o que cada grupo quer, o perfil de cada partido, o apoio e a
rejeição de cada partido em cada grupo e o voto que sai deles. É o contrato em que a
aprovação, as ações de campanha, as promessas e o 2º turno se apoiam. Tudo aqui é
função pura sobre números; o estado da partida guarda o resultado.
"""

import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import (
    GroupReading,
    GroupVerdict,
    MeasureKind,
    VoterGroup,
    VoterValue,
)

G = VoterGroup
V = VoterValue

HUNDRED = Decimal(100)
ZERO = Decimal(0)

# Fatia de cada grupo no eleitorado
WEIGHTS: dict[VoterGroup, Decimal] = {
    G.INVESTORS: Decimal("0.08"),
    G.ENTREPRENEURS: Decimal("0.12"),
    G.FORMAL_WORKERS: Decimal("0.35"),
    G.PUBLIC_SERVANTS: Decimal("0.10"),
    G.RETIREES: Decimal("0.20"),
    G.WELFARE: Decimal("0.15"),
}

# Quanto cada grupo quer cada valor, de -1 (rejeita) a +1 (quer)
POSITIONS: dict[VoterGroup, dict[VoterValue, Decimal]] = {
    G.INVESTORS: {
        V.FREE_MARKET: Decimal(1),
        V.SOCIAL_JUSTICE: Decimal(-1),
        V.STABILITY: Decimal("0.5"),
        V.DEVELOPMENT: Decimal("0.3"),
        V.SAVER_PROTECTION: Decimal("0.5"),
        V.PUBLIC_SERVICE: Decimal("-0.5"),
    },
    G.ENTREPRENEURS: {
        V.FREE_MARKET: Decimal("0.8"),
        V.SOCIAL_JUSTICE: Decimal("-0.5"),
        V.STABILITY: Decimal("0.3"),
        V.DEVELOPMENT: Decimal(1),
        V.SAVER_PROTECTION: ZERO,
        V.PUBLIC_SERVICE: Decimal("-0.5"),
    },
    G.FORMAL_WORKERS: {
        V.FREE_MARKET: Decimal("-0.2"),
        V.SOCIAL_JUSTICE: Decimal("0.5"),
        V.STABILITY: Decimal("0.6"),
        V.DEVELOPMENT: Decimal("0.5"),
        V.SAVER_PROTECTION: Decimal("0.2"),
        V.PUBLIC_SERVICE: ZERO,
    },
    G.PUBLIC_SERVANTS: {
        V.FREE_MARKET: Decimal("-0.6"),
        V.SOCIAL_JUSTICE: Decimal("0.4"),
        V.STABILITY: Decimal("0.3"),
        V.DEVELOPMENT: ZERO,
        V.SAVER_PROTECTION: Decimal("0.2"),
        V.PUBLIC_SERVICE: Decimal(1),
    },
    G.RETIREES: {
        V.FREE_MARKET: ZERO,
        V.SOCIAL_JUSTICE: Decimal("0.2"),
        V.STABILITY: Decimal(1),
        V.DEVELOPMENT: Decimal("-0.2"),
        V.SAVER_PROTECTION: Decimal(1),
        V.PUBLIC_SERVICE: Decimal("0.3"),
    },
    G.WELFARE: {
        V.FREE_MARKET: Decimal("-0.8"),
        V.SOCIAL_JUSTICE: Decimal(1),
        V.STABILITY: Decimal("0.5"),
        V.DEVELOPMENT: Decimal("0.2"),
        V.SAVER_PROTECTION: Decimal("-0.3"),
        V.PUBLIC_SERVICE: Decimal("0.3"),
    },
}

# Os resultados do governo que mais pesam para cada grupo, na ordem em que pesam
READINGS: dict[VoterGroup, tuple[GroupReading, ...]] = {
    G.INVESTORS: (GroupReading.STOCKS, GroupReading.INFLATION),
    G.ENTREPRENEURS: (GroupReading.SELIC, GroupReading.STOCKS),
    G.FORMAL_WORKERS: (GroupReading.INFLATION, GroupReading.SELIC),
    G.PUBLIC_SERVANTS: (GroupReading.INFLATION, GroupReading.CAPITAL_GAINS_TAX),
    G.RETIREES: (GroupReading.INFLATION, GroupReading.SELIC),
    G.WELFARE: (GroupReading.INFLATION,),
}

# Margem de erro da pesquisa em pontos: cresce nos grupos menores, de amostra menor
TOTAL_MARGIN = 3
MARGINS: dict[VoterGroup, int] = {
    G.INVESTORS: 11,
    G.ENTREPRENEURS: 9,
    G.FORMAL_WORKERS: 5,
    G.PUBLIC_SERVANTS: 10,
    G.RETIREES: 7,
    G.WELFARE: 8,
}

# Bandeiras: 3 por partido, e Mercado livre e Justiça social não andam juntas
FLAGS_PER_PARTY = 3
EXCLUSIVE = frozenset({V.FREE_MARKET, V.SOCIAL_JUSTICE})

# Perfil de 0 a 100: o valor que o partido não defende fica no neutro, a bandeira no
# alto; a afinidade conta quanto cada valor está acima do neutro, em bandeiras inteiras
RADAR_NEUTRAL = Decimal(30)
RADAR_FLAG = Decimal(80)
# Pontos de perfil por unidade de efeito da medida aprovada (cortar o day trade em
# 10 pontos move Mercado livre em +6)
RADAR_PER_EFFECT = Decimal(6)

# Afinidade = 20 + 12 x a soma das posições do grupo nas bandeiras, nunca abaixo de 0
AFFINITY_BASE = Decimal(20)
AFFINITY_PER_POSITION = Decimal(12)

# Pontos de apoio por gasto de campanha, em cada grupo: R$ 8 mil num mês dão
# √8000 ÷ 64 = 1,4 ponto. Rende pela raiz, então dobrar a verba não dobra o apoio
SQRT_DIVISOR = Decimal(64)

# Os indecisos entram na divisão de cada grupo como um partido de saldo fixo: com dois
# partidos de saldo 30 e 25, 15 ÷ 70 = 21% do grupo fica indeciso
UNDECIDED_BALANCE = Decimal(15)

# Faixa neutra da satisfação: acima de 55 o grupo aprova o mês, abaixo de 45 reprova e,
# entre as duas, o mês passa em branco
APPROVES_ABOVE = Decimal(55)
REPROVES_BELOW = Decimal(45)
# Mês aprovado: +1 de apoio ao partido do governo e -0,25 de rejeição; mês reprovado:
# -1 de apoio e +0,5 de rejeição
APPROVED_SUPPORT = Decimal(1)
APPROVED_REPAIR = Decimal("0.25")
REPROVED_SUPPORT = Decimal(-1)
REPROVED_REJECTION = Decimal("0.5")
# O apoio que o mandato dá cai pela metade em 3 meses: a cada mês sobra 0,5 ** (1/3)
SUPPORT_MONTHLY_KEEP = Decimal("0.5") ** (Decimal(1) / 3)

# O que cada tipo de medida avança ou recua nos valores, por passo de referência; o
# passo no sentido contrário (subir o que a tabela corta) tem o efeito inverso
EFFECT_STEPS: dict[MeasureKind, Decimal] = {
    MeasureKind.STOCK_PROFIT_RATE: Decimal("0.05"),
    MeasureKind.DAY_TRADE_RATE: Decimal("0.10"),
    MeasureKind.STOCK_EXEMPTION: Decimal(20000),
    MeasureKind.FIXED_INCOME_TABLE: Decimal("0.05"),
    MeasureKind.LCI_LCA_RATE: Decimal("0.15"),
    MeasureKind.SECTOR_TAX: Decimal("0.05"),
}
EFFECTS: dict[MeasureKind, dict[VoterValue, Decimal]] = {
    # Por corte de 5 pontos no IR do ganho comum
    MeasureKind.STOCK_PROFIT_RATE: {
        V.FREE_MARKET: Decimal(1),
        V.SOCIAL_JUSTICE: Decimal(-1),
        V.DEVELOPMENT: Decimal("0.3"),
    },
    # Por corte de 10 pontos no day trade
    MeasureKind.DAY_TRADE_RATE: {
        V.FREE_MARKET: Decimal(1),
        V.SOCIAL_JUSTICE: Decimal("-0.5"),
    },
    # Por R$ 20 mil a mais na isenção das vendas
    MeasureKind.STOCK_EXEMPTION: {
        V.FREE_MARKET: Decimal("0.5"),
        V.SOCIAL_JUSTICE: Decimal("-0.5"),
        V.SAVER_PROTECTION: Decimal("0.5"),
    },
    # Por corte de 5 pontos no IR da renda fixa
    MeasureKind.FIXED_INCOME_TABLE: {
        V.FREE_MARKET: Decimal("0.5"),
        V.SOCIAL_JUSTICE: Decimal("-0.5"),
        V.SAVER_PROTECTION: Decimal(1),
    },
    # Por 15 pontos de IR em LCI e LCA
    MeasureKind.LCI_LCA_RATE: {
        V.SOCIAL_JUSTICE: Decimal("0.5"),
        V.DEVELOPMENT: Decimal("-0.3"),
        V.SAVER_PROTECTION: Decimal(-1),
    },
    MeasureKind.SECTOR_EXEMPT: {
        V.FREE_MARKET: Decimal("0.3"),
        V.SOCIAL_JUSTICE: Decimal("-0.5"),
        V.DEVELOPMENT: Decimal(1),
    },
}
# Na tabela, o passo positivo de cada tipo: corte de alíquota, teto maior, imposto novo
_CUT_IS_POSITIVE = frozenset(
    {
        MeasureKind.STOCK_PROFIT_RATE,
        MeasureKind.DAY_TRADE_RATE,
        MeasureKind.FIXED_INCOME_TABLE,
    }
)


@dataclass(frozen=True)
class Standing:
    """O que um grupo acha de um partido, de 0 a 100."""

    support: Decimal
    rejection: Decimal

    @property
    def balance(self) -> Decimal:
        """O saldo é o que decide o voto: apoio menos rejeição."""
        return self.support - self.rejection


@dataclass(frozen=True)
class GroupVote:
    """Em cada 100 eleitores do grupo, quantos votariam em cada partido."""

    shares: dict[int, Decimal]
    undecided: Decimal


@dataclass(frozen=True)
class Vote:
    groups: dict[VoterGroup, GroupVote]
    # Em cada 100 eleitores do país: a soma dos grupos pelo peso de cada um
    total: dict[int, Decimal]
    undecided: Decimal


def is_valid_flags(values: Iterable[VoterValue]) -> bool:
    flags = list(values)
    chosen = set(flags)
    return (
        len(flags) == FLAGS_PER_PARTY
        and len(chosen) == FLAGS_PER_PARTY
        and not EXCLUSIVE.issubset(chosen)
    )


def initial_radar(flags: Iterable[VoterValue] | None) -> dict[VoterValue, Decimal]:
    """O perfil na fundação; sem bandeiras, neutro em tudo."""
    chosen = set(flags or ())
    return {v: RADAR_FLAG if v in chosen else RADAR_NEUTRAL for v in V}


def clamp(value: Decimal, low: Decimal = ZERO, high: Decimal = HUNDRED) -> Decimal:
    return max(low, min(high, value))


def affinity_weight(score: Decimal) -> Decimal:
    """Quanto do valor o partido defende, em bandeiras: neutro é 0, bandeira é 1."""
    return (score - RADAR_NEUTRAL) / (RADAR_FLAG - RADAR_NEUTRAL)


def affinity(group: VoterGroup, radar: Mapping[VoterValue, Decimal]) -> Decimal:
    """A proximidade entre o que o grupo quer e o perfil do partido."""
    positions = POSITIONS[group]
    total = sum(
        (positions[v] * affinity_weight(score) for v, score in radar.items()),
        ZERO,
    )
    return max(ZERO, AFFINITY_BASE + AFFINITY_PER_POSITION * total)


def campaign_points(amount: Decimal) -> Decimal:
    """Pontos de apoio que um gasto de `amount` rende em cada grupo."""
    return amount.sqrt() / SQRT_DIVISOR if amount > 0 else ZERO


def standing(
    group: VoterGroup,
    radar: Mapping[VoterValue, Decimal],
    campaign: Decimal,
    rejection: Decimal,
) -> Standing:
    """O apoio parte da afinidade e soma a campanha; a rejeição vem guardada."""
    return Standing(
        support=clamp(affinity(group, radar) + campaign),
        rejection=rejection,
    )


def add_rejection(current: Decimal, amount: Decimal) -> Decimal:
    """A rejeição sobe com promessa descumprida e mês reprovado, até 100."""
    return clamp(current + amount)


def repair_rejection(current: Decimal, amount: Decimal) -> Decimal:
    """A rejeição só cai por reparação, até zero; o tempo sozinho não a mexe."""
    return clamp(current - amount)


def group_vote(balances: Mapping[int, Decimal]) -> GroupVote:
    """A fatia de cada partido no grupo é proporcional ao saldo positivo dele."""
    positive = {pid: max(ZERO, b) for pid, b in balances.items()}
    total = sum(positive.values(), ZERO) + UNDECIDED_BALANCE
    return GroupVote(
        shares={pid: b * HUNDRED / total for pid, b in positive.items()},
        undecided=UNDECIDED_BALANCE * HUNDRED / total,
    )


def vote(standings: Mapping[int, Mapping[VoterGroup, Standing]]) -> Vote:
    """O voto de cada grupo e o total, somado pelo peso de cada grupo."""
    groups = {
        g: group_vote({pid: s[g].balance for pid, s in standings.items()}) for g in G
    }
    return combine(groups)


def restrict(result: Vote, finalists: Iterable[int]) -> Vote:
    """
    O voto só entre os finalistas: em cada grupo, os eleitores de quem saiu se dividem
    entre os finalistas e os indecisos na mesma proporção em que estes já estão.
    """
    kept = list(finalists)
    groups = {}
    for g, gv in result.groups.items():
        shares = {pid: gv.shares.get(pid, ZERO) for pid in kept}
        total = sum(shares.values(), ZERO) + gv.undecided
        scale = HUNDRED / total if total > 0 else ZERO
        groups[g] = GroupVote(
            shares={pid: s * scale for pid, s in shares.items()},
            undecided=gv.undecided * scale if total > 0 else HUNDRED,
        )
    return combine(groups)


def combine(groups: dict[VoterGroup, GroupVote]) -> Vote:
    """O total do país a partir do voto de cada grupo, somado pelo peso do grupo."""
    parties = {pid for gv in groups.values() for pid in gv.shares}
    total = {
        pid: sum(
            (WEIGHTS[g] * gv.shares.get(pid, ZERO) for g, gv in groups.items()), ZERO
        )
        for pid in parties
    }
    undecided = sum((WEIGHTS[g] * gv.undecided for g, gv in groups.items()), ZERO)
    return Vote(groups=groups, total=total, undecided=undecided)


def month_verdict(satisfaction: Decimal) -> GroupVerdict:
    """Se o grupo aprova, reprova ou fica neutro no fechamento do mês."""
    if satisfaction > APPROVES_ABOVE:
        return GroupVerdict.APPROVES
    if satisfaction < REPROVES_BELOW:
        return GroupVerdict.REPROVES
    return GroupVerdict.NEUTRAL


def remember_month(
    support: Decimal, rejection: Decimal, verdict: GroupVerdict
) -> tuple[Decimal, Decimal]:
    """
    O que o mês do governo deixa para o partido do presidente num grupo: o apoio que já
    havia perde parte pelo tempo e soma ou tira 1 conforme o veredito; a rejeição
    repara no mês aprovado e sobe no reprovado.
    """
    kept = support * SUPPORT_MONTHLY_KEEP
    match verdict:
        case GroupVerdict.APPROVES:
            return kept + APPROVED_SUPPORT, repair_rejection(rejection, APPROVED_REPAIR)
        case GroupVerdict.REPROVES:
            return kept + REPROVED_SUPPORT, add_rejection(rejection, REPROVED_REJECTION)
        case GroupVerdict.NEUTRAL:
            return kept, rejection


def published(
    exact: Decimal, margin: int, seed: int, day: date, key: str, party_id: int
) -> Decimal:
    """
    O número que a pesquisa publica: o exato com um erro sorteado pela semente da
    partida, sempre dentro da margem. A mesma pesquisa sai igual para todos e em toda
    retomada.
    """
    rng = random.Random(f"{seed}:{day.isoformat()}:{key}:{party_id}")
    error = max(-margin, min(margin, rng.gauss(0, margin / 2)))
    return clamp(exact + Decimal(str(round(error, 2))))


def measure_steps(
    kind: MeasureKind, value: Decimal | None, before: Decimal | None
) -> Decimal:
    """Quantos passos de referência a medida anda, no sentido positivo da tabela."""
    if kind is MeasureKind.SECTOR_EXEMPT:
        return Decimal(1)
    reference = EFFECT_STEPS[kind]
    if kind is MeasureKind.SECTOR_TAX:
        return (value or ZERO) / reference
    change = (value or ZERO) - (before or ZERO)
    return (-change if kind in _CUT_IS_POSITIVE else change) / reference


def measure_effects(
    kind: MeasureKind, value: Decimal | None, before: Decimal | None
) -> dict[VoterValue, Decimal]:
    """O quanto a medida avança (positivo) ou recua cada valor."""
    steps = measure_steps(kind, value, before)
    # Taxar um setor é o inverso de isentá-lo
    table = EFFECTS[
        MeasureKind.SECTOR_EXEMPT if kind is MeasureKind.SECTOR_TAX else kind
    ]
    sign = Decimal(-1) if kind is MeasureKind.SECTOR_TAX else Decimal(1)
    return {v: sign * effect * steps for v, effect in table.items()}


def reaction(group: VoterGroup, effects: Mapping[VoterValue, Decimal]) -> Decimal:
    """Quanto o grupo quer o que a medida faz: a posição dele em cada valor vezes o que a medida move."""
    positions = POSITIONS[group]
    return sum((positions[v] * effect for v, effect in effects.items()), ZERO)


def radar_moves(
    kind: MeasureKind, value: Decimal | None, before: Decimal | None
) -> dict[VoterValue, Decimal]:
    """Quanto a medida aprovada move o perfil do partido do governo, em pontos inteiros."""
    moves = {}
    for v, effect in measure_effects(kind, value, before).items():
        points = (effect * RADAR_PER_EFFECT).quantize(Decimal(1), ROUND_HALF_UP)
        if points != 0:
            moves[v] = points
    return moves
