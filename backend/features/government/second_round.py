"""
O 2º turno por grupo de eleitores: a transferência dos votos de quem saiu, a declaração
de apoio, o efeito das ações, das contribuições e das doações, e a abstenção no dia da
votação. Tudo aqui é função pura sobre números; o estado da partida guarda o resultado.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from backend.core.enum import VoterGroup, VoterValue
from backend.features.government import voters

ZERO = Decimal(0)
ONE = Decimal(1)

# Com afinidade somada (descontada a rejeição) igual a este valor, metade dos votos do
# eliminado fica indecisa: 1 ÷ (1 + (somada ÷ 20)²)
TRANSFER_HALF = Decimal(20)

# A declaração leva até metade dos indecisos vindos do eliminado, vezes a confiança do
# grupo nele; a confiança é (afinidade - rejeição) ÷ 50, entre 0 e 1
FOLLOW_MAX = Decimal("0.5")
TRUST_FULL = Decimal(50)

# Até 4 promessas por chapa no 2º turno (3 na campanha), sem retirar nem trocar
MAX_PROMISES = 4

# O finalista do computador contribui com esta fração da verba mensal dele
COMPUTER_CONTRIBUTION_SHARE = Decimal("0.5")

# A pesquisa entre os turnos sai semanalmente, a partir do dia seguinte ao 1º turno
POLL_INTERVAL_DAYS = 7


@dataclass
class GroupRace:
    """A disputa dentro de um grupo: em cada 100 eleitores dele, quantos votam em cada finalista."""

    votes: dict[int, Decimal]
    undecided: Decimal
    # Dos indecisos, os que vieram do voto de cada partido eliminado
    pools: dict[int, Decimal]
    # Votos do grupo que cada ponto de apoio vale: o que valeria no 1º turno
    unit: Decimal
    # Como o 1º turno terminou no grupo, para a tabela de transferência
    voted: dict[int, Decimal] = field(default_factory=dict)
    sent: dict[int, dict[int, Decimal]] = field(default_factory=dict)

    def shift(self, party_id: int, points: Decimal) -> None:
        """
        O finalista ganha `points` de apoio no grupo: o ganho sai primeiro dos indecisos e,
        quando eles acabam, do rival. Perder apoio devolve os votos aos indecisos.
        """
        amount = abs(points) * self.unit
        if points >= 0:
            from_pool = min(amount, self.undecided)
            self._draw(from_pool)
            rival = next(f for f in self.votes if f != party_id)
            from_rival = min(amount - from_pool, self.votes[rival])
            self.votes[rival] -= from_rival
            self.votes[party_id] += from_pool + from_rival
        else:
            lost = min(amount, self.votes[party_id])
            self.votes[party_id] -= lost
            self.undecided += lost

    def _draw(self, amount: Decimal) -> None:
        """Tira votos dos indecisos, na mesma proporção de cada origem."""
        if amount <= 0 or self.undecided <= 0:
            return
        keep = ONE - amount / self.undecided
        for eliminated in self.pools:
            self.pools[eliminated] *= keep
        self.undecided -= amount

    def vote(self) -> voters.GroupVote:
        return voters.GroupVote(shares=dict(self.votes), undecided=self.undecided)


@dataclass
class Race:
    """O 2º turno em andamento: a disputa de cada grupo e quem já declarou apoio."""

    finalists: tuple[int, int]
    groups: dict[VoterGroup, GroupRace]
    # Partido eliminado -> finalista apoiado; nulo é neutralidade
    endorsements: dict[int, int | None] = field(default_factory=dict)

    def gain(
        self,
        party_id: int,
        points: Decimal,
        groups: list[VoterGroup] | None = None,
    ) -> None:
        for group in groups or list(VoterGroup):
            self.groups[group].shift(party_id, points)

    def endorse(
        self,
        eliminated: int,
        choice: int | None,
        trust: Mapping[VoterGroup, Decimal],
    ) -> None:
        """Os indecisos do eliminado seguem o apoio na medida da confiança de cada grupo."""
        self.endorsements[eliminated] = choice
        if choice is None:
            return
        for group, race in self.groups.items():
            pool = race.pools.get(eliminated, ZERO)
            moved = FOLLOW_MAX * trust[group] * pool
            race.pools[eliminated] = pool - moved
            race.undecided -= moved
            race.votes[choice] += moved

    def vote(self) -> voters.Vote:
        """O voto de hoje: o de cada grupo e o total, pelo peso do grupo."""
        return voters.combine({g: race.vote() for g, race in self.groups.items()})


def trust(affinity: Decimal, rejection: Decimal) -> Decimal:
    """Quanto o grupo confia no partido: (afinidade - rejeição) ÷ 50, entre 0 e 1."""
    return voters.clamp((affinity - rejection) / TRUST_FULL, ZERO, ONE)


def undecided_share(net_sum: Decimal) -> Decimal:
    """A fração do voto do eliminado que fica indecisa: metade com 20, 1 em 10 com 60."""
    return ONE / (ONE + (net_sum / TRANSFER_HALF) ** 2)


def start(
    standings: Mapping[int, Mapping[VoterGroup, voters.Standing]],
    nets: Mapping[int, Mapping[VoterGroup, Decimal]],
    finalists: tuple[int, int],
) -> Race:
    """
    O 2º turno a partir do 1º: em cada grupo, os votos de cada eliminado se dividem entre
    os finalistas pela afinidade do grupo com cada um (descontada a rejeição), e uma
    parte fica indecisa, maior quando o grupo gosta pouco dos dois. `nets` é a afinidade
    menos a rejeição de cada partido em cada grupo.
    """
    first = voters.vote(standings)
    groups = {}
    for group in VoterGroup:
        first_vote = first.groups[group]
        denominator = voters.UNDECIDED_BALANCE + sum(
            (max(ZERO, s[group].balance) for s in standings.values()), ZERO
        )
        race = GroupRace(
            votes={f: first_vote.shares[f] for f in finalists},
            undecided=first_vote.undecided,
            pools={},
            unit=voters.HUNDRED / denominator,
        )
        net = {f: max(ZERO, nets[f][group]) for f in finalists}
        together = sum(net.values(), ZERO)
        lost = undecided_share(together)
        for eliminated, share in first_vote.shares.items():
            if eliminated in finalists:
                continue
            split = {
                f: (net[f] / together if together > 0 else ONE / len(finalists))
                for f in finalists
            }
            pool = share * lost
            race.voted[eliminated] = share
            race.sent[eliminated] = {
                f: share * (ONE - lost) * split[f] for f in finalists
            }
            race.pools[eliminated] = pool
            race.undecided += pool
            for f in finalists:
                race.votes[f] += race.sent[eliminated][f]
        groups[group] = race
    return Race(finalists=finalists, groups=groups)


def winner(totals: Mapping[int, Decimal], first_round: Mapping[int, Decimal]) -> int:
    """O mais votado; no empate, o que foi melhor no 1º turno e, depois, o mais antigo."""
    return min(totals, key=lambda f: (-totals[f], -first_round.get(f, ZERO), f))


def totals(vote: voters.Vote, finalists: tuple[int, int]) -> dict[int, Decimal]:
    return {f: vote.total.get(f, ZERO) for f in finalists}


def radar_distance(
    a: Mapping[VoterValue, Decimal], b: Mapping[VoterValue, Decimal]
) -> Decimal:
    """A distância entre dois perfis: a média da diferença absoluta nos 6 valores."""
    return sum((abs(a[v] - b[v]) for v in VoterValue), ZERO) / len(VoterValue)


def computer_endorsement(
    radar: Mapping[VoterValue, Decimal],
    finalists: Mapping[int, Mapping[VoterValue, Decimal]],
) -> int:
    """O partido do computador eliminado declara para o finalista de valores mais próximos."""
    return min(finalists, key=lambda f: (radar_distance(radar, finalists[f]), f))


def contribution_points(total: Decimal, previous: Decimal) -> Decimal:
    """O apoio que a contribuição rende em cada grupo: a diferença da raiz do total do partido."""
    return voters.campaign_points(total) - voters.campaign_points(previous)


def poll_days(first_round: date, eve: date) -> list[date]:
    """Os dias das pesquisas entre os turnos: o seguinte ao 1º turno e a cada 7 dias, até a véspera."""
    days = []
    day = first_round + timedelta(days=1)
    while day <= eve:
        days.append(day)
        day += timedelta(days=POLL_INTERVAL_DAYS)
    return days
