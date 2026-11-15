"""
Protótipo de calibração das estatais.

Roda as contas puras do próprio backend (alavancas e teto de IPCA, payout, valor justo,
preço, empurrão no PIB, o livro das estatais, o passo da dívida e as ligações da
economia) sobre uma economia sintética nas faixas do histórico, sem banco e sem subir
partida. Mede os sete critérios de aceite, cada um com PASSA ou FALHA e o número, e
mostra a sensibilidade das constantes provisórias:

    (1) fundar 10 estatais em 10 anos contra não fundar
    (2) segurar e soltar o preço devolve a inflação represada inteira
    (3) o Banco estatal só baixa o juro do crédito, nunca o IPCA
    (4) nenhuma combinação de degraus permitidos passa do teto de IPCA
    (5) espremer e reinvestir contra o dividendo normal
    (6) fundar e privatizar ao valor justo nunca reduz a dívida
    (7) a estatal importada sem ordem segue o histórico

    uv run python -m scripts.state_company_prototype                # 200 sementes
    uv run python -m scripts.state_company_prototype --runs 50      # rodada rápida
    uv run python -m scripts.state_company_prototype --out relatorio.md

As constantes do backend são lidas como estão; a sensibilidade as troca só durante a
conta (`overridden`) e o backend nunca é alterado.
"""

import argparse
import io
import itertools
import math
import random
import statistics
import sys
from collections.abc import Generator, Sequence
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from functools import cache
from pathlib import Path
from types import ModuleType

from backend.core.dto.state_company import StateCompanyDTO
from backend.core.enum import (
    DividendPolicy,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
)
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.utils import last_day_of_month
from backend.features.economy.links import LinkMonth, link_month
from backend.features.government import budget
from backend.features.state_companies import (
    fair_value,
    gdp,
    levers,
    payout,
    price,
)
from backend.features.state_companies.book import (
    FOUNDING_GOVERNMENT_SHARE,
    FOUNDING_PRICE,
    StateCompanyBook,
    government_shares,
    invested_by,
)
from backend.features.state_companies.orders import StateOrder

ZERO = Decimal(0)
BILLION = Decimal(10) ** 9
CENT = Decimal("0.01")
START_YEAR = 2026

# O Banco Central reage com 1,5 ponto de SELIC por ponto de IPCA a mais (a regra da camada da economia)
SELIC_REACTION = 1.5

PROVISIONAL = (
    "LEVER_WEIGHT (FUEL 0,05; ENERGY 0,04; BANK 0)",
    "CREDIT_WEIGHT (BANK 0,05)",
    "IPCA_CAP_POINTS (1,5)",
    "POLICY_REFERENCE_GROWTH (0,04)",
    "SIZE_STEP (0,01), limites do porte (0,5 a 1,5), FOUNDING_MONTHS (12)",
)


# Premissas da economia sintética


@dataclass(frozen=True)
class Setting:
    """A economia em que as estatais entram: PIB, dívida, crescimento, inflação e SELIC de partida."""

    gdp: Decimal = Decimal(11) * 10**12
    debt: Decimal = Decimal("0.75")
    growth: Decimal = Decimal("0.02")
    ipca: Decimal = Decimal("0.045")
    selic: Decimal = Decimal("0.105")
    # O primário da linha de base, em fração do PIB: o superávit que mantém a dívida perto de estável
    primary: Decimal = Decimal("0.03")

    @property
    def real_interest(self) -> Decimal:
        """O juro real do dia da fundação: SELIC descontada a inflação."""
        return (1 + self.selic) / (1 + self.ipca) - 1


SETTING = Setting()


def fast_period_rate(rate: Decimal, periods: Decimal | int) -> Decimal:
    """
    A taxa de um período que, composta por `periods` períodos, rende `rate`: a mesma conta
    de `backend.core.rates.period_rate` em ponto flutuante (erro de 1e-16 por mês), que
    custa uma fração do `Decimal` e deixa milhares de partidas caberem no relatório.
    """
    return Decimal((1 + float(rate)) ** (1 / float(periods)) - 1)


