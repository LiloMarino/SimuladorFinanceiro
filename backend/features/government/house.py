"""
A casa do Congresso: 101 cadeiras eleitas junto com o presidente, a bancada de cada
partido, a orientação que o líder dá em cada votação e os deputados que desobedecem. É o
contrato em que a negociação de apoio e as medidas de gasto se apoiam. Tudo aqui é
função pura sobre números; o estado da partida guarda o resultado.
"""

import math
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal

from backend.core.enum import VoterGroup, VoterValue
from backend.features.government import voters
from backend.features.government.computer_parties import COMPUTER_PARTIES

ZERO = Decimal(0)
HUNDRED = Decimal(100)

SEATS = 101
# A medida passa com 51 votos Sim; o impeachment cai com 68, dois terços da casa
MAJORITY = 51
IMPEACHMENT_VOTES = 68
# Quem fica abaixo de 5% dos votos válidos não elege ninguém
BARRIER = Decimal("0.05")

# Força de um partido num grupo = afinidade + 1,5 x (lealdade - rejeição) + 0,5 x apoio
# da campanha de Congresso: o histórico pesa mais do que o dinheiro do mês
HISTORY_WEIGHT = Decimal("1.5")
CAMPAIGN_WEIGHT = Decimal("0.5")

# Quanto da bancada desobedece: um terço dela, quando a medida contraria por inteiro
# quem elegeu o partido (contrariedade 1)
DISOBEDIENCE_MAX = Decimal(1) / 3
DISOBEDIENCE_FULL = Decimal(1)

# A fração da verba de base do computador (o que sobra das ações do mês) que vai para a campanha do Congresso
COMPUTER_HOUSE_SHARE = Decimal("0.3")

# No impeachment, os eleitores mandam: abaixo desta satisfação a bancada vota Sim
IMPEACHMENT_SATISFACTION = Decimal(25)

# Os três partidos do computador têm lugar fixo na casa, com chave negativa; o partido
# de jogador usa o próprio id
COMPUTER_KEYS: dict[str, int] = {
    party.abbr: -(index + 1) for index, party in enumerate(COMPUTER_PARTIES)
}


@dataclass(frozen=True)
class Bloc:
    """A bancada de um partido na casa eleita."""

    key: int
    # O partido na partida; nulo no partido do computador que não concorreu naquele ano
    party_id: int | None
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    # Em cada 100 votos válidos
    votes: Decimal
    seats: int
    # De quem é feito o eleitorado da bancada, por grupo, somando 1
    mix: dict[VoterGroup, Decimal]


@dataclass(frozen=True)
class House:
    """A casa eleita: a bancada de cada partido que entrou na disputa."""

    blocs: tuple[Bloc, ...]
    # Quem ficou abaixo da barreira
    below: tuple[int, ...] = ()
    # O quociente da última cadeira dada e o da primeira que ficou de fora
    last: Decimal = ZERO
    upcoming: Decimal = ZERO

    def bloc(self, key: int) -> Bloc | None:
        return next((b for b in self.blocs if b.key == key), None)

    def of_party(self, party_id: int) -> Bloc | None:
        return next((b for b in self.blocs if b.party_id == party_id), None)

    @property
    def seated(self) -> tuple[Bloc, ...]:
        return tuple(b for b in self.blocs if b.seats > 0)


@dataclass(frozen=True)
class Distribution:
    seats: dict[int, int]
    below: tuple[int, ...]
    last: Decimal
    upcoming: Decimal


@dataclass(frozen=True)
class Candidate:
    """Um partido na disputa da casa."""

    key: int
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    party_id: int | None


@dataclass(frozen=True)
class BlocVote:
    """Como uma bancada votou: a orientação, o Sim e o Não e quantos foram contra ela."""

    seats: int
    orientation: bool
    yes: int
    no: int
    defected: int
    # O grupo do eleitorado da bancada que mais queria o voto contrário ao orientado
    cause: VoterGroup | None = None


@dataclass(frozen=True)
class Tally:
    yes: int
    no: int
    blocs: dict[int, BlocVote]

    @property
    def defected(self) -> int:
        return sum(b.defected for b in self.blocs.values())


def strength(
    group: VoterGroup,
    radar: Mapping[VoterValue, Decimal],
    loyalty: Decimal,
    rejection: Decimal,
    campaign: Decimal,
) -> Decimal:
    """Quanto o partido pesa no voto do grupo para a casa."""
    value = (
        voters.affinity(group, radar)
        + HISTORY_WEIGHT * (loyalty - rejection)
        + CAMPAIGN_WEIGHT * campaign
    )
    return max(ZERO, value)


