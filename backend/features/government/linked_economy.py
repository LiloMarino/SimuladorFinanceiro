"""
A economia interligada: o coordenador que fecha os meses da partida e da linha de base
e calcula as ligações de cada mês fechado, com a SELIC e a credibilidade que as
reuniões do governo fixaram. A ordem do fechamento de um mês é fixa:
crescimento e desemprego, orçamento da partida, orçamento da base e, por fim, as
ligações, que valem do mês seguinte em diante. Assim o fechamento de um mês lê séries
que só dependem de meses já fechados, e o resultado não depende de quem leu primeiro.
"""

import threading
from bisect import bisect_left
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.utils import last_day_of_month
from backend.features.economy.growth import MacroCourse
from backend.features.economy.layer import EconomyLayer
from backend.features.economy.links import (
    IMPULSE_MONTHS,
    NO_LINK,
    ZERO,
    LinkMonth,
    link_month,
)
from backend.features.economy.monetary import (
    LAG_MONTHS,
    Monetary,
    credibility_premium,
    rate_inflation_points,
)
from backend.features.government.budget import (
    AccountStart,
    BudgetCourse,
    Cycle,
    SpendingOn,
    StateReaisOn,
    no_state_dividends,
)
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy

# Um valor por dia: pontos de IPCA, pontos de juro ou fração ao ano
PointsOn = Callable[[date], Decimal]


def _no_points(_day: date) -> Decimal:
    return ZERO


@dataclass(frozen=True)
class StateFeed:
    """
    O que as estatais dão à economia em cada dia: ao orçamento, em reais (os dividendos
    que o Tesouro recebe, o gasto da fundação e o que a privatização rende no mês) e às
    ligações (o efeito no IPCA e no juro do crédito, em pontos, e o empurrão no PIB, em fração ao ano).
    """

    dividends_on: StateReaisOn = no_state_dividends
    spending_on: StateReaisOn = no_state_dividends
    assets_on: StateReaisOn = no_state_dividends
    inflation_on: PointsOn = _no_points
    credit_on: PointsOn = _no_points
    gdp_push_on: PointsOn = _no_points


NO_STATE_FEED = StateFeed()


