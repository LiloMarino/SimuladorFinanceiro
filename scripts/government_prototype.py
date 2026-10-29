"""
Protótipo de calibração do orçamento, dos gastos e do Congresso.

Estende o protótipo da eleição (`election_prototype.py`) com as regras do orçamento do
governo, das medidas de gasto, do Congresso eleito e das emendas, sobre mandatos de 48
meses com séries sintéticas de IPCA, SELIC e Ibovespa nas faixas do histórico. Responde às
cinco perguntas da calibração:

    (a) o gastador e o austero têm eleitorado?   (b) a dívida pesa?
    (c) o Congresso muda o jogo?                 (d) a base sai cara ou barata?
    (e) o impeachment votado cai só no governo ruim?

    python -m scripts.government_prototype                # 1.000 por pergunta
    python -m scripts.government_prototype --runs 200     # rodada rápida
    python -m scripts.government_prototype --out numeros.json

O orçamento está em % do PIB por ano; as taxas, a inflação e o crescimento, em % ao ano.
"""

import argparse
import json
import warnings
from collections.abc import Callable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

import numpy as np

from scripts.election_prototype import (
    ECONOMIES,
    GROUPS,
    MEASURE_EFFECTS,
    MEASURES,
    POSITIONS,
    REFERENCE_BUDGET,
    VALUES,
    WEIGHTS,
    Campaign,
    Economy,
    Params,
    Party,
    clone,
    economy_series,
    fraction,
    make_parties,
    measure_reaction,
    random_profile,
    run_election,
    targets,
    winner_starts,
)

STABILITY, DEVELOPMENT, PUBLIC_SERVICE = 2, 3, 5
FREE_MARKET, SOCIAL_JUSTICE, SAVER_PROTECTION = 0, 1, 4


@dataclass(frozen=True)
class Tax:
    """Um imposto do jogo: a receita com a alíquota de referência e a elasticidade."""

    name: str
    # Receita com a alíquota de referência, em % do PIB por ano
    base: float
    reference: float
    default: float
    # Cortar a alíquota pela metade tira 1 - 0,5 ** (1 - elasticidade) da receita
    elasticity: float

    def revenue(self, rate: float) -> float:
        return self.base * (max(rate, 0.0) / self.reference) ** (1 - self.elasticity)


COMMON = Tax("Ganho comum de ações", 0.06, 0.15, 0.15, 0.4)
DAY_TRADE = Tax("Day trade e FII", 0.03, 0.20, 0.20, 0.3)
# A tabela de 22,5% a 15% rende, pelo prazo médio das aplicações, como uma alíquota de 17,5%
FIXED_INCOME = Tax("Renda fixa", 0.60, 0.175, 0.175, 0.15)
LCI_LCA = Tax("LCI e LCA", 0.12, 0.15, 0.0, 0.3)
TAXES = (COMMON, DAY_TRADE, FIXED_INCOME, LCI_LCA)

# Fração dos ganhos comuns que a isenção de R$ 20 mil deixa fora do IR; cresce com a raiz do teto
EXEMPT_SHARE = 0.3
EXEMPT_LIMIT = 20_000.0
# Parte do IR do ganho comum que vem de um setor
SECTOR_SHARE = 0.1


@dataclass(frozen=True)
class Policy:
    common: float = COMMON.default
    day_trade: float = DAY_TRADE.default
    exemption: float = EXEMPT_LIMIT
    fixed_income: float = FIXED_INCOME.default
    lci_lca: float = LCI_LCA.default
    exempt_sectors: float = 0.0
    # Pontos extras no IR do ganho comum, somados entre os setores taxados
    sector_extra: float = 0.0


def exempt_share(limit: float) -> float:
    return min(EXEMPT_SHARE * np.sqrt(max(limit, 0.0) / EXEMPT_LIMIT), 0.9)


def revenue(policy: Policy) -> float:
    """A receita dos impostos do jogo, em % do PIB por ano."""
    taxed = (1 - exempt_share(policy.exemption)) / (1 - exempt_share(EXEMPT_LIMIT))
    sectors = 1 - SECTOR_SHARE * policy.exempt_sectors
    common = COMMON.revenue(policy.common) * taxed * sectors
    extra = COMMON.revenue(policy.common + policy.sector_extra) - COMMON.revenue(
        policy.common
    )
    return (
        common
        + SECTOR_SHARE * extra * taxed
        + DAY_TRADE.revenue(policy.day_trade)
        + FIXED_INCOME.revenue(policy.fixed_income)
        + LCI_LCA.revenue(policy.lci_lca)
    )


TAX_STEPS: tuple[Callable[[Policy, float], Policy], ...] = (
    lambda p, s: replace(p, common=p.common - 0.05 * s),
    lambda p, s: replace(p, common=p.common + 0.05 * s),
    lambda p, s: replace(p, day_trade=p.day_trade - 0.10 * s),
    lambda p, s: replace(p, day_trade=p.day_trade + 0.10 * s),
    lambda p, s: replace(p, exemption=p.exemption + EXEMPT_LIMIT * s),
    lambda p, s: replace(p, exemption=0.0),
    lambda p, s: replace(p, fixed_income=p.fixed_income - 0.05 * s),
    lambda p, s: replace(p, fixed_income=p.fixed_income + 0.05 * s),
    lambda p, s: replace(p, lci_lca=0.15 * s),
    lambda p, s: replace(p, exempt_sectors=p.exempt_sectors + s),
    lambda p, s: replace(p, sector_extra=p.sector_extra + 0.05 * s),
)
DEFAULT_REVENUE = revenue(Policy())


def tax_effect(measure: int, steps: float) -> float:
    """A estimativa da tela: quanto a medida muda a receita contra a política padrão."""
    return revenue(TAX_STEPS[measure](Policy(), steps)) - DEFAULT_REVENUE