@contextmanager
def overridden(module: ModuleType, **values: object) -> Generator[None]:
    """Troca constantes do módulo só dentro do bloco; o valor do backend volta ao sair."""
    saved = {name: getattr(module, name) for name in values}
    for name, value in values.items():
        setattr(module, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(module, name, value)


# Datas e formatação


def month_start(index: int) -> date:
    return date(START_YEAR + index // 12, index % 12 + 1, 1)


def month_end(index: int) -> date:
    return last_day_of_month(month_start(index))


def br(value: float | Decimal, digits: int = 1, *, sign: bool = False) -> str:
    """Número no formato brasileiro: vírgula nos decimais e ponto nos milhares."""
    text = f"{float(value):{'+' if sign else ''},.{digits}f}"
    return text.replace(",", "\0").replace(".", ",").replace("\0", ".")


def status(ok: bool) -> str:
    return "PASSA" if ok else "FALHA"


def share_text(hits: int, total: int) -> str:
    """A fração com uma casa quando o arredondamento a esconderia: 199 de 200 é 99,5%."""
    if not total:
        return "sem amostra"
    digits = 0 if (hits * 100) % total == 0 else 1
    return f"{br(hits / total * 100, digits)}% de {total}"


def billions(value: Decimal) -> Decimal:
    return value / BILLION


# As estatais fundadas


@dataclass(frozen=True)
class Firm:
    """
    Uma estatal fundada com o caminho inteiro já calculado pela semente: o valor justo, o
    dividendo que o Tesouro recebe a cada mês e o que a venda rende.
    """

    company: StateCompanyDTO
    start: int
    sale: int | None
    policy: DividendPolicy
    values: tuple[Decimal, ...]
    dividends: tuple[Decimal, ...]
    proceeds: Decimal

    def active(self, index: int) -> bool:
        """A fundada conta no mês: da vigência até o mês anterior ao da venda."""
        return self.start <= index and (self.sale is None or index < self.sale)

    def spending(self, index: int) -> Decimal:
        installment = gdp.founding_installment(self.company.invested)
        return installment if 0 <= index - self.start < gdp.FOUNDING_MONTHS else ZERO

    def treasury_dividend(self, index: int) -> Decimal:
        age = index - self.start
        if age < 1 or not self.active(index) or age >= len(self.dividends):
            return ZERO
        return self.dividends[age]

    def asset_sale(self, index: int) -> Decimal:
        return self.proceeds if self.sale == index else ZERO

    def value_on(self, index: int) -> Decimal:
        """O valor justo no mês; zero antes da fundação."""
        age = index - self.start
        return self.values[age] if 0 <= age < len(self.values) else ZERO


@cache
def size_multiplier(policy: DividendPolicy, months: int, step: Decimal) -> Decimal:
    """O porte efetivo depois de `months` meses sob a mesma política; `step` chaveia o cache."""
    return gdp.size_multiplier(itertools.repeat(policy, months))


def make_company(
    index: int,
    size: StateCompanySize,
    lever: StateLever | None,
    run_seed: int,
    setting: Setting,
    start: int,
    sale: int | None,
) -> StateCompanyDTO:
    """A linha da estatal como a fundação a grava: o código, a semente e o retorno médio."""
    ticker = f"EST{chr(65 + index % 26)}{index // 26 % 10}"
    invested = invested_by(size)
    return StateCompanyDTO(
        id=index + 1,
        stock_id=index + 1,
        ticker=ticker,
        origin=StateCompanyOrigin.FOUNDED,
        government_share=FOUNDING_GOVERNMENT_SHARE,
        shares=int(invested / FOUNDING_PRICE),
        lever=lever,
        size=size,
        invested=invested,
        mean_return=fair_value.mean_annual_return(setting.real_interest),
        seed=random.Random(f"{run_seed}:{ticker}").getrandbits(31),
        status=(
            StateCompanyStatus.ACTIVE if sale is None else StateCompanyStatus.PRIVATIZED
        ),
        founded_on=month_start(start),
        offer_opened_on=None,
        privatized_on=None if sale is None else month_start(sale),
        proceeds=None,
    )


@cache
def size_path(
    policy: DividendPolicy, months: int, step: Decimal
) -> tuple[Decimal, ...]:
    """O porte efetivo ao fim de cada mês sob a mesma política; `step` chaveia o cache."""
    return tuple(gdp.size_path(itertools.repeat(policy, months)))


def fair_values(
    company: StateCompanyDTO,
    months: int,
    policy: DividendPolicy = DividendPolicy.NORMAL,
) -> tuple[Decimal, ...]:
    """
    O valor justo m meses depois da fundação, no mesmo passo mensal do backend (um sorteio
    por ano): o crescimento de cada mês soma o retorno médio vezes o quanto o porte efetivo
    da política passa do original.
    """
    assert company.seed is not None and company.mean_return is not None
    sizes = size_path(policy, months, gdp.SIZE_STEP)
    values = [company.invested]
    rate = 0.0
    for month in range(months):
        if month % 12 == 0:
            rate = fair_value.annual_return(
                company.seed, month // 12, company.mean_return
            )
        monthly = rate + float(company.mean_return) * float(sizes[month] - 1)
        values.append(values[-1] * Decimal(str((1 + monthly) ** (1 / 12))))
    return tuple(values)


def build_firm(
    index: int,
    size: StateCompanySize,
    lever: StateLever | None,
    run_seed: int,
    *,
    start: int = 0,
    sale: int | None = None,
    policy: DividendPolicy = DividendPolicy.NORMAL,
    months: int,
    setting: Setting = SETTING,
) -> Firm:
    company = make_company(index, size, lever, run_seed, setting, start, sale)
    values = fair_values(company, months, policy)
    dividends = [ZERO]
    for age in range(1, len(values)):
        profit = max(values[age] - values[age - 1], ZERO)
        dividends.append(
            payout.dividend(profit, policy, StateControl.NONE)
            * company.government_share
        )
    proceeds = ZERO
    if sale is not None and 0 <= sale - start < len(values):
        unit = (values[sale - start] / company.shares).quantize(CENT, ROUND_HALF_UP)
        proceeds = unit * government_shares(company)
    return Firm(company, start, sale, policy, values, tuple(dividends), proceeds)


def sector_push(firms: Sequence[Firm], index: int) -> Decimal:
    """O empurrão permanente no crescimento: o porte efetivo de cada setor, que anda com a política."""
    totals: dict[StateLever | None, Decimal] = {}
    for firm in firms:
        if not firm.active(index):
            continue
        multiplier = size_multiplier(firm.policy, index - firm.start + 1, gdp.SIZE_STEP)
        size = firm.company.size
        assert size is not None
        totals[firm.company.lever] = (
            totals.get(firm.company.lever, ZERO) + Decimal(size.billions) * multiplier
        )
    return gdp.permanent_push(totals)


# A economia mês a mês


@dataclass(frozen=True)
class Course:
    """A economia depois de cada mês fechado: PIB nominal, dívida ÷ PIB, prêmio e dividendos ao Tesouro."""

    gdp: tuple[Decimal, ...]
    debt: tuple[Decimal, ...]
    premium: tuple[Decimal, ...]
    dividends: tuple[Decimal, ...]

    def debt_reais(self, index: int = -1) -> Decimal:
        return self.debt[index] * self.gdp[index]

    def output(self, last: int) -> Decimal:
        """O PIB acumulado até o mês `last`: a soma da produção mensal, em reais."""
        return sum(self.gdp[: last + 1], ZERO) / MONTHS_PER_YEAR


@cache
def base_path(months: int) -> Course:
    """O país sem nenhuma estatal: a referência de todo "contra não fundar"."""
    return simulate((), months)


def simulate(firms: Sequence[Firm], months: int, setting: Setting = SETTING) -> Course:
    """
    Fecha `months` meses com as contas do backend: o passo da dívida, o prêmio de risco e as
    ligações da economia (impulso fiscal, empurrão das estatais e efeito expulsão). O
    crescimento do mês é o da linha de base mais o que a ligação do mês anterior somou, e
    o primário vem do gasto da fundação, dos dividendos e da venda de ativos.
    """
    reference = base_path(months) if firms else None
    gdp_level, debt, prem = setting.gdp, setting.debt, budget.premium(setting.debt)
    window = (setting.selic + prem,) * budget.FIXED_WINDOW_MONTHS
    previous: LinkMonth | None = None
    gaps: list[Decimal] = []
    closed_gdp, closed_debt, closed_prem, closed_div = [], [], [], []
    for index in range(months):
        spending = sum((f.spending(index) for f in firms), ZERO)
        dividends = sum((f.treasury_dividend(index) for f in firms), ZERO)
        assets = sum((f.asset_sale(index) for f in firms), ZERO)
        push = sector_push(firms, index)
        # Os valores em reais viram fração do PIB por ano sobre o PIB com que o mês abre
        spending_ratio = spending * MONTHS_PER_YEAR / gdp_level
        cycle = ZERO if previous is None else previous.cycle_revenue
        primary = (
            setting.primary
            + dividends * MONTHS_PER_YEAR / gdp_level
            - spending_ratio
            + cycle
        )
        growth = setting.growth
        if previous is not None:
            growth += previous.impulse + previous.state_gdp_push + previous.crowding_out
        window = (*window[1:], setting.selic + prem)
        rate = budget.debt_rate(setting.selic, window)
        debt, _ = budget.step(
            debt, rate, setting.ipca, growth, primary, assets / gdp_level
        )
        debt = min(debt, budget.MAX_DEBT)
        prem = budget.premium(debt)
        gdp_level *= (1 + fast_period_rate(growth, MONTHS_PER_YEAR)) * (
            1 + fast_period_rate(setting.ipca, MONTHS_PER_YEAR)
        )
        premium_gap = prem - (reference.premium[index] if reference else prem)
        gaps.append(-spending_ratio)
        previous = link_month(
            previous,
            month_end(index),
            unemployment_gap=ZERO,
            premium_gap=premium_gap,
            growth_gap=growth - setting.growth,
            primary_gap=-spending_ratio,
            primary_gap_year_ago=gaps[index - 12] if index >= 12 else ZERO,
            state_gdp_push=push,
        )
        closed_gdp.append(gdp_level)
        closed_debt.append(debt)
        closed_prem.append(prem)
        closed_div.append(dividends)
    return Course(
        tuple(closed_gdp), tuple(closed_debt), tuple(closed_prem), tuple(closed_div)
    )


# Resultado de cada critério


@dataclass(frozen=True)
class Check:
    """Um critério de aceite: o veredito, o número que o resume e o detalhe para ler."""

    number: int
    title: str
    passed: bool
    summary: str
    details: tuple[str, ...]
    # Os números que a sugestão de constantes cita, para o texto nunca divergir das tabelas
    figures: dict[str, float] = field(default_factory=dict)


def stats(values: Sequence[float]) -> tuple[float, float, float]:
    """Média, mínimo e máximo da amostra."""
    return statistics.fmean(values), min(values), max(values)


def spread(values: Sequence[float], digits: int = 2) -> str:
    mean, low, high = stats(values)
    return f"média {br(mean, digits, sign=True)}, mínimo {br(low, digits, sign=True)}, máximo {br(high, digits, sign=True)}"


# Critério 1: fundar 10 estatais em 10 anos

FOUNDING_LEVERS: tuple[StateLever | None, ...] = (
    StateLever.FUEL,
    StateLever.ENERGY,
    StateLever.BANK,
    None,
)
TEN_YEARS = 120


@dataclass(frozen=True)
class TenFoundings:
    """O que dez fundações (uma por ano) deixam contra o país sem elas, em 10 anos."""

    output_pct: float
    level_pct: float
    debt_pp: float
    debt_reais_bi: float
    dividends_bi: float


def ten_firms(run_seed: int, months: int = 12 * 12) -> list[Firm]:
    """Dez médias de R$ 100 bi, uma por ano, repartidas entre as alavancas e as sem alavanca."""
    return [
        build_firm(
            k,
            StateCompanySize.MEDIUM,
            FOUNDING_LEVERS[k % len(FOUNDING_LEVERS)],
            run_seed,
            start=12 * k,
            months=months,
        )
        for k in range(10)
    ]


def ten_foundings(firms: Sequence[Firm]) -> TenFoundings:
    base = base_path(TEN_YEARS)
    path = simulate(firms, TEN_YEARS)
    last = TEN_YEARS - 1
    return TenFoundings(
        output_pct=float(path.output(last) / base.output(last) - 1) * 100,
        level_pct=float(path.gdp[last] / base.gdp[last] - 1) * 100,
        debt_pp=float(path.debt[last] - base.debt[last]) * 100,
        debt_reais_bi=float(billions(path.debt_reais() - base.debt_reais())),
        dividends_bi=float(billions(sum(path.dividends, ZERO))),
    )


def check_founding(runs: int) -> Check:
    seeds = range(runs)
    all_firms = [ten_firms(seed) for seed in seeds]
    main = [ten_foundings(firms) for firms in all_firms]
    level = [m.level_pct for m in main]
    output = [m.output_pct for m in main]
    debt_pp = [m.debt_pp for m in main]
    debt_bi = [m.debt_reais_bi for m in main]
    dividends = [m.dividends_bi for m in main]
    level_mean = statistics.fmean(level)
    ok = level_mean > 0 and statistics.fmean(dividends) > 0 and level_mean <= 5
    details = [
        "Cenário: 10 estatais médias (R$ 100 bi cada), uma por ano, repartidas entre "
        "combustível, energia, banco e sem alavanca, todas no dividendo normal e sem "
        f"controle de preço. Economia de partida: PIB R$ {br(billions(SETTING.gdp) / 1000, 0)} tri, "
        f"dívida {SETTING.debt:.0%} do PIB, crescimento {br(SETTING.growth * 100)}%, IPCA {br(SETTING.ipca * 100)}%, SELIC {br(SETTING.selic * 100)}%.",
        f"Gasto da fundação: R$ {br(10 * 100, 0)} bi no total, espalhado em 12 meses para cada uma.",
        f"Nível do PIB no mês 120 contra não fundar: {spread(level)} %.",
        f"PIB acumulado nos 10 anos (soma da produção) contra não fundar: {spread(output)} %.",
        f"Dívida ÷ PIB no mês 120 contra não fundar: {spread(debt_pp)} pontos percentuais.",
        f"Dívida em reais no mês 120 contra não fundar: {spread(debt_bi, 0)} R$ bi.",
        f"Dividendos acumulados ao Tesouro em 10 anos: {spread(dividends, 0)} R$ bi.",
        "Como ler: Δ é a diferença entre o país com as estatais e o mesmo país sem elas. "
        "Um nível de PIB +2% significa que, no fim dos 10 anos, a economia é 2% maior "
        "do que seria. Ponto percentual (pp) é a diferença de uma porcentagem para outra: "
        "dívida de 80% para 77% é -3 pp.",
        "Régua: PASSA se o PIB fica acima do cenário sem estatais, o Tesouro recebe "
        "dividendo e o ganho de nível fica até 5% (dez estatais não podem virar o "
        "principal motor de crescimento do país).",
    ]
    details.append("")
    figures: dict[str, float] = {}
    details.extend(sensitivity_founding(all_firms[: max(runs // 4, 20)], figures))
    summary = (
        f"PIB {br(level_mean, 2, sign=True)}% (nível), dívida "
        f"{br(statistics.fmean(debt_pp), 1, sign=True)} pp, dividendos "
        f"R$ {br(statistics.fmean(dividends), 0)} bi, média de {runs} sementes"
    )
    return Check(
        1, "Fundar 10 estatais em 10 anos", ok, summary, tuple(details), figures
    )


K_FACTORS = (Decimal("0.5"), Decimal("0.75"), Decimal(1), Decimal("1.5"), Decimal(2))


def sensitivity_founding(
    all_firms: Sequence[Sequence[Firm]], figures: dict[str, float]
) -> list[str]:
    """O empurrão k e o prazo da fundação trocados, sobre as mesmas sementes."""
    lines = [
        f"Sensibilidade do empurrão no PIB (GDP_PER_ROOT_BILLION, hoje {br(gdp.GDP_PER_ROOT_BILLION, 5)}; k), "
        f"em {len(all_firms)} sementes:",
        "| k | nível do PIB | dívida ÷ PIB |",
        "|---|---|---|",
    ]
    for factor in K_FACTORS:
        with overridden(gdp, GDP_PER_ROOT_BILLION=gdp.GDP_PER_ROOT_BILLION * factor):
            results = [ten_foundings(firms) for firms in all_firms]
        figures[f"k_level_{factor}"] = statistics.fmean(r.level_pct for r in results)
        figures[f"k_debt_{factor}"] = statistics.fmean(r.debt_pp for r in results)
        lines.append(
            f"| {br(factor, 1)}x ({br(gdp.GDP_PER_ROOT_BILLION * factor, 5)}) "
            f"| {br(statistics.fmean(r.level_pct for r in results), 2, sign=True)}% "
            f"| {br(statistics.fmean(r.debt_pp for r in results), 1, sign=True)} pp |"
        )
    lines += [
        "",
        f"Sensibilidade do prazo da fundação (FOUNDING_MONTHS, hoje {gdp.FOUNDING_MONTHS}):",
        "| meses | nível do PIB | dívida ÷ PIB |",
        "|---|---|---|",
    ]
    for months in (6, 12, 24):
        with overridden(gdp, FOUNDING_MONTHS=months):
            results = [ten_foundings(firms) for firms in all_firms]
        figures[f"months_debt_{months}"] = statistics.fmean(r.debt_pp for r in results)
        lines.append(
            f"| {months} "
            f"| {br(statistics.fmean(r.level_pct for r in results), 2, sign=True)}% "
            f"| {br(statistics.fmean(r.debt_pp for r in results), 1, sign=True)} pp |"
        )
    return lines


# Critérios 2 a 4 e 7: o livro das estatais sem banco


def imported_company(index: int, lever: StateLever | None) -> StateCompanyDTO:
    """Uma estatal importada: a base histórica a marcou, sem valor justo nem semente."""
    return StateCompanyDTO(
        id=index + 1,
        stock_id=index + 1,
        ticker=f"IMP{chr(65 + index)}3",
        origin=StateCompanyOrigin.IMPORTED,
        government_share=Decimal("0.5"),
        shares=1_000_000,
        lever=lever,
        size=None,
        invested=ZERO,
        mean_return=None,
        seed=None,
        status=StateCompanyStatus.ACTIVE,
        founded_on=None,
        offer_opened_on=None,
        privatized_on=None,
        proceeds=None,
    )


type Orders = dict[str, StateOrder]
type History = dict[date, Orders]

LEVER_TICKERS = {
    StateLever.FUEL: "IMPA3",
    StateLever.ENERGY: "IMPB3",
    StateLever.BANK: "IMPC3",
}


def lever_book(history: History) -> StateCompanyBook:
    companies = [
        imported_company(index, lever)
        for index, lever in enumerate(
            (StateLever.FUEL, StateLever.ENERGY, StateLever.BANK)
        )
    ]
    return StateCompanyBook(1, 7, lambda: history, companies)


def held_orders(controls: dict[StateLever, StateControl]) -> Orders:
    return {
        LEVER_TICKERS[lever]: StateOrder(control=control)
        for lever, control in controls.items()
    }


def cycle_history(
    controls: dict[StateLever, StateControl], held_months: int, free_months: int = 2
) -> History:
    """As vigências de um ciclo: as ordens por `held_months` meses e depois nenhuma."""
    history: History = {}
    for index in range(held_months):
        history[month_start(index)] = held_orders(controls)
    for index in range(held_months, held_months + free_months):
        history[month_start(index)] = {}
    return history


def cycle_sum(book: StateCompanyBook, months: int) -> tuple[Decimal, list[Decimal]]:
    path = [book.inflation_points(month_start(index)) for index in range(months)]
    return sum(path, ZERO), path


def legal_controls(
    rng: random.Random, lever_set: Sequence[StateLever], held: Decimal
) -> StateControl:
    """Um degrau que o presidente poderia dar agora: o teto de IPCA decide."""
    lever = rng.choice(lever_set)
    free = [s.control for s in levers.step_availability(lever, held) if not s.blocked]
    return rng.choice(free)


def check_hold_and_release(runs: int) -> Check:
    controls = {
        StateLever.FUEL: StateControl.P20,
        StateLever.ENERGY: StateControl.P10,
    }
    held_months = 12
    book = lever_book(cycle_history(controls, held_months))
    total, path = cycle_sum(book, held_months + 2)
    backlog = book.backlog(month_start(held_months - 1))
    spike = path[held_months]
    # Sequências aleatórias de degraus dentro do teto, sempre terminando em meses livres
    rng = random.Random(2026)
    failures = 0
    sequences = max(runs // 2, 20)
    tickers = (StateLever.FUEL, StateLever.ENERGY, StateLever.FUEL)
    for _ in range(sequences):
        history: History = {}
        length = rng.randint(3, 18)
        for index in range(length):
            orders: Orders = {}
            held = ZERO
            for slot, lever in enumerate(tickers):
                free = [
                    s.control
                    for s in levers.step_availability(lever, held)
                    if not s.blocked
                ]
                control = rng.choice(free)
                held += levers.held_points(lever, control)
                orders[f"IMP{chr(65 + slot)}3"] = StateOrder(control=control)
            history[month_start(index)] = orders
        history[month_start(length)] = {}
        history[month_start(length + 1)] = {}
        random_book = StateCompanyBook(
            1,
            7,
            lambda h=history: h,
            [imported_company(slot, lever) for slot, lever in enumerate(tickers)],
        )
        random_total, _ = cycle_sum(random_book, length + 2)
        failures += random_total != 0
    ok = total == 0 and failures == 0
    monthly_spike = float(spike) / MONTHS_PER_YEAR
    details = [
        "Cenário: combustível em P20 e energia em P10 (o máximo que o teto deixa) por "
        f"{held_months} meses e depois solto. Cada mês de controle tira "
        f"{br(levers.total_held_points([(StateLever.FUEL, StateControl.P20), (StateLever.ENERGY, StateControl.P10)]), 2)} "
        "ponto do IPCA e a diferença vai para a represa.",
        f"Soma dos efeitos mensais no IPCA ao longo do ciclo: {br(total, 2)} ponto (esperado 0).",
        f"Represa no fim do controle: {br(backlog, 2)} pontos; no 1º mês solto o IPCA recebe "
        f"+{br(spike, 2)} pontos de uma vez (cerca de +{br(monthly_spike, 2)} ponto percentual "
        "no IPCA daquele mês, porque os pontos valem em 12 meses e o IPCA é mensal).",
        f"Sequências aleatórias de degraus dentro do teto: {sequences - failures} de "
        f"{sequences} somam exatamente 0 ({share_text(sequences - failures, sequences)}).",
        "Como ler: segurar o preço não elimina a inflação, só a adia. Se a soma não "
        "fosse zero, segurar e soltar criaria ou destruiria inflação de graça.",
        f"Observação: o Banco Central lê esses pontos diretamente (a regra soma "
        f"{br(SELIC_REACTION, 1)} ponto de SELIC por ponto de IPCA). No mês da soltura a regra pede "
        f"+{br(float(spike) * SELIC_REACTION, 1)} pontos de SELIC; o Banco autônomo anda no máximo "
        "1 ponto por reunião, mas o presidente bot leria o pedido inteiro.",
    ]
    summary = f"soma do ciclo {br(total, 2)} ponto; represa {br(backlog, 1)} pontos voltam num mês"
    return Check(2, "Segurar e soltar devolve a inflação", ok, summary, tuple(details))


def check_bank() -> Check:
    steps = [c for c in StateControl if c is not StateControl.NONE]
    held = [levers.held_points(StateLever.BANK, c) for c in steps]
    credit = [levers.credit_points(StateLever.BANK, c) for c in steps]
    others = [
        levers.credit_points(lever, c)
        for lever in (StateLever.FUEL, StateLever.ENERGY)
        for c in steps
    ]
    book = lever_book(
        cycle_history({StateLever.BANK: StateControl.P20}, 12, free_months=2)
    )
    total, path = cycle_sum(book, 14)
    ok = (
        all(point == 0 for point in held)
        and all(point > 0 for point in credit)
        and all(point == 0 for point in others)
        and all(point == 0 for point in path)
        and book.credit_points(month_start(0)) == credit[-1]
    )
    details = [
        "Cenário: banco estatal em cada degrau, e depois P20 por 12 meses e solto.",
        "Pontos de IPCA que o Banco segura por degrau (P5, P10, P15, P20): "
        + ", ".join(br(p, 2) for p in held)
        + " (esperado 0).",
        "Pontos de juro do crédito que o Banco tira por degrau: "
        + ", ".join(br(p, 2) for p in credit)
        + ".",
        f"Efeito no IPCA ao longo do ciclo de 14 meses: soma {br(total, 2)}; maior mês "
        f"{br(max(path), 2)}, menor {br(min(path), 2)} (esperado tudo 0).",
        "Combustível e energia não mexem no juro do crédito: "
        + ("0 em todos os degraus." if all(p == 0 for p in others) else "FALHA."),
        "Como ler: o Banco estatal só barateia o empréstimo (P20 tira "
        f"{br(credit[-1], 2)} ponto de juro, por exemplo de 12% para 11% ao ano) e não "
        "entra na conta da inflação, então não gera represa.",
    ]
    summary = f"IPCA {br(max(abs(p) for p in path), 2)} ponto; juro do crédito {br(credit[-1], 2)} ponto no P20"
    return Check(3, "O Banco não baixa o IPCA", ok, summary, tuple(details))


def check_cap(runs: int) -> Check:
    lever_slots = (
        StateLever.FUEL,
        StateLever.ENERGY,
        StateLever.BANK,
        StateLever.FUEL,
        StateLever.ENERGY,
    )
    companies = [imported_company(i, lever) for i, lever in enumerate(lever_slots)]
    book = StateCompanyBook(1, 7, lambda: {}, companies)
    tickers = [c.ticker for c in companies]
    controls = list(StateControl)

    def grant(orders: Orders, slot: int, control: StateControl) -> bool:
        """O presidente tenta o degrau: vale só se o teto das outras estatais deixa."""
        lever = lever_slots[slot]
        if control is not StateControl.NONE:
            others = book.other_points(tickers[slot], orders)
            step = next(
                s
                for s in levers.step_availability(lever, others)
                if s.control is control
            )
            if step.blocked:
                return False
        orders[tickers[slot]] = StateOrder(control=control)
        return True

    def total(orders: Orders) -> Decimal:
        return (
            book.held_points_for(orders)
            if False
            else levers.total_held_points(
                (lever_slots[tickers.index(t)], o.control)
                for t, o in orders.items()
                if lever_slots[tickers.index(t)] is not StateLever.BANK
                or o.control is not StateControl.NONE
            )
        )

    highest = ZERO
    combos = blocked = 0
    for wanted in itertools.product(controls, repeat=len(lever_slots)):
        orders: Orders = {}
        for slot, control in enumerate(wanted):
            blocked += not grant(orders, slot, control)
        highest = max(highest, total(orders))
        combos += 1
    rng = random.Random(2026)
    walks = max(runs, 100) * 100
    orders = {}
    for _ in range(walks):
        blocked += not grant(
            orders, rng.randrange(len(lever_slots)), rng.choice(controls)
        )
        highest = max(highest, total(orders))
    ok = highest <= levers.IPCA_CAP_POINTS
    details = [
        f"Cenário: 5 estatais (combustível x2, energia x2, banco). Todas as {combos} "
        f"combinações de degraus que o presidente pode pedir, na ordem, e mais {walks} "
        "mudanças aleatórias seguidas, cada uma aceita só se o degrau não está bloqueado.",
        f"Maior soma de pontos de IPCA que as ordens aceitas seguraram juntas: "
        f"{br(highest, 2)} (teto {br(levers.IPCA_CAP_POINTS, 2)}).",
        f"Pedidos barrados pelo teto: {blocked}.",
        "Como ler: o teto é a quantidade de inflação que o presidente pode empurrar "
        "para depois de uma vez. 1,5 ponto é a banda de tolerância da meta de inflação, "
        "então com a meta em 3% o governo disfarça no máximo até 4,5%.",
        "Sensibilidade do teto: a represa máxima volta toda de uma vez, e cresce com o "
        "teto e com o tempo de controle.",
        "| teto | represa em 6 meses | em 12 meses | em 24 meses |",
        "|---|---|---|---|",
    ]
    details.extend(
        f"| {br(cap, 1)} | {br(cap * 6, 1)} | {br(cap * 12, 1)} | {br(cap * 24, 1)} |"
        for cap in (Decimal(1), Decimal("1.5"), Decimal(2))
    )
    summary = f"maior soma {br(highest, 2)} ponto contra teto de {br(levers.IPCA_CAP_POINTS, 1)}"
    return Check(4, "O teto de 1,5 ponto se respeita", ok, summary, tuple(details))


def check_imported_default() -> Check:
    history: History = {
        month_start(0): {"OUTRA3": StateOrder(control=StateControl.P20)},
        month_start(3): {"IMPA3": StateOrder()},
    }
    book = lever_book(history)
    days = [
        date(START_YEAR, 1, 1),
        date(START_YEAR, 2, 15),
        date(START_YEAR + 2, 6, 30),
    ]
    price_factors = {book.price_factor("IMPA3", day) for day in days}
    dividend_factors = {book.dividend_factor("IMPA3", day) for day in days}
    unknown = {book.price_factor("PETR4", day) for day in days}
    direct = (
        price.price_factor(StateOrder()),
        price.dividend_factor(StateOrder()),
        payout.dividend_factor(DividendPolicy.NORMAL, StateControl.NONE),
    )
    ok = (
        price_factors == {1.0}
        and dividend_factors == {1.0}
        and unknown == {1.0}
        and direct == (1.0, 1.0, Decimal(1))
    )
    details = [
        "Cenário: a importada sem ordem, com ordem padrão escrita no histórico e com "
        "ordem de outra estatal no histórico, em três dias.",
        f"Fator de preço do livro: {sorted(price_factors)}; fator de dividendo: {sorted(dividend_factors)}; "
        f"ação que não é estatal: {sorted(unknown)} (esperado 1 em todos).",
        f"Contas diretas (preço, dividendo, payout normal sem controle): {direct[0]}, {direct[1]}, {direct[2]} (esperado 1 exato).",
        "Como ler: sem ordem do presidente a ação importada anda exatamente como a "
        "história. Fator 1 significa preço e dividendo iguais aos da série histórica; "
        "qualquer diferença apareceria como efeito fantasma em partidas sem governo.",
    ]
    return Check(
        7,
        "A importada sem ordem segue o histórico",
        ok,
        "fator de preço 1 e de dividendo 1, exatos",
        tuple(details),
    )


# Critério 5: espremer e reinvestir contra o dividendo normal

POLICIES = (DividendPolicy.NORMAL, DividendPolicy.SQUEEZE, DividendPolicy.REINVEST)
POLICY_NAMES = {
    DividendPolicy.NORMAL: "Normal",
    DividendPolicy.SQUEEZE: "Espremer",
    DividendPolicy.REINVEST: "Reinvestir",
}
POLICY_YEARS = 5
LONG_YEARS = 20
PREVIEW_YEARS = price.PREVIEW_MONTHS // 12


@dataclass(frozen=True)
class PolicyRun:
    """Uma política contra o dividendo normal na mesma semente, ao fim de N anos."""

    dividends_bi: float
    level_pct: float
    value_pct: float
    treasury_bi: float


def policy_firms(run_seed: int, months: int) -> dict[DividendPolicy, Firm]:
    return {
        policy: build_firm(
            0,
            StateCompanySize.LARGE,
            None,
            run_seed,
            policy=policy,
            months=months,
        )
        for policy in POLICIES
    }


def treasury_gain(
    firms: dict[DividendPolicy, Firm], policy: DividendPolicy, months: int
) -> tuple[float, float, float]:
    """Contra o normal em `months` meses: o dividendo a mais, o valor da empresa e o ganho do Tesouro (dividendo mais a fatia do valor)."""
    normal, mine = firms[DividendPolicy.NORMAL], firms[policy]
    extra = sum(
        (mine.dividends[m] - normal.dividends[m] for m in range(1, months + 1)), ZERO
    )
    value, value_normal = mine.values[months], normal.values[months]
    held = mine.company.government_share
    gain = extra + (value - value_normal) * held
    return (
        float(billions(extra)),
        float(value / value_normal - 1) * 100,
        float(billions(gain)),
    )


def policy_run(
    firms: dict[DividendPolicy, Firm], policy: DividendPolicy, months: int
) -> PolicyRun:
    base = simulate([firms[DividendPolicy.NORMAL]], months)
    path = simulate([firms[policy]], months)
    extra, value_pct, gain = treasury_gain(firms, policy, months)
    return PolicyRun(
        dividends_bi=extra,
        level_pct=float(path.gdp[-1] / base.gdp[-1] - 1) * 100,
        value_pct=value_pct,
        treasury_bi=gain,
    )


GAIN_YEARS = 10


def mean_gains(
    all_firms: Sequence[dict[DividendPolicy, Firm]], policy: DividendPolicy
) -> list[float]:
    """O ganho do Tesouro com a política contra o Normal, em R$ bi, ao fim de cada ano de 1 a GAIN_YEARS, na média das sementes."""
    return [
        statistics.fmean(
            treasury_gain(firms, policy, 12 * year)[2] for firms in all_firms
        )
        for year in range(1, GAIN_YEARS + 1)
    ]


def turn_year(gains: Sequence[float]) -> int | None:
    """O primeiro ano em que o ganho do Tesouro tem o sinal contrário ao do ano 1; None se nunca troca."""
    for year, gain in enumerate(gains[1:], start=2):
        if gain * gains[0] < 0:
            return year
    return None


def turn_text(gains: Sequence[float], name: str) -> str:
    """O sentido da troca: quem ganha primeiro perde depois, e o contrário."""
    year = turn_year(gains)
    if year is None:
        sense = "ganha" if gains[0] > 0 else "perde"
        return f"{name}: o Tesouro {sense} em todos os {GAIN_YEARS} anos"
    first, then = ("ganha", "perde") if gains[0] > 0 else ("perde", "ganha")
    return f"{name}: o Tesouro {first} até o ano {year - 1} e {then} a partir do ano {year}"


def check_policy(runs: int) -> Check:
    months = 12 * LONG_YEARS
    seeds = range(max(runs // 4, 20))
    all_firms = [policy_firms(seed, months) for seed in seeds]
    horizon = 12 * POLICY_YEARS
    results = {
        policy: [policy_run(firms, policy, horizon) for firms in all_firms]
        for policy in (DividendPolicy.SQUEEZE, DividendPolicy.REINVEST)
    }

    def mean(policy: DividendPolicy, field: str) -> float:
        return statistics.fmean(getattr(r, field) for r in results[policy])

    squeeze, reinvest = DividendPolicy.SQUEEZE, DividendPolicy.REINVEST
    gains = {policy: mean_gains(all_firms, policy) for policy in (squeeze, reinvest)}
    squeeze_turn = turn_year(gains[squeeze])
    reinvest_turn = turn_year(gains[reinvest])
    # Espremer rende ao Tesouro nos 3 primeiros anos e passa a custar entre o 4º e o 6º; Reinvestir é o espelho
    turns_in_window = all(
        turn is not None and MANDATE_YEARS <= turn <= MANDATE_YEARS + 2
        for turn in (squeeze_turn, reinvest_turn)
    )
    first_years = all(
        gains[squeeze][year] > 0 and gains[reinvest][year] < 0 for year in range(3)
    )
    ok = (
        mean(squeeze, "dividends_bi") > 0
        and mean(squeeze, "level_pct") < 0
        and mean(squeeze, "value_pct") < 0
        and mean(reinvest, "dividends_bi") < 0
        and mean(reinvest, "level_pct") > 0
        and mean(reinvest, "value_pct") > 0
        and first_years
        and turns_in_window
    )
    details = [
        f"Cenário: uma estatal grande (R$ 300 bi), sem controle de preço, por {POLICY_YEARS} anos "
        f"em cada política, contra a mesma estatal no dividendo normal ({len(seeds)} sementes).",
        "| política | dividendo a mais ao Tesouro | nível do PIB | valor da empresa | ganho total do Tesouro |",
        "|---|---|---|---|---|",
    ]
    details.extend(
        f"| {POLICY_NAMES[policy]} (payout {br(payout.payout_ratio(policy), 2)} contra "
        f"{br(payout.payout_ratio(DividendPolicy.NORMAL), 2)}) "
        f"| R$ {br(mean(policy, 'dividends_bi'), 2, sign=True)} bi "
        f"| {br(mean(policy, 'level_pct'), 3, sign=True)}% "
        f"| {br(mean(policy, 'value_pct'), 1, sign=True)}% "
        f"| R$ {br(mean(policy, 'treasury_bi'), 2, sign=True)} bi |"
        for policy in (squeeze, reinvest)
    )
    details += [
        "Como ler: payout é a fração do lucro paga como dividendo (0,80 é 80%). O "
        "valor da empresa é o valor justo, que cresce menos quando o porte efetivo "
        "encolhe e mais quando ele aumenta; o ganho total do Tesouro soma o dividendo a mais "
        "com a fatia de 51% do governo nessa diferença de valor. Espremer rende caixa "
        "agora e cobra no crescimento depois.",
        f"Estatal importada (as mesmas contas diretas): preço do Espremer em "
        f"{PREVIEW_YEARS} anos seguidos {br(price.sustained_policy_factor(squeeze), 3)} do preço sem ordem e "
        f"dividendo {br(price.dividend_factor(StateOrder(dividend_policy=squeeze)), 2)}; "
        f"Reinvestir, preço {br(price.sustained_policy_factor(reinvest), 3)} e dividendo "
        f"{br(price.dividend_factor(StateOrder(dividend_policy=reinvest)), 2)}.",
        "Régua: PASSA se Espremer dá mais dividendo e deixa PIB e valor menores, e "
        "Reinvestir dá o inverso, sempre contra o Normal; e se o Tesouro, na média das "
        "sementes, ganha com o Espremer nos anos 1 a 3 e passa a perder entre o ano "
        f"{MANDATE_YEARS} e o {MANDATE_YEARS + 2}, com o Reinvestir no espelho.",
        "",
        f"Ganho do Tesouro por ano contra o Normal, em R$ bi (média de {len(seeds)} sementes; "
        "positivo é o Tesouro ganhando). Um mandato dura 4 anos:",
        "| política | "
        + " | ".join(f"ano {y}" for y in range(1, GAIN_YEARS + 1))
        + " |",
        "|---|" + "---|" * GAIN_YEARS,
    ]
    details.extend(
        f"| {POLICY_NAMES[policy]} | "
        + " | ".join(br(g, 1, sign=True) for g in gains[policy])
        + " |"
        for policy in (squeeze, reinvest)
    )
    details += [
        turn_text(gains[squeeze], "Espremer"),
        turn_text(gains[reinvest], "Reinvestir"),
        "",
        "Sensibilidade do ritmo do porte (SIZE_STEP, hoje "
        f"{br(gdp.SIZE_STEP, 2)} ao mês): o ano em que o Tesouro troca de lado e o PIB em "
        f"{POLICY_YEARS} anos.",
        "| passo | Espremer | Reinvestir | PIB com Espremer | PIB com Reinvestir |",
        "|---|---|---|---|---|",
    ]
    figures: dict[str, float] = {}
    for policy, name in ((squeeze, "squeeze"), (reinvest, "reinvest")):
        figures[f"{name}_dividends_bi"] = mean(policy, "dividends_bi")
        figures[f"{name}_level_pct"] = mean(policy, "level_pct")
        figures[f"{name}_value_pct"] = mean(policy, "value_pct")
        figures[f"{name}_treasury_bi"] = mean(policy, "treasury_bi")
        figures[f"{name}_turn"] = turn_year(gains[policy]) or 0
    for step in (Decimal("0.005"), Decimal("0.01"), Decimal("0.02")):
        with overridden(gdp, SIZE_STEP=step):
            sample = [
                policy_firms(seed, 12 * GAIN_YEARS)
                for seed in range(min(len(seeds), 20))
            ]
            turns = {
                policy: turn_year(mean_gains(sample, policy))
                for policy in (squeeze, reinvest)
            }
            levels = {
                policy: statistics.fmean(
                    policy_run(firms, policy, horizon).level_pct for firms in sample
                )
                for policy in (squeeze, reinvest)
            }
        never = f"nunca em {GAIN_YEARS} anos"
        details.append(
            f"| {br(step, 3)} "
            f"| {turns[squeeze] or never} "
            f"| {turns[reinvest] or never} "
            f"| {br(levels[squeeze], 3, sign=True)}% | {br(levels[reinvest], 3, sign=True)}% |"
        )
    summary = (
        f"Espremer: dividendo {br(mean(squeeze, 'dividends_bi'), 1, sign=True)} bi, "
        f"PIB {br(mean(squeeze, 'level_pct'), 3, sign=True)}%, valor {br(mean(squeeze, 'value_pct'), 1, sign=True)}%, "
        f"Tesouro perde a partir do ano {squeeze_turn}; "
        f"Reinvestir: PIB {br(mean(reinvest, 'level_pct'), 3, sign=True)}%, valor {br(mean(reinvest, 'value_pct'), 1, sign=True)}%, "
        f"Tesouro ganha a partir do ano {reinvest_turn}"
    )
    return Check(
        5, "Espremer e reinvestir contra o Normal", ok, summary, tuple(details), figures
    )


# Critério 6: fundar e privatizar ao valor justo

POLICY_SIZE_NAMES = {
    StateCompanySize.SMALL: "pequena",
    StateCompanySize.MEDIUM: "média",
    StateCompanySize.LARGE: "grande",
}

HOLD_YEARS = (1, 2, 4, 8, 12, 20)
AFTER_SALE_MONTHS = 24


@dataclass(frozen=True)
class Cycle:
    """O ciclo fundar → privatizar contra o país que nada fez, medido dois anos depois da venda."""

    debt_pp: float
    debt_reais_bi: float


def founding_cycle(
    size: StateCompanySize, run_seed: int, hold_years: int, setting: Setting = SETTING
) -> Cycle:
    sale = 12 * hold_years
    months = sale + AFTER_SALE_MONTHS
    firm = build_firm(
        0, size, None, run_seed, sale=sale, months=months + 1, setting=setting
    )
    path, base = simulate([firm], months, setting), base_path(months)
    return Cycle(
        debt_pp=float(path.debt[-1] - base.debt[-1]) * 100,
        debt_reais_bi=float(billions(path.debt_reais() - base.debt_reais())),
    )


def cycle_mean(cycles: Sequence[Cycle]) -> float:
    return statistics.fmean(c.debt_pp for c in cycles)


def cycle_row(label: str, cycles: Sequence[Cycle]) -> str:
    pp = [c.debt_pp for c in cycles]
    bi = [c.debt_reais_bi for c in cycles]
    hits = sum(value >= 0 for value in pp)
    return (
        f"| {label} | {br(statistics.fmean(pp), 2, sign=True)} / {br(min(pp), 2, sign=True)} / "
        f"{br(max(pp), 2, sign=True)} | {br(statistics.fmean(bi), 0, sign=True)} / {br(min(bi), 0, sign=True)} / "
        f"{br(max(bi), 0, sign=True)} | {share_text(hits, len(pp))} |"
    )


def cell(cycles: Sequence[Cycle]) -> str:
    """A média em pp e a fração das sementes com Δ ≥ 0, com a amostra."""
    hits = sum(c.debt_pp >= 0 for c in cycles)
    return (
        f"{br(cycle_mean(cycles), 2, sign=True)} pp ({share_text(hits, len(cycles))})"
    )


TABLE_HEAD = (
    "| {} | Δ dívida ÷ PIB em pp (média / mín. / máx.) | Δ dívida em R$ bi (média / mín. / máx.) | sementes com Δ ≥ 0 |",
    "|---|---|---|---|",
)


def k_label(factor: Decimal) -> str:
    return f"empurrão k = {br(gdp.GDP_PER_ROOT_BILLION * factor, 6)} ({br(factor, 2)}x)"


def check_privatization_cycle(runs: int) -> Check:
    samples = max(runs // 4, 20)
    horizons = {
        years: [
            founding_cycle(StateCompanySize.MEDIUM, seed, years) for seed in range(runs)
        ]
        for years in HOLD_YEARS
    }
    every_pass = all(cycle_mean(cycles) >= 0 for cycles in horizons.values())
    first_fail = next(
        (years for years, cycles in horizons.items() if cycle_mean(cycles) < 0), None
    )
    figures = {f"mean_{years}": cycle_mean(c) for years, c in horizons.items()}
    by_size = [
        TABLE_HEAD[0].format("porte (prazo de 4 anos)"),
        TABLE_HEAD[1],
    ]
    by_size.extend(
        cycle_row(
            f"{POLICY_SIZE_NAMES[size]} (R$ {size.billions} bi)",
            [founding_cycle(size, seed, 4) for seed in range(samples)],
        )
        for size in StateCompanySize
    )
    # Cada variante troca constantes só durante a conta; a primeira é o backend como está
    variants: tuple[
        tuple[str, tuple[tuple[ModuleType, dict[str, object]], ...]], ...
    ] = (
        ("constantes de hoje", ()),
        (
            "desconto do retorno 2 pp",
            ((fair_value, {"MEAN_RETURN_DISCOUNT": Decimal("0.02")}),),
        ),
        (
            "desconto do retorno 3 pp",
            ((fair_value, {"MEAN_RETURN_DISCOUNT": Decimal("0.03")}),),
        ),
        (
            "desconto do retorno 4 pp",
            ((fair_value, {"MEAN_RETURN_DISCOUNT": Decimal("0.04")}),),
        ),
        ("volatilidade 5%", ((fair_value, {"ANNUAL_VOLATILITY": 0.05}),)),
        ("volatilidade 20%", ((fair_value, {"ANNUAL_VOLATILITY": 0.20}),)),
        *(
            (
                k_label(factor),
                ((gdp, {"GDP_PER_ROOT_BILLION": gdp.GDP_PER_ROOT_BILLION * factor}),),
            )
            for factor in (Decimal("0.5"), Decimal("0.75"))
        ),
        ("sem empurrão no PIB (k = 0)", ((gdp, {"GDP_PER_ROOT_BILLION": ZERO}),)),
    )
    sensitivity = [
        "| variante | prazo de 8 anos | prazo de 20 anos |",
        "|---|---|---|",
    ]
    for label, changes in variants:
        cells = []
        for years in (8, 20):
            with ExitStack() as stack:
                for module, values in changes:
                    stack.enter_context(overridden(module, **values))
                cycles = [
                    founding_cycle(StateCompanySize.MEDIUM, seed, years)
                    for seed in range(samples)
                ]
            cells.append(cell(cycles))
            figures[f"variant_{label}_{years}"] = cycle_mean(cycles)
        sensitivity.append(f"| {label} | {cells[0]} | {cells[1]} |")
    pp = [c.debt_pp for c in horizons[4]]
    hits = sum(value >= 0 for value in pp)
    mean, low, high = stats(pp)
    figures.update(mean_4=mean, share_4=hits / len(pp))
    details = [
        "Cenário: uma estatal média (R$ 100 bi) fundada no mês 0, segurada pelo prazo "
        f"da tabela e privatizada ao valor justo; a dívida é medida {AFTER_SALE_MONTHS} meses depois da "
        "venda, contra o país que nada fez. O governo põe o capital inteiro e fica com "
        "51% das ações, e a venda rende o valor justo dessa fatia.",
        f"Ciclo de 4 anos (um mandato): Δ dívida ÷ PIB {spread(pp)} pp; "
        f"{share_text(hits, len(pp))} das sementes têm Δ ≥ 0.",
        "Como ler: Δ dívida ≥ 0 quer dizer que o ciclo não deixou o país com dívida menor "
        "do que se nada tivesse feito, ou seja, fundar e vender não fabrica dinheiro. "
        "Semente é uma rodada sorteada dos retornos anuais da empresa; mil sementes "
        "são mil futuros possíveis. A coluna em reais confere o mesmo sem a ajuda do "
        "PIB maior (a dívida em pp também cai quando o PIB cresce).",
        "Régua: PASSA se a média é ≥ 0 em todos os prazos da primeira tabela.",
        (
            "Resultado: a média fica ≥ 0 em todos os prazos."
            if every_pass
            else f"Resultado: a média vira negativa a partir de {first_fail} anos com a estatal."
        ),
        "",
        *(TABLE_HEAD[0].format("prazo com a estatal"), TABLE_HEAD[1]),
        *(cycle_row(f"{years} ano(s)", c) for years, c in horizons.items()),
        "",
        *by_size,
        "",
        "Sensibilidade do valor justo (porte médio; média em pp e fração das sementes com Δ ≥ 0):",
        *sensitivity,
    ]
    summary = (
        f"4 anos: Δ dívida ÷ PIB {br(mean, 2, sign=True)} pp (mín. {br(low, 2, sign=True)}, máx. "
        f"{br(high, 2, sign=True)}), {share_text(hits, len(pp))} com Δ ≥ 0"
        + ("" if every_pass else f"; média negativa a partir de {first_fail} anos")
    )
    return Check(
        6,
        "Fundar e privatizar ao valor justo",
        every_pass,
        summary,
        tuple(details),
        figures,
    )


# Conferência do protótipo com o livro das estatais


def check_against_book() -> Check:
    """As contas mensais do protótipo contra as do livro do backend, nas mesmas estatais."""
    sizes = (StateCompanySize.SMALL, StateCompanySize.MEDIUM, StateCompanySize.LARGE)
    leversets = (StateLever.FUEL, StateLever.FUEL, None)
    firms = [
        build_firm(
            i,
            sizes[i],
            leversets[i],
            11,
            start=3 * i,
            sale=40 if i == 1 else None,
            policy=POLICIES[i],
            months=60,
        )
        for i in range(3)
    ]
    history: History = {}
    for firm in firms:
        history.setdefault(month_start(firm.start), {})[firm.company.ticker] = (
            StateOrder(dividend_policy=firm.policy)
        )
    # Ordens em vigor desde o primeiro mês; a política de cada uma vale até o fim
    merged: Orders = {}
    full: History = {}
    for index in range(60):
        merged.update(history.get(month_start(index), {}))
        full[month_start(index)] = dict(merged)
    companies = [
        firm.company.model_copy(
            update={"proceeds": firm.proceeds if firm.sale is not None else None}
        )
        for firm in firms
    ]
    book = StateCompanyBook(1, 11, lambda: full, companies)
    worst = Decimal(0)
    for index in (1, 5, 13, 25, 39, 40, 41, 55):
        month = month_start(index)
        mine = {
            "gasto da fundação": (
                sum((f.spending(index) for f in firms), ZERO),
                book.founding_spending(month),
            ),
            "dividendo ao Tesouro": (
                sum((f.treasury_dividend(index) for f in firms), ZERO),
                book.treasury_dividends(month),
            ),
            "empurrão no PIB": (sector_push(firms, index), book.gdp_push(month)),
            "venda de ativos": (
                sum((f.asset_sale(index) for f in firms), ZERO),
                book.assets_in(month_end(index)),
            ),
        }
        for theirs_mine, theirs_book in mine.values():
            scale = max(abs(theirs_book), Decimal(1))
            worst = max(worst, abs(theirs_mine - theirs_book) / scale)
    ok = worst < Decimal("1e-9")
    details = [
        "Cenário: três estatais fundadas em meses diferentes, uma privatizada no mês 40, "
        "cada uma numa política; oito meses conferidos.",
        f"Maior diferença relativa entre o protótipo e o livro (gasto, dividendo, "
        f"empurrão no PIB, venda): {worst:.1e} (esperado abaixo de 1e-9).",
    ]
    return Check(
        0,
        "Conferência do protótipo com o livro",
        ok,
        f"diferença máxima {worst:.1e}".replace("0.0e+1", "0"),
        tuple(details),
    )


# Relatório


def acceptance_table(checks: Sequence[Check]) -> list[str]:
    lines = ["| # | critério | veredito | número |", "|---|---|---|---|"]
    lines += [
        f"| {c.number} | {c.title} | {status(c.passed)} | {c.summary} |"
        for c in checks
        if c.number
    ]
    return lines


MANDATE_YEARS = 4
CYCLE_K_FACTORS = (Decimal(1), Decimal("0.75"), Decimal("0.5"))


def figure(checks: Sequence[Check], number: int, key: str) -> float:
    return next(c for c in checks if c.number == number).figures[key]


def suggestions(checks: Sequence[Check], runs: int) -> list[str]:
    """
    As constantes que o protótipo recomenda, cada uma com o porquê em linguagem simples e
    um exemplo com número. Os números medidos vêm das tabelas dos critérios; os de conta
    de cabeça vêm das próprias constantes.
    """
    cap = levers.IPCA_CAP_POINTS
    weight_fuel = levers.LEVER_WEIGHT[StateLever.FUEL]
    weight_energy = levers.LEVER_WEIGHT[StateLever.ENERGY]
    fuel_p20 = levers.held_points(StateLever.FUEL, StateControl.P20)
    energy_p10 = levers.held_points(StateLever.ENERGY, StateControl.P10)
    credit_p20 = levers.credit_points(StateLever.BANK, StateControl.P20)
    cut_p20 = payout.profit_cut(StateControl.P20)
    real = SETTING.real_interest
    normal_payout = payout.payout_ratio(DividendPolicy.NORMAL)
    sample = max(runs // 4, 20)

    # Desconto: o retorno total do dono (alta do valor mais dividendo) não passa do juro real
    mean_today = real - fair_value.MEAN_RETURN_DISCOUNT
    total_today = mean_today * (1 + normal_payout)
    discount = Decimal(str(round(float(real - real / (1 + normal_payout)), 2)))
    total_pick = (real - discount) * (1 + normal_payout)

    # Preço da política: o ano em que o Tesouro troca de lado, medido no critério 5
    squeeze_turn = int(figure(checks, 5, "squeeze_turn"))
    reinvest_turn = int(figure(checks, 5, "reinvest_turn"))
    reference_growth = price.POLICY_REFERENCE_GROWTH
    squeeze_preview = price.sustained_policy_factor(DividendPolicy.SQUEEZE)
    reinvest_preview = price.sustained_policy_factor(DividendPolicy.REINVEST)
    preview_loss_example = 100 * (1 - squeeze_preview)

    # Empurrão k: o maior fator testado em que o ciclo de 20 anos não deixa o governo ganhando
    def cycle_20(factor: Decimal) -> float:
        if factor == 1:
            return figure(checks, 6, "mean_20")
        return figure(checks, 6, f"variant_{k_label(factor)}_20")

    def cycle_8(factor: Decimal) -> float:
        if factor == 1:
            return figure(checks, 6, "mean_8")
        return figure(checks, 6, f"variant_{k_label(factor)}_8")

    k_pick = next((f for f in CYCLE_K_FACTORS if cycle_20(f) >= 0), CYCLE_K_FACTORS[-1])
    k_value = gdp.GDP_PER_ROOT_BILLION * k_pick
    k_keep = k_pick == 1
    push_today = math.sqrt(100) * float(gdp.GDP_PER_ROOT_BILLION) * 100
    push_pick = math.sqrt(100) * float(k_value) * 100
    hits_4 = round(figure(checks, 6, "share_4") * runs)

    # Porte: um mandato inteiro de Espremer
    months_mandate = 12 * MANDATE_YEARS
    multiplier = max(gdp.MIN_SIZE_MULTIPLIER, 1 - gdp.SIZE_STEP * months_mandate)
    months_to_floor = int((1 - gdp.MIN_SIZE_MULTIPLIER) / gdp.SIZE_STEP)

    volatility = fair_value.ANNUAL_VOLATILITY
    sigmas = (float(mean_today) - fair_value.MIN_ANNUAL_RETURN) / volatility

    lines = [
        "Valores recomendados para as constantes ainda provisórias e as calibradas, cada um com o motivo e "
        "um exemplo. Os números medidos vêm das tabelas acima, com "
        f"{runs} sementes (e {sample} nas sensibilidades mais pesadas). Como ler os termos: "
        "Δ (delta) é a diferença entre o país com a estatal e o mesmo país sem ela; "
        "pp (ponto percentual) é a distância entre duas porcentagens, de 75% para 74% "
        "da dívida ÷ PIB é -1 pp; semente (seed) é um sorteio fixo dos retornos anuais "
        f"de cada empresa, então {runs} sementes são {runs} futuros possíveis da mesma "
        "economia.",
        "",
        "| constante | hoje | recomendado |",
        "|---|---|---|",
        f"| IPCA_CAP_POINTS | {br(cap, 1)} | manter |",
        f"| LEVER_WEIGHT (combustível, energia, banco) | {br(weight_fuel, 2)}, {br(weight_energy, 2)}, 0 | manter |",
        f"| CREDIT_WEIGHT (banco) | {br(levers.CREDIT_WEIGHT[StateLever.BANK], 2)} | manter |",
        f"| POLICY_REFERENCE_GROWTH | {br(reference_growth, 2)} | manter |",
        f"| GDP_PER_ROOT_BILLION (k) | {br(gdp.GDP_PER_ROOT_BILLION, 6)} | {'manter' if k_keep else br(k_value, 6)} |",
        f"| SIZE_STEP e limites do porte | {br(gdp.SIZE_STEP, 2)}, de {br(gdp.MIN_SIZE_MULTIPLIER, 1)} a {br(gdp.MAX_SIZE_MULTIPLIER, 1)} | manter |",
        f"| FOUNDING_MONTHS | {gdp.FOUNDING_MONTHS} | manter |",
        f"| MEAN_RETURN_DISCOUNT | {br(fair_value.MEAN_RETURN_DISCOUNT, 2)} | {br(discount, 2)} |",
        f"| ANNUAL_VOLATILITY e limites do retorno anual | {br(volatility, 2)}, de {br(fair_value.MIN_ANNUAL_RETURN, 1)} a {br(fair_value.MAX_ANNUAL_RETURN, 1)} | manter |",
        "",
        f"IPCA_CAP_POINTS = {br(cap, 1)} (manter). É o teto do que o governo consegue "
        "esconder da inflação segurando preço, e coincide com a banda de tolerância da "
        "meta de inflação (3% com 1,5 ponto para cima ou para baixo). Exemplo: combustível "
        f"no degrau P20 segura {br(fuel_p20, 2)} ponto e energia no P10 segura {br(energy_p10, 2)}, "
        f"juntos {br(fuel_p20 + energy_p10, 2)}, abaixo do teto. O critério 4 testou todas as combinações "
        f"de degraus: a maior soma permitida foi exatamente {br(cap, 2)}, nunca acima.",
        "",
        "LEVER_WEIGHT (manter). Peso é a fatia do IPCA que cada ponto percentual de "
        f"preço segurado representa. Combustível pesa {br(weight_fuel * 100, 0)}% e energia "
        f"{br(weight_energy * 100, 0)}%, a ordem de grandeza desses itens na cesta do IPCA (valores "
        "arredondados, não tirados da tabela oficial). Exemplo: segurar o combustível 20% "
        f"abaixo do que seria tira 20 vezes {br(weight_fuel, 2)} = {br(fuel_p20, 2)} ponto do IPCA. "
        "O banco pesa 0 porque não segura preço de cesta nenhuma (critério 3).",
        "",
        f"CREDIT_WEIGHT (manter). O banco no P20 baixa {br(credit_p20, 2)} ponto o juro do "
        "crédito (exemplo: de 12% para 11% ao ano). É o mesmo tamanho do maior alívio "
        "que o combustível dá no IPCA, então as três alavancas têm poder parecido. "
        f"O preço pago é o corte de {br(cut_p20 * 100, 0)}% do lucro do banco no P20.",
        "",
        f"POLICY_REFERENCE_GROWTH = {br(reference_growth, 2)} (manter). Na estatal importada a "
        "política só mexe no preço pelo porte efetivo: cada mês com porte acima do original soma "
        f"{br(reference_growth * 100, 0)}% ao ano vezes o quanto o porte passa de 1 ao preço, e abaixo do original "
        f"subtrai. Exemplo: após {PREVIEW_YEARS} anos seguidos no Espremer o preço fica em "
        f"{br(squeeze_preview * 100, 1)}% do preço sem ordem (perde R$ {br(preview_loss_example, 1)} a cada R$ 100), "
        f"e no Reinvestir em {br(reinvest_preview * 100, 1)}%. Na fundada o mesmo mecanismo vive no "
        "valor justo, com o retorno médio no lugar da referência. O ganho do Tesouro soma o "
        f"dividendo a mais com a fatia de {br(FOUNDING_GOVERNMENT_SHARE * 100, 0)}% do governo no valor da empresa. "
        f"Um mandato dura {MANDATE_YEARS} anos: o Espremer passa a dar prejuízo ao Tesouro no ano "
        f"{squeeze_turn} e o Reinvestir passa a compensar no ano {reinvest_turn}, depois do "
        "mandato em que o dividendo foi colhido.",
        "",
        (
            f"GDP_PER_ROOT_BILLION (k) = {br(gdp.GDP_PER_ROOT_BILLION, 6)} (manter)."
            if k_keep
            else f"GDP_PER_ROOT_BILLION (k) = {br(k_value, 6)} (hoje {br(gdp.GDP_PER_ROOT_BILLION, 6)})."
        )
        + " k é o quanto cada raiz de bilhão de porte soma ao crescimento do PIB "
        f"por ano. Exemplo: uma estatal de R$ 100 bi soma raiz de 100 = 10 vezes k, "
        f"ou {br(push_today, 3)} pp ao ano com o k de hoje e {br(push_pick, 3)} pp com o recomendado. "
        "É a constante que decide o critério 6: sem empurrão (k = 0) fundar e vender "
        "deixa a dívida maior, porque o governo põe o capital inteiro e fica só com "
        f"{br(FOUNDING_GOVERNMENT_SHARE * 100, 0)}%; com o empurrão grande demais, o PIB maior derruba a "
        "dívida ÷ PIB e o ciclo vira dinheiro de graça. Média do Δ dívida ÷ PIB em pp, "
        "estatal média, venda ao valor justo (negativo é o governo saindo ganhando): "
        f"em 8 anos de posse {br(cycle_8(Decimal(1)), 2, sign=True)} com o k de hoje e "
        f"{br(cycle_8(k_pick), 2, sign=True)} com o recomendado; em 20 anos "
        f"{br(cycle_20(Decimal(1)), 2, sign=True)} e {br(cycle_20(k_pick), 2, sign=True)}. "
        f"No prazo de um mandato (4 anos) {br(figure(checks, 6, 'mean_4'), 2, sign=True)} pp com o k de hoje, "
        f"com Δ ≥ 0 em {hits_4} de {runs} sementes ({share_text(hits_4, runs)}). "
        f"Custo do recomendado no critério 1 (dez estatais em 10 anos): o PIB sobe "
        f"{br(figure(checks, 1, f'k_level_{k_pick}'), 2, sign=True)}% (contra "
        f"{br(figure(checks, 1, 'k_level_1'), 2, sign=True)}% hoje) e a dívida ÷ PIB muda "
        f"{br(figure(checks, 1, f'k_debt_{k_pick}'), 1, sign=True)} pp (contra "
        f"{br(figure(checks, 1, 'k_debt_1'), 1, sign=True)} pp hoje).",
        "",
        f"SIZE_STEP = {br(gdp.SIZE_STEP, 2)}, limites {br(gdp.MIN_SIZE_MULTIPLIER, 1)} a {br(gdp.MAX_SIZE_MULTIPLIER, 1)} (manter). A política de "
        f"dividendo muda o porte efetivo em {br(gdp.SIZE_STEP * 100, 0)}% por mês. Exemplo: após um "
        f"mandato ({months_mandate} meses) no Espremer o porte efetivo é {br(multiplier, 2)} do original, "
        f"e o piso chega em {months_to_floor} meses. Uma empresa de R$ 100 bi passa a "
        f"empurrar o PIB como uma de R$ {br(100 * multiplier, 0)} bi, ou {br(math.sqrt(float(multiplier)) * 100, 0)}% do "
        "empurrão original, já que o empurrão cresce com a raiz do porte. O mesmo porte decide o "
        "crescimento do valor da empresa: com porte 0,6, a empresa cresce 40% do retorno médio a menos "
        "por ano. O efeito no PIB é de décimos de ponto percentual (critério 5), então o passo "
        "não desequilibra nada.",
        "",
        f"FOUNDING_MONTHS = {gdp.FOUNDING_MONTHS} (manter). É o prazo em que o Tesouro paga o capital em "
        "parcelas mensais iguais, um ano de orçamento. Exemplo: uma estatal de R$ 100 bi "
        f"custa R$ {br(100 / gdp.FOUNDING_MONTHS, 1)} bi por mês. Com 6 meses a dívida ÷ PIB muda "
        f"{br(figure(checks, 1, 'months_debt_6'), 1, sign=True)} pp, com 12 "
        f"{br(figure(checks, 1, 'months_debt_12'), 1, sign=True)} pp e com 24 "
        f"{br(figure(checks, 1, 'months_debt_24'), 1, sign=True)} pp (critério 1): a diferença entre os prazos é "
        "pequena perto do efeito de k.",
        "",
        f"MEAN_RETURN_DISCOUNT = {br(discount, 2)} (hoje {br(fair_value.MEAN_RETURN_DISCOUNT, 2)}). "
        "É quanto o retorno médio anual do valor justo fica abaixo do juro real "
        f"(hoje {br(real * 100, 2)}% ao ano: SELIC descontada a inflação). O dono recebe a alta do valor "
        f"mais o dividendo, que paga {br(normal_payout * 100, 0)}% do lucro, então o retorno total "
        f"é cerca de {br(1 + normal_payout, 1)} vezes a média. Exemplo com R$ 100 bi: com o desconto "
        f"de hoje o valor sobe {br(mean_today * 100, 2)}% e o total é {br(total_today * 100, 2)}% ao ano, "
        f"acima dos {br(real * 100, 2)}% de um título sem risco; com {br(discount, 2)} o total é "
        f"{br(total_pick * 100, 2)}%, no nível do juro real. Quando o total passa do juro real, "
        "comprar estatal vira melhor do que a renda fixa sem risco extra nenhum, "
        "distorção que o desconto corrige.",
        "",
        f"ANNUAL_VOLATILITY = {br(volatility, 2)} (manter). Volatilidade é o tamanho típico do "
        "susto: em 2 de cada 3 anos o retorno fica a até 10 pontos percentuais da "
        f"média. O corte do retorno anual ({br(fair_value.MIN_ANNUAL_RETURN, 1)} a {br(fair_value.MAX_ANNUAL_RETURN, 1)}) só atua além de "
        f"{br(sigmas, 1)} desvios, ou seja, nunca na prática. Exemplo no critério 6 (média do Δ dívida ÷ PIB, "
        f"posse de 8 anos): {br(figure(checks, 6, 'variant_volatilidade 5%_8'), 2, sign=True)} pp com volatilidade 5%, "
        f"{br(figure(checks, 6, 'variant_constantes de hoje_8'), 2, sign=True)} pp com 10% e "
        f"{br(figure(checks, 6, 'variant_volatilidade 20%_8'), 2, sign=True)} pp com 20%: a volatilidade muda a "
        "dispersão entre as sementes bem mais do que a média, e 10% dá sorte e azar "
        "sem decidir o resultado.",
    ]
    return lines


def build_report(runs: int) -> str:
    checks = [
        check_founding(runs),
        check_hold_and_release(runs),
        check_bank(),
        check_cap(runs),
        check_policy(runs),
        check_privatization_cycle(runs),
        check_imported_default(),
    ]
    book_check = check_against_book()
    lines = [
        "# Calibração das estatais",
        "",
        f"Amostra: {runs} sementes por medida (a semente sorteia os retornos anuais "
        "do valor justo das fundadas). Economia sintética sem banco; as contas são as "
        "funções reais do backend.",
        "",
        "## Critérios de aceite",
        "",
        *acceptance_table(checks),
        "",
        f"Conferência do protótipo com o livro das estatais: {status(book_check.passed)} "
        f"({book_check.summary}).",
        "",
    ]
    for check in sorted(checks, key=lambda c: c.number):
        lines += [
            f"## {check.number}. {check.title}: {status(check.passed)}",
            "",
            *check.details,
            "",
        ]
    lines += ["## Conferência com o livro", "", *book_check.details, ""]
    lines += ["## Sugestão de constantes", "", *suggestions(checks, runs)]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--runs", type=int, default=200)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    # O relatório sai em UTF-8 também no terminal do Windows
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    # O passo da dívida do backend roda com a taxa mensal em ponto flutuante
    with overridden(budget, period_rate=fast_period_rate):
        report = build_report(args.runs)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
