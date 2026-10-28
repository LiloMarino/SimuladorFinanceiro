"""
Protótipo de calibração da eleição e do governo por grupos de eleitores.

Roda fora do app (só stdlib e numpy) as regras dos grupos de eleitores, da aprovação pelos
grupos, das ações de campanha com o d20, do 2º turno com disputa e das promessas cobradas no
mandato, sobre eleições e mandatos sintéticos. Responde às cinco perguntas da calibração:

    (a) o dinheiro ainda decide tudo?   (b) uma virada é possível?
    (c) quanto pesa o dado?             (d) aprovação de governo bom, médio e ruim
    (e) quanto rende cumprir a promessa e quanto custa trair

    python scripts/election_prototype.py                  # 1.000 por pergunta
    python scripts/election_prototype.py --runs 200       # rodada rápida
    python scripts/election_prototype.py --out numeros.json

Os pontos de apoio, afinidade e rejeição estão na escala de cada grupo (0 a 100), e a
intenção de voto é a soma dos grupos pelo peso.
"""

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np

# Grupos de eleitores e o peso de cada um no eleitorado
GROUPS = (
    "Investidores",
    "Empreendedores",
    "Trabalhadores com carteira",
    "Servidores",
    "Aposentados",
    "Quem depende de auxílio",
)
WEIGHTS = np.array([0.08, 0.12, 0.35, 0.10, 0.20, 0.15])

VALUES = (
    "Mercado livre",
    "Justiça social",
    "Estabilidade",
    "Desenvolvimento",
    "Proteção ao poupador",
    "Serviço público",
)
FREE_MARKET, SOCIAL_JUSTICE = 0, 1

# Posição de cada grupo (linha) em cada valor (coluna), de -1 (rejeita) a +1 (quer)
POSITIONS = np.array(
    [
        [1.0, -1.0, 0.5, 0.3, 0.5, -0.5],
        [0.8, -0.5, 0.3, 1.0, 0.0, -0.5],
        [-0.2, 0.5, 0.6, 0.5, 0.2, 0.0],
        [-0.6, 0.4, 0.3, 0.0, 0.2, 1.0],
        [0.0, 0.2, 1.0, -0.2, 1.0, 0.3],
        [-0.8, 1.0, 0.5, 0.2, -0.3, 0.3],
    ]
)


@dataclass(frozen=True)
class Measure:
    """Uma medida da lista: quanto um passo dela avança (+) ou recua (-) cada valor."""

    name: str
    # Tamanho do passo de referência, como a tela escreveria
    step: str
    effect: tuple[float, float, float, float, float, float]


MEASURES = (
    Measure("Cortar o IR do ganho comum de ações", "5 pontos", (1, -1, 0, 0.3, 0, 0)),
    Measure("Subir o IR do ganho comum de ações", "5 pontos", (-1, 1, 0, -0.3, 0, 0)),
    Measure("Cortar o IR do day trade", "10 pontos", (1, -0.5, 0, 0, 0, 0)),
    Measure("Subir o IR do day trade", "10 pontos", (-1, 0.5, 0, 0, 0, 0)),
    Measure(
        "Subir a isenção das vendas de ações", "R$ 20 mil", (0.5, -0.5, 0, 0, 0.5, 0)
    ),
    Measure(
        "Acabar com a isenção das vendas de ações",
        "R$ 20 mil",
        (-0.5, 0.5, 0, 0, -0.5, 0),
    ),
    Measure("Cortar o IR da renda fixa", "5 pontos", (0.5, -0.5, 0, 0, 1, 0)),
    Measure("Subir o IR da renda fixa", "5 pontos", (-0.5, 0.5, 0, 0, -1, 0)),
    Measure("Taxar LCI e LCA", "15%", (0, 0.5, 0, -0.3, -1, 0)),
    Measure("Isentar um setor", "isenção", (0.3, -0.5, 0, 1, 0, 0)),
    Measure("Taxar um setor", "5 pontos", (-0.3, 0.5, 0, -1, 0, 0)),
)
MEASURE_EFFECTS = np.array([m.effect for m in MEASURES], dtype=float)

TV, EVENT, RALLY, ATTACK = 0, 1, 2, 3
ACTIONS = ("TV", "Evento com um grupo", "Comício", "Ataque ao rival")