@dataclass(frozen=True)
class Spending:
    """Uma medida de gasto: o passo, o gasto de hoje e o que um passo faz."""

    name: str
    step: float
    unit: str
    # Gasto de hoje com o que a medida mexe, em % do PIB por ano
    base: float
    # O valor é um reajuste acima da inflação, que a conta ganha todo janeiro
    yearly: bool
    # Efeito de um passo nos valores e agrado direto de cada grupo, na escala das posições
    effect: tuple[float, ...]
    groups: tuple[float, ...]
    # Pontos de IPCA e de crescimento de um passo, quando o efeito vale cheio
    inflation: float
    growth: float

    def first_year_cost(self) -> float:
        return self.base * self.step / 100 if self.yearly else self.step


AID, SERVANTS, PENSIONS, WORKS = 0, 1, 2, 3
SPENDINGS = (
    Spending(
        "Auxílio",
        0.5,
        "ponto do PIB",
        1.5,
        False,
        (0, 1, -0.5, 0, 0, 0),
        (0, 0, 0, 0, 0, 1.5),
        0.25,
        0.0,
    ),
    Spending(
        "Reajuste dos servidores",
        3.0,
        "% acima da inflação",
        3.3,
        True,
        (0, 0, 0, 0, 0, 1),
        (0, 0, 0, 0.5, 0, 0),
        0.2,
        0.0,
    ),
    Spending(
        "Reajuste das aposentadorias",
        3.0,
        "% acima da inflação",
        8.0,
        True,
        (0, 0.5, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 0),
        0.25,
        0.0,
    ),
    Spending(
        "Obras",
        0.5,
        "ponto do PIB",
        0.7,
        False,
        (0, 0, 0, 1, 0, 0),
        (0, 0.5, 0.5, 0, 0, 0),
        0.15,
        0.6,
    ),
)


@dataclass(frozen=True)
class GovParams:
    """Os números do orçamento e do Congresso que a calibração escolhe."""

    # Gasto base do governo, em % do PIB por ano
    base_spending: float = 19.0
    # Crescimento: tendência, menos o juro real acima do neutro, mais a bolsa acima do neutro
    trend: float = 2.0
    real_rate_neutral: float = 5.0
    real_rate_weight: float = 0.4
    # Pontos de crescimento por 100% de alta do Ibovespa em 12 meses acima de 5%
    stocks_weight: float = 5.0
    stocks_neutral: float = 0.05
    # Fração do caminho até o crescimento do mês que o PIB anda por mês
    growth_step: float = 0.25
    # Lei de Okun: pontos de desemprego por ponto de crescimento acima da tendência, no ano
    okun: float = 0.5
    unemployment_neutral: float = 9.0
    # Prêmio de risco = escala x (e^(ritmo x (dívida - piso)) - 1), acima do piso
    premium_floor: float = 50.0
    premium_scale: float = 2.0
    premium_rate: float = 0.02
    # Reação da economia ao gasto (coeficientes do choque de inflação do gerador)
    selic_reaction: float = 1.5
    stocks_per_selic: float = 0.029
    # Atraso até o efeito do gasto valer cheio e meia-vida da queda, em meses
    effect_delay: int = 6
    effect_half_life: float = 12.0
    # Grupos: pontos de alvo por ponto de desemprego acima do neutro e por ponto de prêmio
    unemployment_weight: tuple[float, ...] = (0.25, 0.5, 1.0, 0.25, 0.25, 1.0)
    unemployment_cap: float = 4.0
    premium_weight: tuple[float, ...] = (2.0, 0.5, 0.5, 0.0, 1.0, 0.0)
    premium_cap: float = 6.0
    # Congresso
    seats: int = 101
    majority: int = 51
    impeachment_votes: int = 68
    barrier: float = 0.05
    # Voto da casa = afinidade + peso do histórico x (lealdade - rejeição) + peso da campanha x apoio
    history_weight: float = 1.5
    campaign_weight: float = 0.5
    # Desobediência: fração da bancada = máximo x (contrariedade ÷ cheia), até o máximo
    disobedience_max: float = 1 / 3
    disobedience_full: float = 1.0
    # Emendas: % do PIB por ano por cadeira, e a margem do centrão
    seat_price: float = 0.005
    centrao_markup: float = 1.5
    # Cadeiras a mais que o governo compra para cobrir a desobediência da base
    base_margin: int = 5
    # Quebra de acordo: rejeição nos grupos do aliado; acordo: apoio por mês ao aliado
    break_rejection: float = 8.0
    deal_support: float = 1.0


@dataclass(frozen=True)
class Passed:
    """Uma medida que passou a valer no mês do mandato, com quantos passos."""

    month: int
    spending: bool
    index: int
    steps: float


def pulls(item: Passed) -> np.ndarray:
    """Quanto a medida avança (+) ou recua (-) cada valor."""
    if item.spending:
        return item.steps * np.array(SPENDINGS[item.index].effect)
    return item.steps * MEASURE_EFFECTS[item.index]


def reaction(item: Passed) -> np.ndarray:
    """Quanto cada grupo quer a medida: posição · efeito nos valores, mais o agrado direto."""
    if item.spending:
        spending = SPENDINGS[item.index]
        return item.steps * (
            POSITIONS @ np.array(spending.effect) + np.array(spending.groups)
        )
    return measure_reaction(item.index, item.steps)


def shape(gp: GovParams, months: int) -> float:
    """O efeito do gasto: enche até o atraso, vale cheio e cai pela metade a cada meia-vida."""
    if months < 0:
        return 0.0
    if months < gp.effect_delay:
        return (months + 1) / (gp.effect_delay + 1)
    return 0.5 ** ((months - gp.effect_delay) / gp.effect_half_life)


def premium(gp: GovParams, debt: float) -> float:
    if debt <= gp.premium_floor:
        return 0.0
    return gp.premium_scale * (np.exp(gp.premium_rate * (debt - gp.premium_floor)) - 1)


