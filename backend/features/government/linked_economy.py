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
)
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.tax_policy import DEFAULT_TAX_POLICY, TaxPolicy


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
    ):
        """
        `works_on` é o gasto a mais com obras no dia: as obras têm efeito próprio no
        crescimento e ficam fora do impulso. `monetary` traz a SELIC das reuniões do
        governo e a credibilidade, que pesam só na partida; a base é a história.
        """
        self._macro = macro
        self._monetary = monetary
        self._works_on = works_on
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
        )
        self._base = BudgetCourse(
            start, lambda _day: DEFAULT_TAX_POLICY, account, macro, stored=True
        )
        self.layer = EconomyLayer(simulation_id, start, spending, self, monetary)
        spending.use_on_change(self.layer.refresh)
        macro.use_government(
            spending.growth_points, self._impulse_on, self._crowding_on
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
        # O primário que o governo escolheu: sem o ciclo e sem as obras
        chosen = (game.revenue - game.cycle_revenue) - (
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
        return self.links_on(day).impulse

    def _crowding_on(self, day: date) -> Decimal:
        return self.links_on(day).crowding_out

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

    def base_budget(self) -> BudgetCourse:
        return self._base