def vote(
    strengths: Mapping[int, Mapping[VoterGroup, Decimal]],
) -> voters.Vote:
    """O voto de cada grupo na casa: a força de cada partido contra os indecisos."""
    groups = {
        g: voters.group_vote({key: s[g] for key, s in strengths.items()})
        for g in VoterGroup
    }
    return voters.combine(groups)


def distribute(
    votes: Mapping[int, Decimal],
    seats: int = SEATS,
    barrier: Decimal = BARRIER,
) -> Distribution:
    """
    As cadeiras pelo método D'Hondt: os votos de cada partido são divididos por 1, 2, 3 e
    assim por diante, e as maiores divisões levam as cadeiras. Quem fica abaixo da
    barreira não entra na divisão.
    """
    total = sum(votes.values(), ZERO)
    share = {k: (v / total if total > 0 else ZERO) for k, v in votes.items()}
    below = tuple(sorted(k for k, s in share.items() if s < barrier))
    eligible = {k: v for k, v in votes.items() if k not in below}
    won = dict.fromkeys(votes, 0)
    last = ZERO
    for _ in range(seats if eligible else 0):
        key = max(eligible, key=lambda k: (eligible[k] / (won[k] + 1), eligible[k], -k))
        last = eligible[key] / (won[key] + 1)
        won[key] += 1
    upcoming = max(
        (eligible[k] / (won[k] + 1) for k in eligible),
        default=ZERO,
    )
    return Distribution(won, below, last, upcoming)


def electorate_mix(
    key: int, groups: Mapping[VoterGroup, voters.GroupVote]
) -> dict[VoterGroup, Decimal]:
    """De quem é feito o eleitorado do partido: o peso de cada grupo nos votos dele, somando 1."""
    weighted = {
        g: voters.WEIGHTS[g] * gv.shares.get(key, ZERO) for g, gv in groups.items()
    }
    total = sum(weighted.values(), ZERO)
    if total <= 0:
        return {g: voters.WEIGHTS[g] for g in VoterGroup}
    return {g: w / total for g, w in weighted.items()}


def elect(
    candidates: Iterable[Candidate],
    strengths: Mapping[int, Mapping[VoterGroup, Decimal]],
) -> House:
    """A casa de uma eleição: os votos de cada partido viram cadeiras pelo D'Hondt com barreira."""
    result = vote(strengths)
    cut = distribute(result.total)
    total = sum(result.total.values(), ZERO)
    blocs = tuple(
        Bloc(
            key=c.key,
            party_id=c.party_id,
            abbr=c.abbr,
            name=c.name,
            color=c.color,
            is_computer=c.is_computer,
            votes=result.total.get(c.key, ZERO) * HUNDRED / total
            if total > 0
            else ZERO,
            seats=cut.seats.get(c.key, 0),
            mix=electorate_mix(c.key, result.groups),
        )
        for c in candidates
    )
    return House(blocs, cut.below, cut.last, cut.upcoming)


def initial_house() -> House:
    """A casa antes da 1ª eleição: as 101 cadeiras dos três partidos do computador pelo eleitorado inicial."""
    candidates = [
        Candidate(COMPUTER_KEYS[p.abbr], p.abbr, p.name, None, True, None)
        for p in COMPUTER_PARTIES
    ]
    strengths = {
        COMPUTER_KEYS[p.abbr]: {
            g: strength(g, voters.initial_radar(p.flags), ZERO, ZERO, ZERO)
            for g in VoterGroup
        }
        for p in COMPUTER_PARTIES
    }
    return elect(candidates, strengths)


# Orientação


def flag_rules(flags: Iterable[VoterValue] | None) -> dict[VoterValue, bool]:
    """A orientação padrão que nasce com o partido: Sim nos valores que ele defende, Não nos outros."""
    chosen = set(flags or ())
    return {v: v in chosen for v in VoterValue}


def pulled_value(effects: Mapping[VoterValue, Decimal]) -> VoterValue | None:
    """O valor que a medida mais avança; nenhum quando ela só recua valores."""
    best = max(
        effects.items(),
        key=lambda item: (item[1], -list(VoterValue).index(item[0])),
        default=None,
    )
    return best[0] if best is not None and best[1] > 0 else None


def default_orientation(
    rules: Mapping[VoterValue, bool], effects: Mapping[VoterValue, Decimal]
) -> bool:
    """A bancada sem orientação do líder segue a regra do valor que a medida mais puxa."""
    value = pulled_value(effects)
    return False if value is None else rules[value]