@dataclass
class Course:
    """Um mandato mês a mês: a economia, as contas e a satisfação dos grupos."""

    ipca: np.ndarray
    selic: np.ndarray
    stocks: np.ndarray
    growth: np.ndarray
    unemployment: np.ndarray
    debt: np.ndarray
    premium: np.ndarray
    primary: np.ndarray
    result: np.ndarray
    satisfaction: np.ndarray
    approval: np.ndarray
    support: np.ndarray
    rejection: np.ndarray
    requests: int = 0
    impeached_at: int | None = None


# Recebe a satisfação dos grupos no mês da votação e diz se o presidente cai
Impeachment = Callable[[np.ndarray], bool]


def run_course(
    params: Params,
    gp: GovParams,
    economy: Economy,
    plan: list[Passed],
    rng: np.random.Generator,
    start: np.ndarray,
    *,
    debt0: float = 74.0,
    primary0: float = 0.0,
    unemployment0: float = 9.0,
    emendas: float = 0.0,
    impeachment: Impeachment | None = None,
    months: int = 48,
) -> Course:
    """
    O mandato começa em janeiro. Sem `impeachment`, vale a régua automática da aprovação;
    com ela, o 6º mês seguido abaixo do piso abre o pedido e a casa vota no mês seguinte.
    """
    base_ipca, base_selic, base_stocks = economy_series(economy, rng, months)
    taxes = sum(
        (tax_effect(i.index, i.steps) for i in plan if not i.spending), start=0.0
    )
    fixed = gp.base_spending - DEFAULT_REVENUE + primary0
    out = {
        k: np.full(months, np.nan)
        for k in (
            "ipca",
            "selic",
            "stocks",
            "growth",
            "unemployment",
            "debt",
            "premium",
            "primary",
            "result",
            "approval",
        )
    }
    satisfaction = start * 100
    history = np.full((months, len(GROUPS)), np.nan)
    multiplier = np.ones(len(SPENDINGS))
    level = np.ones(months)
    selic_added = np.zeros(months)
    growth, unemployment, debt = gp.trend, unemployment0, debt0
    decay = 0.5 ** (1 / params.campaign_half_life)
    support = np.zeros(len(GROUPS))
    rejection = np.zeros(len(GROUPS))
    below, requests, impeached_at, pending = 0, 0, None, False
    for m in range(months):
        active = [i for i in plan if i.month <= m]
        spend = [i for i in active if i.spending]
        added_ipca = sum(
            (
                SPENDINGS[i.index].inflation * i.steps * shape(gp, m - i.month)
                for i in spend
            ),
            start=0.0,
        )
        added_growth = sum(
            (
                SPENDINGS[i.index].growth * i.steps * shape(gp, m - i.month)
                for i in spend
            ),
            start=0.0,
        )
        ipca = base_ipca[m] + added_ipca
        selic = base_selic[m] + gp.selic_reaction * added_ipca
        selic_added[m] = gp.selic_reaction * added_ipca
        # A bolsa cai 2,9% por ponto de alta da SELIC, espalhado pelo trimestre
        level[m] = np.exp(
            -gp.stocks_per_selic * selic_added[max(m - 2, 0) : m + 1].mean()
        )
        stocks = (1 + base_stocks[m]) * level[m] / (
            level[m - 12] if m >= 12 else 1.0
        ) - 1
        real = selic - ipca
        aim = (
            gp.trend
            - gp.real_rate_weight * (real - gp.real_rate_neutral)
            + gp.stocks_weight * (stocks - gp.stocks_neutral)
            + added_growth
        )
        growth += gp.growth_step * (aim - growth)
        unemployment = float(
            np.clip(unemployment - gp.okun * (growth - gp.trend) / 12, 4.0, 18.0)
        )
        # Todo janeiro os reajustes vigentes sobem a conta
        if m > 0 and m % 12 == 0:
            for i in spend:
                if SPENDINGS[i.index].yearly:
                    multiplier[i.index] *= 1 + SPENDINGS[i.index].step * i.steps / 100
        spending = gp.base_spending + emendas
        for k, s in enumerate(SPENDINGS):
            if s.yearly:
                spending += s.base * (multiplier[k] - 1)
        spending += sum(
            (
                SPENDINGS[i.index].step * i.steps
                for i in spend
                if not SPENDINGS[i.index].yearly
            ),
            start=0.0,
        )
        primary = fixed + DEFAULT_REVENUE + taxes - spending
        risk = premium(gp, debt)
        rate = selic + risk
        debt = (
            debt
            * ((1 + rate / 100) / ((1 + growth / 100) * (1 + ipca / 100))) ** (1 / 12)
            - primary / 12
        )
        for key, value in (
            ("ipca", ipca),
            ("selic", selic),
            ("stocks", stocks),
            ("growth", growth),
            ("unemployment", unemployment),
            ("debt", debt),
            ("premium", risk),
            ("primary", primary),
            ("result", primary - debt * rate / 100),
        ):
            out[key][m] = value
        effect = np.zeros(len(GROUPS))
        for i in active:
            fade = 0.5 ** ((m - i.month) / params.measure_half_life)
            effect += params.measure_effect * reaction(i) * fade
        effect -= np.array(gp.unemployment_weight) * np.clip(
            unemployment - gp.unemployment_neutral,
            -gp.unemployment_cap,
            gp.unemployment_cap,
        )
        effect -= np.array(gp.premium_weight) * min(risk, gp.premium_cap)
        target = targets(params, ipca, selic, stocks, effect)
        satisfaction = satisfaction + (target - satisfaction) * params.approval_step
        history[m] = satisfaction
        approval = float(satisfaction @ WEIGHTS)
        out["approval"][m] = approval
        good = satisfaction > params.approved_above
        bad = satisfaction < params.reproved_below
        support = (
            support * decay
            + params.approved_support * good
            - params.reproved_support * bad
        )
        rejection = np.maximum(
            rejection + params.reproved_rejection * bad - params.approved_repair * good,
            0,
        )
        if pending:
            pending = False
            assert impeachment is not None
            if impeachment(satisfaction):
                impeached_at = m + 1
                break
            below = 0
        if m >= params.grace_months:
            below = below + 1 if approval < params.floor else 0
            if below >= params.floor_months:
                if impeachment is None:
                    impeached_at = m + 1
                    break
                requests += 1
                pending = True
    return Course(
        ipca=out["ipca"],
        selic=out["selic"],
        stocks=out["stocks"],
        growth=out["growth"],
        unemployment=out["unemployment"],
        debt=out["debt"],
        premium=out["premium"],
        primary=out["primary"],
        result=out["result"],
        satisfaction=history,
        approval=out["approval"],
        support=support,
        rejection=rejection,
        requests=requests,
        impeached_at=impeached_at,
    )