@dataclass(frozen=True)
class Params:
    """Os números que a calibração escolhe; o resto é regra escrita nos cards."""

    # Afinidade = base + escala vezes (posição do grupo · perfil do partido), nunca negativa
    affinity_base: float = 20.0
    affinity_scale: float = 12.0
    # Saldo fixo dos indecisos: entra na divisão do grupo como um partido a mais
    undecided: float = 15.0
    # Verba de base: pontos por mês em cada grupo = base_k vezes a raiz de R$
    base_k: float = 1 / 64
    # Fração da verba de cada partido que vai para a contribuição mensal
    base_share: float = 0.4
    # Preço (R$) e ganho normal (pontos) de cada ação
    prices: tuple[float, float, float, float] = (6000.0, 2500.0, 800.0, 2500.0)
    gains: tuple[float, float, float, float] = (0.75, 1.5, 0.5, 1.5)
    # Multiplica todos os ganhos de campanha (verba e ações)
    campaign_scale: float = 1.0
    # Reparação da rejeição pelo evento, e o limite por campanha em cada grupo
    event_repair: float = 1.0
    event_repair_cap: float = 6.0
    # Meia-vida do apoio de campanha, em meses
    campaign_half_life: float = 3.0
    # Transferência do 2º turno: com afinidade somada igual a esta, metade fica indecisa
    transfer_half: float = 20.0
    # Fração máxima dos indecisos do eliminado que segue a declaração de apoio
    follow_max: float = 0.5
    # Afinidade menos rejeição com o eliminado que dá confiança cheia
    trust_full: float = 50.0
    # Contribuição única de 2º turno e verba de ações entre os turnos, em meses de verba
    runoff_contribution: float = 0.5
    runoff_actions: float = 0.5
    # Promessa: pontos por passo e por unidade de posição do grupo
    promise_gain: float = 4.0
    # Promessa cumprida: afinidade somada e rejeição reparada, por passo e unidade de posição
    promise_loyalty: float = 3.0
    promise_repair: float = 8.0
    # Promessa descumprida: rejeição somada; na direção contrária, vezes 1,5
    promise_break: float = 8.0
    contrary_factor: float = 1.5
    # Aprovação: ponto neutro e passo até o alvo
    neutral: float = 50.0
    approval_step: float = 1 / 3
    # Força de cada fator por grupo: inflação (por ponto abaixo da meta + tolerância),
    # SELIC (por ponto acima do neutro) e Ibovespa (por 10% acima do neutro em 12 meses)
    inflation_weight: tuple[float, ...] = (2.0, 2.0, 3.5, 3.0, 4.0, 4.0)
    selic_weight: tuple[float, ...] = (0.5, -2.0, -1.5, 0.0, 1.5, -0.5)
    ibov_weight: tuple[float, ...] = (8.0, 4.0, 1.0, 0.0, 1.0, 0.0)
    inflation_tolerance: float = 1.5
    inflation_cap: float = 5.0
    selic_neutral: float = 10.0
    selic_cap: float = 6.0
    ibov_neutral: float = 0.05
    ibov_cap: float = 3.0
    # Efeito de uma medida no alvo, por passo e unidade de posição; meia-vida em meses
    measure_effect: float = 6.0
    measure_half_life: float = 6.0
    # Faixa neutra da memória do mandato
    approved_above: float = 55.0
    reproved_below: float = 45.0
    # Mês aprovado: apoio ao partido do presidente e reparação; mês reprovado: apoio e rejeição
    approved_support: float = 1.0
    approved_repair: float = 0.25
    reproved_support: float = 1.0
    reproved_rejection: float = 0.5
    # Impeachment: piso, meses seguidos abaixo dele e carência
    floor: float = 25.0
    floor_months: int = 6
    grace_months: int = 12


# Faixas do d20: (último número da faixa, multiplicador do ganho normal)
D20_BANDS = ((1, -2.0), (6, 0.5), (14, 1.0), (19, 1.5), (20, 3.0))


def die_multiplier(action: int, roll: int) -> float:
    """O multiplicador do ganho normal para o número tirado; o comício dobra os extremos."""
    multiplier = next(m for top, m in D20_BANDS if roll <= top)
    if action == RALLY and roll in (1, 20):
        return multiplier * 2
    return multiplier


def roll(action: int, dice: np.random.Generator) -> int:
    """A TV rola com vantagem: dois dados, vale o maior."""
    first = int(dice.integers(1, 21))
    if action == TV:
        return max(first, int(dice.integers(1, 21)))
    return first


@dataclass
class Party:
    profile: np.ndarray
    # Verba da campanha inteira, em R$
    budget: float
    # Mês a mês: >0 guarda a verba para o fim, <0 gasta no começo
    timing: float
    rejection: np.ndarray
    promises: list[tuple[int, float]] = field(default_factory=list)
    attacks: bool = False
    loyalty: np.ndarray = field(default_factory=lambda: np.zeros(len(GROUPS)))