def reactions(effects: Mapping[VoterValue, Decimal]) -> dict[VoterGroup, Decimal]:
    """Quanto cada grupo quer a medida (+) ou a rejeita (-)."""
    return {g: voters.reaction(g, effects) for g in VoterGroup}


def wants(
    mix: Mapping[VoterGroup, Decimal], by_group: Mapping[VoterGroup, Decimal]
) -> Decimal:
    """Quanto os eleitores da bancada querem o Sim (+) ou o Não (-): a reação de cada grupo pesada pela composição dela."""
    return sum((mix[g] * by_group[g] for g in mix), ZERO)


def contrariety(orientation: bool, want: Decimal) -> Decimal:
    """Quanto os eleitores querem o voto contrário ao orientado, de 0 para cima."""
    return max(ZERO, -want if orientation else want)


def defection(contrary: Decimal) -> Decimal:
    """A fração da bancada que vota contra a orientação: cheia (um terço) em contrariedade 1."""
    return DISOBEDIENCE_MAX * min(contrary / DISOBEDIENCE_FULL, Decimal(1))


def contrary_group(
    mix: Mapping[VoterGroup, Decimal],
    by_group: Mapping[VoterGroup, Decimal],
    orientation: bool,
) -> VoterGroup | None:
    """O grupo do eleitorado da bancada que mais quer o voto contrário ao orientado."""
    pushes = {g: mix[g] * (-by_group[g] if orientation else by_group[g]) for g in mix}
    best = max(pushes, key=lambda g: (pushes[g], g.value), default=None)
    return best if best is not None and pushes[best] > 0 else None


def count(
    key: str,
    seed: int,
    house: House,
    orientations: Mapping[int, bool],
    wanted: Mapping[int, Decimal],
) -> Tally:
    """
    A votação: cada deputado vota na orientação da bancada, e uma fração dele, que cresce
    com a contrariedade, vota contra. O sorteio nasce da semente da partida e da votação,
    deputado a deputado: a retomada sorteia igual.
    """
    rng = random.Random(f"{seed}:house:{key}")
    yes = no = 0
    blocs = {}
    for bloc in sorted(house.seated, key=lambda b: b.key):
        orientation = orientations.get(bloc.key, False)
        rate = float(defection(contrariety(orientation, wanted.get(bloc.key, ZERO))))
        defected = sum(1 for _ in range(bloc.seats) if rng.random() < rate)
        bloc_yes = bloc.seats - defected if orientation else defected
        yes += bloc_yes
        no += bloc.seats - bloc_yes
        blocs[bloc.key] = BlocVote(
            bloc.seats, orientation, bloc_yes, bloc.seats - bloc_yes, defected
        )
    return Tally(yes, no, blocs)


def may_defect(seats: int, orientation: bool, want: Decimal) -> int:
    """Até quantos deputados da bancada podem votar contra a orientação."""
    return min(seats, math.ceil(seats * defection(contrariety(orientation, want))))


def forecast(
    house: House,
    orientations: Mapping[int, bool],
    wanted: Mapping[int, Decimal],
) -> tuple[int, int]:
    """O placar previsto em faixa: do Sim com todos que podem desobedecer votando contra até o Sim sem nenhum."""
    low = high = 0
    for bloc in house.seated:
        orientation = orientations.get(bloc.key, False)
        risk = may_defect(bloc.seats, orientation, wanted.get(bloc.key, ZERO))
        if orientation:
            low += bloc.seats - risk
            high += bloc.seats
        else:
            high += risk
    return low, high


# Impeachment


def mood(
    mix: Mapping[VoterGroup, Decimal], satisfaction: Mapping[VoterGroup, Decimal]
) -> Decimal:
    """A satisfação com o governo dos eleitores da bancada, pesada pela composição dela."""
    return sum((mix[g] * satisfaction[g] for g in mix), ZERO)


def impeachment_orientation(mood_: Decimal) -> bool:
    """Sim quando a satisfação dos eleitores da bancada está abaixo do piso."""
    return mood_ < IMPEACHMENT_SATISFACTION


def impeachment_reactions(
    satisfaction: Mapping[VoterGroup, Decimal],
) -> dict[VoterGroup, Decimal]:
    """Quanto cada grupo quer a saída: 1 com satisfação zero, 0 no piso e negativo acima dele."""
    return {
        g: (IMPEACHMENT_SATISFACTION - satisfaction[g]) / IMPEACHMENT_SATISFACTION
        for g in VoterGroup
    }