def spend(month: int, index: int, steps: float = 1.0) -> Passed:
    return Passed(month=month, spending=True, index=index, steps=steps)


# Os governos das perguntas (a) e (b): o mês em que cada medida passa a valer
STRATEGIES: dict[str, list[Passed]] = {
    "equilibrado": [],
    "austero": [spend(4, AID, -1), spend(8, WORKS, -1)],
    "gastador moderado": [spend(4, AID), spend(12, WORKS)],
    "gastador": [
        spend(4, AID),
        spend(8, WORKS),
        spend(12, PENSIONS),
        spend(16, SERVANTS),
        spend(20, AID),
        spend(24, WORKS),
    ],
    "gasta no ano da eleição": [spend(36, AID), spend(38, WORKS)],
}
MEDIUM = ECONOMIES[1]
# Os governos da pergunta (e), com um fraco entre o médio e o ruim
GOVERNMENTS = (
    *ECONOMIES[:2],
    Economy("fraco", inflation=7.0, stocks=0.0, measures=-0.5),
    ECONOMIES[2],
)


def stats(matrix: np.ndarray) -> dict[str, list[float]]:
    """Mediana e faixa de 8 em 10 mês a mês; o mês depois de todos os impeachments fica vazio."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return {
            "median": np.nanmedian(matrix, axis=0).round(2).tolist(),
            "p10": np.nanpercentile(matrix, 10, axis=0).round(2).tolist(),
            "p90": np.nanpercentile(matrix, 90, axis=0).round(2).tolist(),
        }


def strategy_question(
    params: Params, gp: GovParams, runs: int, seed: int, starts: list[np.ndarray]
) -> dict[str, object]:
    """
    (a) e (b): os mesmos mandatos (mesma série, mesma posse) com cada governo. Devolve a
    satisfação de cada grupo contra o equilibrado, o que o mandato deixou na memória e a
    eleição seguinte, e as trajetórias da dívida, do prêmio, da inflação e do crescimento.
    """
    courses: dict[str, list[Course]] = {name: [] for name in STRATEGIES}
    for k in range(runs):
        for name, plan in STRATEGIES.items():
            rng = np.random.default_rng(seed + k)
            courses[name].append(
                run_course(params, gp, MEDIUM, plan, rng, starts[k % len(starts)])
            )
    realistic = [
        run_course(
            params,
            gp,
            MEDIUM,
            plan,
            np.random.default_rng(seed + k),
            starts[k % len(starts)],
            primary0=-1.5,
        )
        for k in range(runs)
        for plan in (STRATEGIES["equilibrado"], STRATEGIES["gastador"])
    ]
    base = np.array([c.satisfaction for c in courses["equilibrado"]])
    out: dict[str, object] = {"runs": runs}
    for name, items in courses.items():
        sat = np.array([c.satisfaction for c in items])
        diff = sat - base
        out[name] = {
            "groups_diff_year1": dict(
                zip(
                    GROUPS,
                    np.nanmean(diff[:, :12], axis=(0, 1)).round(1).tolist(),
                    strict=True,
                )
            ),
            "groups_diff_final": dict(
                zip(
                    GROUPS,
                    np.nanmean(diff[:, -1], axis=0).round(1).tolist(),
                    strict=True,
                )
            ),
            "groups_diff_mean": dict(
                zip(
                    GROUPS, np.nanmean(diff, axis=(0, 1)).round(1).tolist(), strict=True
                )
            ),
            "approval": stats(np.array([c.approval for c in items])),
            "approval_diff_year1": float(np.nanmean(diff[:, :12] @ WEIGHTS)),
            "approval_diff_final": float(np.nanmean(diff[:, -1] @ WEIGHTS)),
            "support": dict(
                zip(
                    GROUPS,
                    np.mean([c.support for c in items], axis=0).round(2).tolist(),
                    strict=True,
                )
            ),
            "rejection": dict(
                zip(
                    GROUPS,
                    np.mean([c.rejection for c in items], axis=0).round(2).tolist(),
                    strict=True,
                )
            ),
            "debt": stats(np.array([c.debt for c in items])),
            "premium": stats(np.array([c.premium for c in items])),
            "ipca_added": stats(
                np.array([c.ipca for c in items])
                - np.array([c.ipca for c in courses["equilibrado"]])
            ),
            "selic_added": stats(
                np.array([c.selic for c in items])
                - np.array([c.selic for c in courses["equilibrado"]])
            ),
            "growth": stats(np.array([c.growth for c in items])),
            "unemployment": stats(np.array([c.unemployment for c in items])),
            "primary": stats(np.array([c.primary for c in items])),
            "debt_above_90": fraction(
                int(sum(np.nanmax(c.debt) > 90 for c in items)), runs
            ),
            "impeachment": fraction(
                int(sum(c.impeached_at is not None for c in items)), runs
            ),
        }
    out["next_election"] = next_election(params, courses, runs, seed)
    out["realistic"] = {
        name: {
            "debt": stats(np.array([c.debt for c in realistic[i::2]])),
            "premium": stats(np.array([c.premium for c in realistic[i::2]])),
            "debt_above_90": fraction(
                int(sum(np.nanmax(c.debt) > 90 for c in realistic[i::2])), runs
            ),
        }
        for i, name in enumerate(("equilibrado", "gastador"))
    }
    return out


def next_election(
    params: Params, courses: dict[str, list[Course]], runs: int, seed: int
) -> dict[str, dict[str, float]]:
    """A eleição seguinte: o partido que governou leva o apoio e a rejeição que o mandato deixou."""
    out = {}
    for name, items in courses.items():
        shares, wins = [], []
        for k, course in enumerate(items):
            if course.impeached_at is not None:
                continue
            world = np.random.default_rng(seed + 7 * 10**6 + k)
            parties = make_parties(
                params, world, [REFERENCE_BUDGET] * int(world.integers(3, 5))
            )
            parties[0].loyalty = parties[0].loyalty + course.support
            parties[0].rejection = parties[0].rejection + course.rejection
            election = run_election(params, parties, seed + k, seed + 10**6 + k)
            shares.append(float(election.first_round[0] / election.first_round.sum()))
            wins.append(float(election.winner == 0))
        out[name] = {
            "share": float(np.mean(shares)),
            "win": float(np.mean(wins)),
            "total": len(wins),
        }
    return out


# Os partidos do computador, sempre na casa: a UPR é o centrão
COMPUTER = (
    ("UPR", (STABILITY, DEVELOPMENT, PUBLIC_SERVICE)),
    ("MNV", (FREE_MARKET, DEVELOPMENT, SAVER_PROTECTION)),
    ("ACI", (SOCIAL_JUSTICE, STABILITY, PUBLIC_SERVICE)),
)
CENTRAO = 0


def flags(values: tuple[int, ...]) -> np.ndarray:
    profile = np.zeros(len(VALUES))
    profile[list(values)] = 1
    return profile


def dhondt(votes: np.ndarray, seats: int, barrier: float) -> np.ndarray:
    """Cadeiras pelo D'Hondt: as maiores divisões dos votos por 1, 2, 3... levam as cadeiras."""
    share = votes / votes.sum()
    eligible = np.where(share >= barrier, votes, 0.0)
    out = np.zeros(len(votes), dtype=int)
    for _ in range(seats):
        out[int(np.argmax(eligible / (out + 1)))] += 1
    return out