def random_profile(rng: np.random.Generator) -> np.ndarray:
    """Três valores sorteados; Mercado livre e Justiça social não andam juntos."""
    while True:
        chosen = rng.choice(len(VALUES), 3, replace=False)
        if not (FREE_MARKET in chosen and SOCIAL_JUSTICE in chosen):
            profile = np.zeros(len(VALUES))
            profile[chosen] = 1
            return profile


def affinity(params: Params, party: Party) -> np.ndarray:
    raw = params.affinity_base + params.affinity_scale * POSITIONS @ party.profile
    return np.maximum(raw, 0) + party.loyalty


def measure_reaction(measure: int, steps: float) -> np.ndarray:
    """Quanto cada grupo quer a medida: posição · efeito nos valores, vezes os passos."""
    return steps * (POSITIONS @ MEASURE_EFFECTS[measure])


def promise_support(params: Params, party: Party) -> np.ndarray:
    """A promessa rende onde o grupo quer a medida, descontada pela rejeição dele."""
    total = np.zeros(len(GROUPS))
    for measure, steps in party.promises:
        reaction = params.promise_gain * measure_reaction(measure, steps)
        discount = np.where(reaction > 0, 1 - party.rejection / 100, 1)
        total += reaction * discount
    return total


def pick_promises(
    rng: np.random.Generator, profile: np.ndarray
) -> list[tuple[int, float]]:
    """Até 3 medidas dos próprios valores, de 1 ou 2 passos."""
    fit = MEASURE_EFFECTS @ profile
    ranked = [int(i) for i in np.argsort(-fit + rng.normal(0, 0.3, len(MEASURES)))]
    chosen = [i for i in ranked if fit[i] > 0][: int(rng.integers(1, 4))]
    return [(i, float(rng.integers(1, 3))) for i in chosen]


@dataclass
class Election:
    """Uma eleição sintética: os partidos e o que sai de cada etapa."""

    parties: list[Party]
    # Intenção de voto total de cada partido, mês a mês (12 pesquisas)
    polls: list[np.ndarray] = field(default_factory=list)
    first_round: np.ndarray = field(default_factory=lambda: np.zeros(0))
    finalists: tuple[int, int] | None = None
    runoff: np.ndarray = field(default_factory=lambda: np.zeros(0))
    abstention: float = 0.0
    winner: int = -1
    # Fatia do vencedor em cada grupo no turno que decidiu
    winner_groups: np.ndarray = field(default_factory=lambda: np.zeros(0))
    spent: np.ndarray = field(default_factory=lambda: np.zeros(0))


class Campaign:
    """A campanha de 12 meses até o 1º turno, com as ações escolhidas por regra."""

    def __init__(self, params: Params, parties: list[Party], dice: np.random.Generator):
        self.params = params
        self.parties = parties
        self.dice = dice
        n = len(parties)
        self.support = np.zeros((n, len(GROUPS)))
        self.repaired = np.zeros((n, len(GROUPS)))
        self.spent = np.zeros(n)
        self.decay = 0.5 ** (1 / params.campaign_half_life)

    def scores(self) -> np.ndarray:
        rows = [
            affinity(self.params, p) + promise_support(self.params, p) - p.rejection
            for p in self.parties
        ]
        return np.array(rows) + self.support

    def group_shares(self) -> np.ndarray:
        """Fatia de cada partido (linha) em cada grupo (coluna); o resto é indeciso."""
        positive = np.maximum(self.scores(), 0)
        return positive / (self.params.undecided + positive.sum(axis=0))

    def intention(self) -> np.ndarray:
        return self.group_shares() @ WEIGHTS

    def run(self, months: int = 12) -> list[np.ndarray]:
        polls = []
        monthly = [self._schedule(p, months) for p in self.parties]
        carry = np.zeros(len(self.parties))
        for month in range(months):
            self.support *= self.decay
            leader = int(np.argmax(self.intention()))
            for i, party in enumerate(self.parties):
                money = monthly[i][month]
                base = money * self.params.base_share
                self.support[i] += self._scaled(self.params.base_k * np.sqrt(base))
                self.spent[i] += base
                carry[i] = self._act(i, money - base + carry[i], leader, party)
            polls.append(self.intention())
        return polls

    def _schedule(self, party: Party, months: int) -> np.ndarray:
        shape = np.exp(party.timing * np.arange(months) / (months - 1))
        return party.budget * shape / shape.sum()

    def _scaled(self, points: float | np.ndarray) -> float | np.ndarray:
        return points * self.params.campaign_scale

    def _act(self, i: int, money: float, leader: int, party: Party) -> float:
        """Compra as ações de melhor rendimento por real até a verba do mês acabar."""
        prices = np.array(self.params.prices)
        gains = np.array(self.params.gains)
        repeats = np.zeros((len(ACTIONS), len(GROUPS)))
        rival = leader if leader != i else -1
        while money >= prices.min():
            value = gains[:, None] * 0.5**repeats * WEIGHTS[None, :] / prices[:, None]
            # A TV atinge todos os grupos: vale o ganho inteiro, uma vez só
            value[TV] = gains[TV] * 1.35 * 0.5 ** repeats[TV, 0] / prices[TV]
            value[TV, 1:] = 0
            # Atacar só vale para quem ataca e tira menos que ganhar para si
            value[ATTACK] *= 0.7 if party.attacks and rival >= 0 else 0
            value[prices > money] = 0
            if value.max() <= 0:
                break
            action, group = np.unravel_index(int(np.argmax(value)), value.shape)
            action, group = int(action), int(group)
            money -= prices[action]
            self.spent[i] += prices[action]
            factor = 0.5 ** repeats[action, group]
            repeats[action, group] += 1
            self._apply(i, action, group, rival, factor)
        return money

    def _apply(
        self, i: int, action: int, group: int, rival: int, factor: float
    ) -> None:
        params = self.params
        number = roll(action, self.dice)
        normal = float(self._scaled(params.gains[action] * factor))
        if action == ATTACK:
            if number == 1:
                self.parties[i].rejection[group] += 2 * normal
            else:
                self.support[rival, group] -= normal * die_multiplier(action, number)
            return
        gain = normal * die_multiplier(action, number)
        if action == TV:
            self.support[i] += gain
            return
        self.support[i, group] += gain
        if action == EVENT and number > 1:
            room = params.event_repair_cap - self.repaired[i, group]
            repair = min(params.event_repair * factor, max(room, 0))
            self.repaired[i, group] += repair
            rejection = self.parties[i].rejection
            rejection[group] = max(rejection[group] - repair, 0)