class LinkedEconomy:
    """
    Dono dos cursos da partida e da linha de base e das ligações. Só ele fecha mês:
    quem lê crescimento, desemprego, orçamento ou prêmio passa antes por `close_until`.
    `links_on` só lê meses já fechados, então a camada das séries o chama de dentro de
    um fechamento sem esperar a trava.
    """

    def __init__(
        self,
        simulation_id: int,
        start: date,
        macro: MacroCourse,
        account: AccountStart,
        policy_on: Callable[[date], TaxPolicy],
        spending_on: SpendingOn,
        works_on: SpendingOn,
        spending: SpendingEconomy,
        monetary: Monetary,
        state_feed: StateFeed = NO_STATE_FEED,
    ):
        """
        `state_feed` é o que as estatais dão ao orçamento e às ligações em cada mês.
        `works_on` é o gasto a mais com obras no dia: as obras têm efeito próprio no
        crescimento e ficam fora do impulso. `monetary` traz a SELIC das reuniões do
        governo e a credibilidade, que pesam só na partida; a base é a história.
        """
        self._macro = macro
        self._policy_on = policy_on
        self._monetary = monetary
        self._works_on = works_on
        self._state = state_feed
        self._lock = threading.RLock()
        self._closed_through = start - timedelta(days=1)
        self._links: list[LinkMonth] = []
        self._ends: list[date] = []
        self._first: date | None = None
        self.budget = BudgetCourse(
            start,
            policy_on,
            account,
            macro,
            spending_on,
            self._cycle_on,
            self._credibility_premium_on,
            state_feed.dividends_on,
            state_spending_on=state_feed.spending_on,
            state_assets_on=state_feed.assets_on,
        )
        self._base = BudgetCourse(
            start, lambda _day: DEFAULT_TAX_POLICY, account, macro, stored=True
        )
        self.layer = EconomyLayer(simulation_id, start, spending, self, monetary)
        spending.use_on_change(self.layer.refresh)
        macro.use_government(
            spending.growth_points,
            self._impulse_on,
            self._crowding_on,
            self._payroll_on,
        )
        repository.economic.use_adjustment(simulation_id, self.layer)

    @property
    def macro(self) -> MacroCourse:
        return self._macro

    def close_until(self, day: date) -> None:
        """Fecha, em ordem, cada mês cujo último dia já chegou."""
        with self._lock:
            while (
                month_end := last_day_of_month(self._closed_through + timedelta(days=1))
            ) <= day:
                self._close(month_end)
                self._closed_through = month_end

    def _close(self, month_end: date) -> None:
        country = self._macro.latest(month_end)
        game = self.budget.latest(month_end)
        base = self._base.latest(month_end)
        # O primário que o governo escolheu: sem o ciclo, sem as obras e sem os dividendos
        # das estatais, que vêm do lucro delas e não de uma decisão fiscal
        chosen = (game.revenue - game.cycle_revenue - game.state_dividends) - (
            game.spending - game.insurance - self._works_on(month_end)
        )
        previous = self._links[-1] if self._links else NO_LINK
        # Antes da partida o primário é o da história: o desvio de 12 meses antes é zero
        year_ago = (
            self._links[-IMPULSE_MONTHS].primary_gap
            if len(self._links) >= IMPULSE_MONTHS
            else ZERO
        )
        # O juro real do mês entra na defasagem junto com os 11 anteriores; antes da partida o desvio é zero
        real_rate_gap = country.aim.real_rate - country.base_aim.real_rate
        gaps = [m.real_rate_gap for m in self._links[-(LAG_MONTHS - 1) :]]
        rate_points = rate_inflation_points(
            [*gaps, real_rate_gap], self._monetary.credibility_on(month_end)
        )
        # Cada imposto do país pesa pela alíquota em vigor contra a padrão; o consumo repassa
        # aos preços pela mudança em 12 meses
        policy = self._policy_on(month_end)
        consumption_gap = policy.consumption_rate - DEFAULT_TAX_POLICY.consumption_rate
        consumption_year_ago = (
            self._links[-IMPULSE_MONTHS].consumption_gap
            if len(self._links) >= IMPULSE_MONTHS
            else ZERO
        )
        # O repasse do câmbio conta a alta do dólar em 12 meses: parte do desvio de 12 meses antes
        dollar_year_ago = (
            self._links[-IMPULSE_MONTHS].dollar_gap
            if len(self._links) >= IMPULSE_MONTHS
            else 0.0
        )
        link = link_month(
            previous if self._links else None,
            month_end,
            unemployment_gap=country.unemployment - country.base_unemployment,
            premium_gap=game.premium - base.premium,
            growth_gap=country.growth - country.base_growth,
            primary_gap=chosen - base.primary,
            primary_gap_year_ago=year_ago,
            real_rate_gap=real_rate_gap,
            rate_points=rate_points,
            consumption_gap=consumption_gap,
            consumption_gap_year_ago=consumption_year_ago,
            corporate_gap=policy.corporate_rate - DEFAULT_TAX_POLICY.corporate_rate,
            payroll_gap=policy.payroll_rate - DEFAULT_TAX_POLICY.payroll_rate,
            dollar_gap_year_ago=dollar_year_ago,
            state_inflation_points=self._state.inflation_on(month_end),
            state_credit_points=self._state.credit_on(month_end),
            state_gdp_push=self._state.gdp_push_on(month_end),
        )
        # A lista das ligações cresce antes da dos dias: quem lê sem a trava acha as duas coerentes
        self._links.append(link)
        self._ends.append(month_end)
        if self._first is None and not link.is_zero:
            self._first = month_end + timedelta(days=1)
        if not link.same_effect(previous):
            self.layer.refresh_from(month_end + timedelta(days=1))

    # Leitura das ligações, sem a trava

    def first_day(self) -> date | None:
        return self._first

    def links_on(self, day: date) -> LinkMonth:
        """As ligações do último mês fechado antes de `day`."""
        index = bisect_left(self._ends, day)
        return self._links[index - 1] if index else NO_LINK

    def links_until(self, day: date) -> list[LinkMonth]:
        """As ligações dos meses fechados até `day`, do mais antigo ao mais novo."""
        return self._links[: bisect_left(self._ends, day + timedelta(days=1))]

    def _impulse_on(self, day: date) -> Decimal:
        """O impulso fiscal mais o empurrão permanente das estatais fundadas."""
        link = self.links_on(day)
        return link.impulse + link.state_gdp_push

    def _crowding_on(self, day: date) -> Decimal:
        return self.links_on(day).crowding_out

    def _payroll_on(self, day: date) -> Decimal:
        return self.links_on(day).payroll_jobs

    def _credibility_premium_on(self, day: date) -> Decimal:
        return credibility_premium(self._monetary.credibility_on(day))

    def _cycle_on(self, day: date) -> Cycle:
        link = self.links_on(day)
        return Cycle(revenue=link.cycle_revenue, insurance=link.insurance)

    # Leitura dos cursos, depois de fechar até o dia

    def premium_on(self, day: date) -> Decimal:
        """O prêmio de risco da dívida da partida no dia."""
        self.close_until(day)
        return self.budget.premium_on(day)

    def premium_gap_on(self, day: date) -> Decimal:
        """O prêmio acima da história que vale no dia, que o crédito soma à taxa."""
        self.close_until(day)
        return self.links_on(day).premium_gap

    def credit_premium_on(self, day: date) -> Decimal:
        """O que o crédito soma à taxa no dia: o prêmio acima da história e o juro que o banco estatal tira."""
        self.close_until(day)
        link = self.links_on(day)
        return link.premium_gap + link.credit_premium

    def base_budget(self) -> BudgetCourse:
        return self._base