@dataclass
class World:
    """Uma partida sintética: os partidos, a eleição do presidente e a casa eleita."""

    parties: list[Party]
    computer: int
    president: int
    seats: np.ndarray
    # Partido (linha) x grupo (coluna): de quem é feito o eleitorado de cada bancada, somando 1
    voters: np.ndarray
    votes: np.ndarray
    start: np.ndarray
    first_round: np.ndarray = field(default_factory=lambda: np.zeros(0))


def house_scores(
    params: Params, gp: GovParams, parties: list[Party], support: np.ndarray
) -> np.ndarray:
    rows = []
    for i, p in enumerate(parties):
        raw = params.affinity_base + params.affinity_scale * POSITIONS @ p.profile
        history = p.loyalty - p.rejection
        rows.append(
            np.maximum(raw, 0)
            + gp.history_weight * history
            + gp.campaign_weight * support[i]
        )
    return np.array(rows)


def make_world(
    params: Params,
    gp: GovParams,
    seed: int,
    *,
    players: list[Party] | None = None,
) -> World:
    world = np.random.default_rng(seed)
    parties = []
    for _, values in COMPUTER:
        parties.append(
            Party(
                profile=flags(values),
                budget=float(REFERENCE_BUDGET * world.lognormal(0, 0.5)),
                timing=float(world.uniform(-0.5, 2.5)),
                rejection=world.uniform(0, 12, len(GROUPS)),
                loyalty=world.uniform(0, 4, len(GROUPS)),
                attacks=bool(world.random() < 0.5),
            )
        )
    if players is None:
        players = make_parties(
            params,
            world,
            list(REFERENCE_BUDGET * world.lognormal(0, 0.5, int(world.integers(1, 3)))),
        )
    parties += players
    split = world.uniform(0.2, 0.5, len(parties))
    president_side = clone(parties)
    house_side = clone(parties)
    for i in range(len(parties)):
        president_side[i].budget = parties[i].budget * (1 - split[i])
        house_side[i].budget = parties[i].budget * split[i]
    election = run_election(params, president_side, seed, seed + 10**6)
    campaign = Campaign(params, house_side, np.random.default_rng(seed + 2 * 10**6))
    campaign.run()
    positive = np.maximum(house_scores(params, gp, parties, campaign.support), 0)
    shares = positive / (params.undecided + positive.sum(axis=0))
    votes = shares @ WEIGHTS
    weighted = shares * WEIGHTS
    return World(
        parties=parties,
        computer=len(COMPUTER),
        president=election.winner,
        seats=dhondt(votes, gp.seats, gp.barrier),
        voters=weighted / weighted.sum(axis=1, keepdims=True),
        votes=votes / votes.sum(),
        start=election.winner_groups,
        first_round=election.first_round / election.first_round.sum(),
    )


def default_orientation(profile: np.ndarray, item: Passed) -> bool:
    """Sim quando o valor que a medida mais puxa é uma bandeira do partido."""
    pulled = pulls(item)
    if pulled.max() <= 0:
        return False
    return bool(profile[int(np.argmax(pulled))] > 0)


def disobedience(gp: GovParams, contrariety: float) -> float:
    return gp.disobedience_max * min(max(contrariety, 0.0) / gp.disobedience_full, 1.0)


def count_votes(
    gp: GovParams,
    world: World,
    orientations: list[bool],
    wants: np.ndarray,
    rng: np.random.Generator,
) -> tuple[int, int]:
    """
    `wants`: quanto os eleitores de cada bancada querem o Sim (+) ou o Não (-). Devolve os
    votos Sim e quantos deputados votaram contra a orientação.
    """
    yes, rebels = 0, 0
    for p, seats in enumerate(world.seats):
        if seats == 0:
            continue
        sign = 1 if orientations[p] else -1
        defect = int(rng.binomial(int(seats), disobedience(gp, -sign * wants[p])))
        rebels += defect
        yes += int(seats) - defect if orientations[p] else defect
    return yes, rebels