def second_round(
    params: Params,
    campaign: Campaign,
    finalists: tuple[int, int],
    world: np.random.Generator,
) -> tuple[np.ndarray, float, np.ndarray]:
    """
    Transferência grupo a grupo, declaração de apoio, três semanas de campanha e a
    votação, em que os indecisos que sobraram se abstêm. Devolve os votos totais dos
    finalistas, a abstenção e os votos de cada finalista por grupo.
    """
    a, b = finalists
    parties = campaign.parties
    shares = campaign.group_shares()
    votes = shares[[a, b]].copy()
    undecided = 1 - shares.sum(axis=0)
    # Cada ponto de apoio vale, em votos do grupo, o que valeria no 1º turno
    point_value = 1 / (params.undecided + np.maximum(campaign.scores(), 0).sum(axis=0))
    net = np.array(
        [
            np.maximum(affinity(params, parties[f]) - parties[f].rejection, 0)
            for f in (a, b)
        ]
    )
    following: list[tuple[float, np.ndarray]] = []
    for e, party in enumerate(parties):
        if e in finalists:
            continue
        together = net.sum(axis=0)
        lost = 1 / (1 + (together / params.transfer_half) ** 2)
        split = np.where(together > 0, net / np.maximum(together, 1e-9), 0.5)
        votes += shares[e] * (1 - lost) * split
        pool = shares[e] * lost
        undecided += pool
        trust = np.clip(
            (affinity(params, party) - party.rejection) / params.trust_full, 0, 1
        )
        closer = (
            0
            if party.profile @ parties[a].profile >= party.profile @ parties[b].profile
            else 1
        )
        neutral = world.random() < 0.2
        day = int(world.integers(0, 3))
        if not neutral:
            following.append(
                (day, params.follow_max * trust * pool * (1 if closer == 0 else -1))
            )
    monthly = np.array([parties[f].budget / 12 for f in (a, b)])
    contribution = params.base_k * np.sqrt(monthly * params.runoff_contribution)
    for week in range(3):
        for day, payload in following:
            if day != week:
                continue
            side = 0 if payload.sum() >= 0 else 1
            moved = np.minimum(np.abs(payload), undecided)
            votes[side] += moved
            undecided -= moved
        for side, f in enumerate((a, b)):
            gains = _runoff_actions(params, campaign, f, monthly[side] / 3)
            if week == 0:
                gains += contribution[side]
            _take(votes, undecided, side, gains * point_value * params.campaign_scale)
    abstention = float(undecided @ WEIGHTS)
    return votes @ WEIGHTS, abstention, votes