def proposals(world: World, rng: np.random.Generator, count: int = 6) -> list[Passed]:
    """O presidente propõe as medidas que mais puxam as bandeiras dele, uma a cada 6 meses."""
    profile = world.parties[world.president].profile
    options = [Passed(0, False, i, 1.0) for i in range(len(MEASURES))]
    options += [
        Passed(0, True, i, s) for i in range(len(SPENDINGS)) for s in (1.0, -1.0)
    ]
    fit = np.array([pulls(o) @ profile for o in options]) + rng.normal(
        0, 0.3, len(options)
    )
    ranked = [options[int(i)] for i in np.argsort(-fit) if fit[int(i)] > 0]
    return [replace(o, month=3 + 6 * k) for k, o in enumerate(ranked[:count])]


def allies_for(
    gp: GovParams, world: World, rng: np.random.Generator
) -> tuple[list[int], float]:
    """
    A base mais barata até 51 cadeiras mais a margem: primeiro quem aceita pelo preço cheio
    (partido do computador com duas bandeiras em comum, partido de jogador que aceita),
    depois o centrão, que cobra mais e aceita sempre. Devolve os aliados e o custo por ano.
    """
    president = world.president
    own = int(world.seats[president])
    need = gp.majority + gp.base_margin - own
    if need <= 0:
        return [], 0.0
    profile = world.parties[president].profile
    offers = []
    for p, seats in enumerate(world.seats):
        if p == president or seats == 0:
            continue
        if p == CENTRAO:
            offers.append((gp.centrao_markup, p))
        elif p < world.computer:
            if world.parties[p].profile @ profile >= 2:
                offers.append((1.0, p))
        elif rng.random() < 0.5:
            offers.append((1.0, p))
    offers.sort(key=lambda o: (o[0], -world.seats[o[1]]))
    allies, cost, got = [], 0.0, 0
    for markup, p in offers:
        if got >= need:
            break
        allies.append(p)
        got += int(world.seats[p])
        cost += int(world.seats[p]) * gp.seat_price * markup
    if got < gp.majority - own:
        return [], float("nan")
    return allies, cost


@dataclass(frozen=True)
class Session:
    """O que uma partida sintética deu na casa: as votações sem acordo e com a base comprada."""

    own_seats: int
    opposition_seats: int
    free: list[bool]
    bought: list[bool]
    # Custo da base em % do PIB por ano; NaN quando nem todos os que aceitam chegam a 51
    cost: float
    rebels: float
    vote_share: float
    seat_share: float


def congress_question(
    params: Params, gp: GovParams, runs: int, seed: int
) -> dict[str, object]:
    """
    (c) e (d): em cada partida sintética, o presidente propõe 6 medidas. A casa vota sem
    acordos e com a base comprada até 51 cadeiras mais a margem. A oposição são os partidos
    que orientam Não em mais da metade das propostas.
    """
    sessions = []
    for k in range(runs):
        world = make_world(params, gp, seed + k)
        rng = np.random.default_rng(seed + 3 * 10**6 + k)
        agenda = proposals(world, rng)
        if not agenda:
            continue
        allies, cost = allies_for(gp, world, rng)
        orientations = [
            [
                p == world.president or default_orientation(party.profile, item)
                for p, party in enumerate(world.parties)
            ]
            for item in agenda
        ]
        against = [
            p
            for p in range(len(world.parties))
            if p != world.president
            and sum(not o[p] for o in orientations) > len(agenda) / 2
        ]
        free, bought, rebels = [], [], []
        for item, orient in zip(agenda, orientations, strict=True):
            wants = world.voters @ reaction(item)
            yes, rebel = count_votes(gp, world, orient, wants, rng)
            free.append(yes >= gp.majority)
            rebels.append(rebel)
            if not np.isnan(cost):
                with_base = [o or p in allies for p, o in enumerate(orient)]
                yes, _ = count_votes(gp, world, with_base, wants, rng)
                bought.append(yes >= gp.majority)
        sessions.append(
            Session(
                own_seats=int(world.seats[world.president]),
                opposition_seats=int(sum(world.seats[p] for p in against)),
                free=free,
                bought=bought,
                cost=cost,
                rebels=float(np.mean(rebels)),
                vote_share=float(world.first_round[world.president]),
                seat_share=float(world.seats[world.president] / gp.seats),
            )
        )
    total = len(sessions)
    opposed = [s for s in sessions if s.opposition_seats >= gp.majority]
    friendly = [s for s in sessions if s.opposition_seats < gp.majority]

    def passed(group: list[Session], bought: bool) -> dict[str, float | int]:
        votes = [v for s in group for v in (s.bought if bought else s.free)]
        return fraction(int(sum(votes)), len(votes))

    costs = np.array([s.cost for s in sessions])
    possible = costs[~np.isnan(costs)]
    own = [s.own_seats for s in sessions]
    votes = [s.vote_share for s in sessions]
    seats = [s.seat_share for s in sessions]
    return {
        "worlds": total,
        "opposition_majority": fraction(len(opposed), total),
        "own_majority": fraction(sum(o >= gp.majority for o in own), total),
        "own_seats_median": float(np.median(own)),
        "own_seats_p10": float(np.percentile(own, 10)),
        "own_seats_p90": float(np.percentile(own, 90)),
        "passed_all": passed(sessions, bought=False),
        "passed_opposition_majority": passed(opposed, bought=False),
        "passed_without_opposition_majority": passed(friendly, bought=False),
        "passed_with_base": passed(sessions, bought=True),
        "passed_with_base_opposition_majority": passed(opposed, bought=True),
        "rebels_mean": float(np.mean([s.rebels for s in sessions])),
        "base_impossible": fraction(int(np.isnan(costs).sum()), total),
        "base_cost_median": float(np.median(possible)),
        "base_cost_p10": float(np.percentile(possible, 10)),
        "base_cost_p90": float(np.percentile(possible, 90)),
        "base_costs": np.sort(possible).round(3).tolist(),
        "average_measure_cost": float(
            np.mean([s.first_year_cost() for s in SPENDINGS])
        ),
        "measure_costs": {s.name: s.first_year_cost() for s in SPENDINGS},
        "president_vote_share_median": float(np.median(votes)),
        "president_seat_share_median": float(np.median(seats)),
        "vote_seat_correlation": float(np.corrcoef(votes, seats)[0, 1]),
    }


# Variantes de um partido de jogador com a verba de referência: (verba, lealdade, rejeição)
HISTORY_VARIANTS = {
    "referência": (1.0, 0.0, 0.0),
    "dobro da verba": (2.0, 0.0, 0.0),
    "histórico bom (+3)": (1.0, 3.0, 0.0),
    "histórico ruim (+5 de rejeição)": (1.0, 0.0, 5.0),
    "pouca verba e histórico bom": (0.3, 3.0, 0.0),
}


def history_question(
    params: Params, gp: GovParams, runs: int, seed: int
) -> dict[str, object]:
    """
    Quanto pesa o histórico contra a campanha: o mesmo partido de jogador (contra os três do
    computador e um rival de jogador) com mais verba, histórico bom ou histórico ruim.
    Devolve as cadeiras, os votos do 1º turno e quantas vezes elege bancada sem a presidência.
    """
    out = {}
    for name, (budget, loyalty, rejection) in HISTORY_VARIANTS.items():
        seats, votes, wins, bench = [], [], 0, 0
        for k in range(runs):
            world_rng = np.random.default_rng(seed + k)
            player = Party(
                profile=random_profile(world_rng),
                budget=budget * REFERENCE_BUDGET,
                timing=1.0,
                rejection=np.full(len(GROUPS), rejection),
                loyalty=np.full(len(GROUPS), loyalty),
            )
            rival = make_parties(params, world_rng, [REFERENCE_BUDGET])
            world = make_world(params, gp, seed + k, players=[player, *rival])
            index = len(COMPUTER)
            seats.append(int(world.seats[index]))
            votes.append(float(world.first_round[index]))
            won = world.president == index
            wins += won
            bench += (not won) and world.seats[index] >= 15
        out[name] = {
            "seats_median": float(np.median(seats)),
            "seats_mean": float(np.mean(seats)),
            "first_round_mean": float(np.mean(votes)),
            "presidency": fraction(int(wins), runs),
            "bench_without_presidency": fraction(int(bench), runs),
        }
    return out


def break_question(
    params: Params, gp: GovParams, runs: int, seed: int
) -> dict[str, object]:
    """
    O preço de romper: na eleição seguinte (verbas iguais), o partido do presidente leva a
    rejeição da quebra nos grupos do aliado, cheia no grupo em que o aliado é mais forte.
    """
    shares: dict[str, list[float]] = {"cumpriu": [], "rompeu": []}
    wins: dict[str, list[float]] = {"cumpriu": [], "rompeu": []}
    for k in range(runs):
        world = make_world(params, gp, seed + k)
        allies = [
            p
            for p in range(len(world.parties))
            if p != world.president and world.seats[p] > 0
        ]
        if not allies:
            continue
        ally = max(allies, key=lambda p: world.seats[p])
        weight = world.voters[ally] / world.voters[ally].max()
        for name in shares:
            parties = clone(world.parties)
            for party in parties:
                party.budget = REFERENCE_BUDGET
            if name == "rompeu":
                parties[world.president].rejection = (
                    parties[world.president].rejection + gp.break_rejection * weight
                )
            election = run_election(
                params, parties, seed + 5 * 10**6 + k, seed + 6 * 10**6 + k
            )
            total = election.first_round
            shares[name].append(float(total[world.president] / total.sum()))
            wins[name].append(float(election.winner == world.president))
    return {
        "runs": len(shares["cumpriu"]),
        "share_kept": float(np.mean(shares["cumpriu"])),
        "share_broken": float(np.mean(shares["rompeu"])),
        "win_kept": float(np.mean(wins["cumpriu"])),
        "win_broken": float(np.mean(wins["rompeu"])),
        # Apoio que o aliado acumula com o acordo: +1 por mês, caindo pela metade em 3 meses
        "deal_support_steady": gp.deal_support
        / (1 - 0.5 ** (1 / params.campaign_half_life)),
    }


def impeachment_vote(
    gp: GovParams, world: World, rng: np.random.Generator
) -> Impeachment:
    """A casa vota pelos eleitores: Sim quando a satisfação deles com o governo está abaixo do piso."""

    def vote(satisfaction: np.ndarray) -> bool:
        mood = world.voters @ satisfaction
        orientations = [
            p != world.president and bool(mood[p] < 25)
            for p in range(len(world.parties))
        ]
        wants = (25 - mood) / 25
        yes, _ = count_votes(gp, world, orientations, wants, rng)
        return yes >= gp.impeachment_votes

    return vote


def impeachment_question(
    params: Params, gp: GovParams, runs: int, seed: int
) -> dict[str, object]:
    """(e) Governo bom, médio e ruim com a régua automática e com o impeachment votado."""
    out: dict[str, object] = {}
    worlds = [make_world(params, gp, seed + k) for k in range(runs)]
    for economy in GOVERNMENTS:
        automatic, voted, requests, saved_by_own = 0, 0, 0, 0
        paths = []
        for k, world in enumerate(worlds):
            start = world.start
            auto = run_course(
                params, gp, economy, [], np.random.default_rng(seed + k), start
            )
            automatic += auto.impeached_at is not None
            rng = np.random.default_rng(seed + 4 * 10**6 + k)
            course = run_course(
                params,
                gp,
                economy,
                [],
                np.random.default_rng(seed + k),
                start,
                impeachment=impeachment_vote(gp, world, rng),
            )
            paths.append(course.approval)
            voted += course.impeached_at is not None
            requests += course.requests > 0
            saved_by_own += (
                course.requests > 0
                and course.impeached_at is None
                and world.seats[world.president] > gp.seats - gp.impeachment_votes
            )
        matrix = np.array(paths)
        out[economy.name] = {
            "automatic": fraction(int(automatic), runs),
            "voted": fraction(int(voted), runs),
            "requested": fraction(int(requests), runs),
            "saved_by_own_bench": fraction(int(saved_by_own), max(int(requests), 1)),
            "approval": stats(matrix),
        }
    return out