def _runoff_actions(
    params: Params, campaign: Campaign, f: int, money: float
) -> np.ndarray:
    """O ganho de uma semana de ações entre os turnos, rolado no dado de cada uma."""
    gains = np.zeros(len(GROUPS))
    budget = money * params.runoff_actions
    order = np.argsort(-WEIGHTS)
    repeats = np.zeros(len(GROUPS))
    k = 0
    while budget >= params.prices[EVENT]:
        group = int(order[k % len(order)])
        number = roll(EVENT, campaign.dice)
        gains[group] += (
            params.gains[EVENT] * 0.5 ** repeats[group] * die_multiplier(EVENT, number)
        )
        repeats[group] += 1
        budget -= params.prices[EVENT]
        k += 1
    return gains


def _take(
    votes: np.ndarray, undecided: np.ndarray, side: int, gains: np.ndarray
) -> None:
    """O ganho sai primeiro dos indecisos do grupo e, quando eles acabam, do rival."""
    other = 1 - side
    positive = np.maximum(gains, 0)
    from_pool = np.minimum(positive, undecided)
    from_rival = np.minimum(positive - from_pool, votes[other])
    votes[side] += from_pool + from_rival
    undecided -= from_pool
    votes[other] -= from_rival
    # O desastre devolve votos aos indecisos
    lost = np.minimum(np.maximum(-gains, 0), votes[side])
    votes[side] -= lost
    undecided += lost


def make_parties(
    params: Params,
    world: np.random.Generator,
    budgets: Sequence[float] | None = None,
) -> list[Party]:
    n = int(world.integers(3, 5)) if budgets is None else len(budgets)
    if budgets is None:
        budgets = list(REFERENCE_BUDGET * world.lognormal(0, 0.5, n))
    parties = []
    for budget in budgets:
        profile = random_profile(world)
        history = world.random() < 0.5
        rejection = (
            world.uniform(0, 20, len(GROUPS)) if history else np.zeros(len(GROUPS))
        )
        parties.append(
            Party(
                profile=profile,
                budget=float(budget),
                timing=float(world.uniform(-0.5, 2.5)),
                rejection=rejection,
                promises=pick_promises(world, profile),
                attacks=bool(world.random() < 0.5),
            )
        )
    return parties


# Verba de referência de um partido na campanha inteira: R$ 10 mil por mês
REFERENCE_BUDGET = 120_000.0


def clone(parties: list[Party]) -> list[Party]:
    return [
        replace(
            p,
            rejection=p.rejection.copy(),
            loyalty=p.loyalty.copy(),
            promises=list(p.promises),
        )
        for p in parties
    ]


def run_election(
    params: Params, parties: list[Party], world_seed: int, dice_seed: int
) -> Election:
    world = np.random.default_rng(world_seed)
    dice = np.random.default_rng(dice_seed)
    campaign = Campaign(params, parties, dice)
    election = Election(parties=parties)
    election.polls = campaign.run()
    shares = campaign.group_shares()
    intention = shares @ WEIGHTS
    election.first_round = intention
    election.spent = campaign.spent
    valid = intention / intention.sum()
    ranked = [int(i) for i in np.argsort(-intention)]
    if valid[ranked[0]] > 0.5:
        election.winner = ranked[0]
        election.winner_groups = shares[ranked[0]] / shares.sum(axis=0)
        return election
    finalists = (ranked[0], ranked[1])
    election.finalists = finalists
    totals, abstention, groups = second_round(params, campaign, finalists, world)
    election.runoff = totals
    election.abstention = abstention
    side = int(np.argmax(totals))
    election.winner = finalists[side]
    election.winner_groups = groups[side] / np.maximum(groups.sum(axis=0), 1e-9)
    return election


def fraction(hits: int, total: int) -> dict[str, float | int]:
    return {"hits": hits, "total": total, "share": hits / total if total else 0.0}


def money_question(
    params: Params, runs: int, seed: int
) -> dict[str, dict[str, float | int]]:
    """(a) Fração de vitórias de quem mais gastou, pela razão da verba sobre a do segundo."""
    out = {}
    for ratio in (1.0, 1.5, 2.0, 5.0, 10.0):
        wins = 0
        for k in range(runs):
            world = np.random.default_rng(seed + k)
            n = int(world.integers(3, 5))
            budgets = [ratio * REFERENCE_BUDGET, REFERENCE_BUDGET]
            budgets += list(REFERENCE_BUDGET * world.uniform(0.4, 1.0, n - 2))
            parties = make_parties(params, world, budgets)
            election = run_election(params, parties, seed + k, seed + 10**6 + k)
            wins += election.winner == 0
        out[f"{ratio:g}"] = fraction(wins, runs)
    return out