def tax_table() -> dict[str, float]:
    return {m.name: round(tax_effect(i, 1.0), 4) for i, m in enumerate(MEASURES)}


def numbers(gp: GovParams) -> dict[str, object]:
    curve = {d: round(premium(gp, d), 2) for d in (50, 60, 70, 80, 90, 100, 120, 135)}
    return {
        "gov_params": asdict(gp),
        "taxes": [asdict(t) for t in TAXES],
        "default_revenue": DEFAULT_REVENUE,
        "fixed_revenue_playable": gp.base_spending - DEFAULT_REVENUE,
        "tax_measures_per_step": tax_table(),
        "spendings": [
            {
                **asdict(s),
                "first_year_cost": s.first_year_cost(),
                "reaction": dict(
                    zip(
                        GROUPS,
                        (POSITIONS @ np.array(s.effect) + np.array(s.groups))
                        .round(2)
                        .tolist(),
                        strict=True,
                    )
                ),
            }
            for s in SPENDINGS
        ],
        "premium_curve": curve,
    }


def answer(params: Params, gp: GovParams, runs: int, seed: int) -> dict[str, object]:
    starts = winner_starts(params, min(runs, 300), seed + 5 * 10**6)
    return {
        "runs": runs,
        "strategies": strategy_question(params, gp, runs, seed, starts),
        "congress": congress_question(params, gp, runs, seed + 10**7),
        "history": history_question(params, gp, runs, seed + 2 * 10**7),
        "break": break_question(params, gp, runs, seed + 3 * 10**7),
        "impeachment": impeachment_question(params, gp, runs, seed + 4 * 10**7),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    gp = GovParams()
    result = {
        "numbers": numbers(gp),
        "answers": answer(Params(), gp, args.runs, args.seed),
    }
    if args.out:
        args.out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    report(result["answers"])


def share(data: dict[str, float | int]) -> str:
    return f"{data['share']:.0%} de {data['total']}"


def groups_line(values: dict[str, float]) -> str:
    return ", ".join(f"{g.split()[0].lower()} {v:+.1f}" for g, v in values.items())


def report(answers: dict[str, Any]) -> None:
    strategies = answers["strategies"]
    print(
        "(a) Satisfação de cada grupo contra o governo equilibrado (pontos de 0 a 100):"
    )
    for name in STRATEGIES:
        if name == "equilibrado":
            continue
        data = strategies[name]
        print(f"    {name}, 1º ano: {groups_line(data['groups_diff_year1'])}")
        print(f"    {name}, 48 meses: {groups_line(data['groups_diff_mean'])}")
    election = strategies["next_election"]
    print("    eleição seguinte (votos no 1º turno, vitória):")
    for name, data in election.items():
        print(
            f"      {name}: {data['share']:.1%}, vence {data['win']:.0%} de {data['total']}"
        )
    print("(b) Dívida ÷ PIB (mediana no 48º mês, faixa de 8 em 10) e prêmio:")
    for name in STRATEGIES:
        data = strategies[name]
        debt, risk = data["debt"], data["premium"]
        print(
            f"    {name}: {debt['median'][-1]:.0f}% ({debt['p10'][-1]:.0f} a "
            f"{debt['p90'][-1]:.0f}), prêmio {risk['median'][-1]:.1f}; passa de 90% em "
            f"{share(data['debt_above_90'])}; inflação a mais no pico "
            f"{max(data['ipca_added']['median']):.2f}"
        )
    congress = answers["congress"]
    print("(c) Congresso:")
    print(
        f"    oposição com maioria em {share(congress['opposition_majority'])} mandatos"
    )
    print(
        f"    aprovadas sem acordo: {share(congress['passed_all'])}; com a oposição em "
        f"maioria {share(congress['passed_opposition_majority'])}; sem ela "
        f"{share(congress['passed_without_opposition_majority'])}"
    )
    print(f"    com a base comprada: {share(congress['passed_with_base'])}")
    print(
        f"(d) Base de 51 + {GovParams().base_margin}: mediana "
        f"{congress['base_cost_median']:.2f}% do PIB por ano "
        f"({congress['base_cost_p10']:.2f} a {congress['base_cost_p90']:.2f}); medida "
        f"de gasto média {congress['average_measure_cost']:.2f}%; sem base possível em "
        f"{share(congress['base_impossible'])}"
    )
    history = answers["history"]
    print("    eleição da casa (cadeiras, votos no 1º turno):")
    for name, data in history.items():
        print(
            f"      {name}: {data['seats_median']:.0f} cadeiras, "
            f"{data['first_round_mean']:.1%} dos votos"
        )
    broken = answers["break"]
    print(
        f"    quebra: votos {broken['share_kept']:.1%} -> {broken['share_broken']:.1%}, "
        f"vitória {broken['win_kept']:.0%} -> {broken['win_broken']:.0%} "
        f"de {broken['runs']}"
    )
    impeachment = answers["impeachment"]
    print("(e) Impeachment (automático e votado):")
    for name, data in impeachment.items():
        print(
            f"    {name}: automático {share(data['automatic'])}, votado "
            f"{share(data['voted'])}, pedido aberto {share(data['requested'])}"
        )


if __name__ == "__main__":
    main()