def comeback_question(params: Params, runs: int, seed: int) -> dict[str, object]:
    """(b) Virada: o líder 3 meses antes perde; o 1º do 1º turno perde o 2º."""
    early, runoffs, first_lost, decided = 0, 0, 0, 0
    abstention = []
    for k in range(runs):
        world = np.random.default_rng(seed + k)
        parties = make_parties(params, world)
        election = run_election(params, parties, seed + k, seed + 10**6 + k)
        early += int(np.argmax(election.polls[8])) != election.winner
        if election.finalists is None:
            decided += 1
            continue
        runoffs += 1
        first_lost += election.finalists[0] != election.winner
        abstention.append(election.abstention)
    return {
        "poll_leader_lost": fraction(early, runs),
        "first_place_lost_runoff": fraction(first_lost, runoffs),
        "decided_in_first_round": fraction(decided, runs),
        "runoff_abstention_mean": float(np.mean(abstention)) if abstention else 0.0,
    }


def dice_question(params: Params, runs: int, seed: int) -> dict[str, float | int]:
    """(c) Fração das eleições cujo vencedor muda trocando só a semente do d20."""
    changed = 0
    for k in range(runs):
        world = np.random.default_rng(seed + k)
        parties = make_parties(params, world)
        first = run_election(params, clone(parties), seed + k, seed + 10**6 + k)
        second = run_election(params, clone(parties), seed + k, seed + 2 * 10**6 + k)
        changed += first.winner != second.winner
    return fraction(changed, runs)


@dataclass(frozen=True)
class Economy:
    """Um governo sintético: média da inflação, deriva da bolsa e medidas aprovadas."""

    name: str
    inflation: float
    stocks: float
    # Quanto as medidas aprovadas agradam o eleitorado (+) ou desagradam (-)
    measures: float


ECONOMIES = (
    Economy("bom", inflation=3.5, stocks=0.18, measures=1.0),
    Economy("médio", inflation=4.5, stocks=0.08, measures=0.0),
    Economy("ruim", inflation=10.0, stocks=-0.12, measures=-1.0),
)
INFLATION_TARGET = 3.0


def economy_series(
    economy: Economy, rng: np.random.Generator, months: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """IPCA e SELIC em % ao ano e alta do Ibovespa em 12 meses, nas faixas do histórico."""
    inflation = np.empty(months)
    level = economy.inflation + rng.normal(0, 1)
    for m in range(months):
        level += 0.1 * (economy.inflation - level) + rng.normal(0, 0.4)
        inflation[m] = level
    inflation = np.clip(inflation, 1.5, 17.0)
    selic = (
        3
        + inflation
        + 1.2 * (inflation - INFLATION_TARGET)
        + rng.normal(0, 0.5, months)
    )
    selic = np.clip(selic, 2.0, 26.5)
    monthly = rng.normal(np.log1p(economy.stocks) / 12, 0.25 / np.sqrt(12), months + 12)
    stocks = np.exp(np.convolve(monthly, np.ones(12), "valid")[1:]) - 1
    return inflation, selic, stocks


def mandate_measures(
    economy: Economy, rng: np.random.Generator
) -> list[tuple[int, int, float]]:
    """(mês em que vale, medida, passos): o governo bom aprova o que agrada, o ruim o que irrita."""
    out = []
    for _ in range(int(rng.integers(2, 5))):
        appeal = (POSITIONS @ MEASURE_EFFECTS.T).T @ WEIGHTS
        noise = rng.normal(0, 0.3, len(MEASURES))
        index = int(np.argmax(economy.measures * appeal + noise))
        out.append((int(rng.integers(3, 44)), index, float(rng.integers(1, 3))))
    return out


def targets(
    params: Params, inflation: float, selic: float, stocks: float, measures: np.ndarray
) -> np.ndarray:
    gap = np.clip(
        INFLATION_TARGET + params.inflation_tolerance - inflation,
        -params.inflation_cap,
        params.inflation_cap,
    )
    rate = np.clip(selic - params.selic_neutral, -params.selic_cap, params.selic_cap)
    bolsa = np.clip(
        (stocks - params.ibov_neutral) / 0.10, -params.ibov_cap, params.ibov_cap
    )
    target = (
        params.neutral
        + np.array(params.inflation_weight) * gap
        + np.array(params.selic_weight) * rate
        + np.array(params.ibov_weight) * bolsa
        + measures
    )
    return np.clip(target, 0, 100)


@dataclass
class Mandate:
    approval: np.ndarray
    impeached_at: int | None
    approved_months: np.ndarray
    reproved_months: np.ndarray
    # O que o mandato deixou para o partido do presidente em cada grupo
    support: np.ndarray
    rejection: np.ndarray


def run_mandate(
    params: Params,
    economy: Economy,
    start: np.ndarray,
    rng: np.random.Generator,
    months: int = 48,
) -> Mandate:
    inflation, selic, stocks = economy_series(economy, rng, months)
    passed = mandate_measures(economy, rng)
    satisfaction = start * 100
    decay = 0.5 ** (1 / params.campaign_half_life)
    approval = np.empty(months)
    approved = np.zeros(len(GROUPS))
    reproved = np.zeros(len(GROUPS))
    support = np.zeros(len(GROUPS))
    rejection = np.zeros(len(GROUPS))
    below = 0
    impeached_at = None
    for m in range(months):
        effect = np.zeros(len(GROUPS))
        for valid_from, measure, steps in passed:
            if valid_from <= m:
                fade = 0.5 ** ((m - valid_from) / params.measure_half_life)
                effect += (
                    params.measure_effect * measure_reaction(measure, steps) * fade
                )
        target = targets(params, inflation[m], selic[m], stocks[m], effect)
        satisfaction += (target - satisfaction) * params.approval_step
        approval[m] = satisfaction @ WEIGHTS
        good = satisfaction > params.approved_above
        bad = satisfaction < params.reproved_below
        approved += good
        reproved += bad
        support = (
            support * decay
            + params.approved_support * good
            - params.reproved_support * bad
        )
        rejection = np.maximum(
            rejection + params.reproved_rejection * bad - params.approved_repair * good,
            0,
        )
        if m >= params.grace_months:
            below = below + 1 if approval[m] < params.floor else 0
            if below >= params.floor_months:
                impeached_at = m + 1
                approval[m + 1 :] = np.nan
                break
    return Mandate(approval, impeached_at, approved, reproved, support, rejection)


def approval_question(
    params: Params, runs: int, seed: int, starts: list[np.ndarray]
) -> dict[str, object]:
    """(d) Trajetória da aprovação de governos bom, médio e ruim, e a taxa de impeachment."""
    out: dict[str, object] = {}
    for economy in ECONOMIES:
        paths = []
        impeached = 0
        months_to_impeach = []
        for k in range(runs):
            rng = np.random.default_rng(seed + k)
            start = starts[k % len(starts)]
            mandate = run_mandate(params, economy, start, rng)
            paths.append(mandate.approval)
            if mandate.impeached_at is not None:
                impeached += 1
                months_to_impeach.append(mandate.impeached_at)
        matrix = np.array(paths)
        finished = matrix[~np.isnan(matrix[:, -1]), -1]
        out[economy.name] = {
            "median": np.nanmedian(matrix, axis=0).round(1).tolist(),
            "p10": np.nanpercentile(matrix, 10, axis=0).round(1).tolist(),
            "p90": np.nanpercentile(matrix, 90, axis=0).round(1).tolist(),
            "final_median": float(np.median(finished)) if finished.size else None,
            "final_p10": float(np.percentile(finished, 10)) if finished.size else None,
            "final_p90": float(np.percentile(finished, 90)) if finished.size else None,
            "impeachment": fraction(impeached, runs),
            "impeachment_month_median": float(np.median(months_to_impeach))
            if months_to_impeach
            else None,
        }
    return out


def promise_question(params: Params, runs: int, seed: int) -> dict[str, object]:
    """
    (e) Na eleição seguinte, o partido que governou e prometeu 2 medidas de 1 passo:
    cumpriu, cumpriu metade, não fez nada ou fez o contrário. A metade do balanço já pesa
    no voto (chapas fechadas); a outra metade fica para a eleição depois dessa.
    """
    outcomes = {
        "sem promessa": None,
        "cumpriu": 1.0,
        "metade": 0.5,
        "nada": 0.0,
        "contrário": -0.5,
    }
    results: dict[str, dict[str, list[float]]] = {
        name: {"share": [], "win": [], "share_full": [], "win_full": []}
        for name in outcomes
    }
    campaign_yield = []
    for k in range(runs):
        world = np.random.default_rng(seed + k)
        base = make_parties(
            params, world, [REFERENCE_BUDGET] * int(world.integers(3, 5))
        )
        incumbent = base[0]
        fits = MEASURE_EFFECTS @ incumbent.profile
        best = [int(i) for i in np.argsort(-fits)[:2]]
        incumbent.promises = [(i, 1.0) for i in best]
        with_promise = promise_support(params, incumbent) @ WEIGHTS
        campaign_yield.append(float(with_promise))
        for name, done in outcomes.items():
            for weight, key in ((0.5, ""), (1.0, "_full")):
                parties = clone(base)
                if done is None:
                    parties[0].promises = []
                else:
                    settle(params, parties[0], done, weight)
                election = run_election(params, parties, seed + k, seed + 10**6 + k)
                total = election.first_round
                results[name]["share" + key].append(float(total[0] / total.sum()))
                results[name]["win" + key].append(float(election.winner == 0))
    summary = {
        name: {key: float(np.mean(values)) for key, values in data.items()}
        for name, data in results.items()
    }
    return {
        "runs": runs,
        "campaign_yield_points": float(np.mean(campaign_yield)),
        "by_outcome": summary,
    }


def settle(params: Params, party: Party, done: float, weight: float) -> None:
    """O balanço das promessas no fim do mandato, nos grupos que queriam cada medida."""
    for measure, steps in party.promises:
        wanted = np.maximum(measure_reaction(measure, steps), 0)
        if done > 0:
            party.loyalty += weight * params.promise_loyalty * done * wanted
            party.rejection = np.maximum(
                party.rejection - weight * params.promise_repair * done * wanted, 0
            )
        # Na direção contrária a rejeição sai maior que a cheia
        missing = 1 - done if done >= 0 else params.contrary_factor
        party.rejection = (
            party.rejection + weight * params.promise_break * missing * wanted
        )


def winner_starts(params: Params, runs: int, seed: int) -> list[np.ndarray]:
    """A satisfação de posse: a fatia do presidente em cada grupo no turno que decidiu."""
    starts = []
    for k in range(runs):
        world = np.random.default_rng(seed + k)
        election = run_election(
            params, make_parties(params, world), seed + k, seed + 10**6 + k
        )
        starts.append(election.winner_groups)
    return starts


def answer(params: Params, runs: int, seed: int) -> dict[str, object]:
    starts = winner_starts(params, min(runs, 300), seed + 5 * 10**6)
    return {
        "runs": runs,
        "money": money_question(params, runs, seed),
        "comeback": comeback_question(params, runs, seed + 10**7),
        "dice": dice_question(params, runs, seed + 2 * 10**7),
        "approval": approval_question(params, runs, seed + 3 * 10**7, starts),
        "promise": promise_question(params, runs, seed + 4 * 10**7),
        "inauguration_mean": float(np.mean([s @ WEIGHTS for s in starts])),
    }


def numbers(params: Params) -> dict[str, object]:
    """Os números calibrados, prontos para os cards."""
    return {
        "params": asdict(params),
        "groups": dict(zip(GROUPS, WEIGHTS.tolist(), strict=True)),
        "positions": {
            g: dict(zip(VALUES, row.tolist(), strict=True))
            for g, row in zip(GROUPS, POSITIONS, strict=True)
        },
        "measures": {
            m.name: {"step": m.step, **dict(zip(VALUES, m.effect, strict=True))}
            for m in MEASURES
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    params = Params()
    result = {
        "numbers": numbers(params),
        "answers": answer(params, args.runs, args.seed),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    report(result["answers"])


def report(answers: dict[str, object]) -> None:
    money = answers["money"]
    assert isinstance(money, dict)
    print("(a) Vitórias de quem mais gastou, pela razão da verba sobre a do 2º:")
    for ratio, data in money.items():
        print(f"    {ratio}x: {data['share']:.0%} de {data['total']}")
    comeback = answers["comeback"]
    assert isinstance(comeback, dict)
    print("(b) Virada:")
    for key in (
        "poll_leader_lost",
        "first_place_lost_runoff",
        "decided_in_first_round",
    ):
        data = comeback[key]
        print(f"    {key}: {data['share']:.0%} de {data['total']}")
    print(f"    abstenção média no 2º turno: {comeback['runoff_abstention_mean']:.1%}")
    dice = answers["dice"]
    assert isinstance(dice, dict)
    print(f"(c) Dado muda o vencedor: {dice['share']:.0%} de {dice['total']}")
    approval = answers["approval"]
    assert isinstance(approval, dict)
    print(f"(d) Aprovação (posse média {answers['inauguration_mean']:.0%}):")
    for name, data in approval.items():
        imp = data["impeachment"]
        print(
            f"    {name}: fim {data['final_median']}, p10 {data['final_p10']}, "
            f"p90 {data['final_p90']}; impeachment {imp['share']:.0%} de {imp['total']}"
        )
    promise = answers["promise"]
    assert isinstance(promise, dict)
    print(
        f"(e) Promessa: rende {promise['campaign_yield_points']:.1f} pontos na campanha"
    )
    for name, data in promise["by_outcome"].items():
        print(
            f"    {name}: votos {data['share']:.1%} (vitória {data['win']:.0%}); "
            f"com o balanço inteiro {data['share_full']:.1%} (vitória {data['win_full']:.0%})"
        )


if __name__ == "__main__":
    main()
