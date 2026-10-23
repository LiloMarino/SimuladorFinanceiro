from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from backend.core import repository
from backend.core.dto.government import (
    CurrentTaxDTO,
    GovernmentActionDTO,
    GovernmentImpactDTO,
    GovernmentPreviewDTO,
    GovernmentStateDTO,
    GovernmentViewDTO,
    PartyRankingDTO,
    TermDTO,
)
from backend.core.enum import FixedIncomeType, IndicatorSeries
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import annual_index_rate, raw_annual_index_rate
from backend.core.runtime.event_manager import EventManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import income_tax_brackets, income_tax_rate
from backend.features.government.economy import (
    active_policies,
    company_effect,
    macro_effect,
    scenario_profile,
    state_on,
    tax_value,
)
from backend.features.government.politics import (
    action,
    advance_day,
    approval_factors,
    election_year,
    ensure_ai,
    phase,
    propose,
    require,
)
from backend.features.variable_income.price_impact import PriceImpact, _scale

if TYPE_CHECKING:
    from backend.features.simulation.simulation import Simulation


class GovernmentPriceImpact(PriceImpact):
    def refresh(self, today: date) -> None:
        self._today = today
        super().refresh(today)

    def apply(self, candle):
        factor = company_effect(
            state_on(self.simulation_id, self._today), candle.ticker, self._today
        )[0]
        return _scale(super().apply(candle), factor)

    def factors_on(self, ticker: str, days: list[date]) -> dict[date, float]:
        return {
            day: factor
            * company_effect(state_on(self.simulation_id, day), ticker, day)[0]
            for day, factor in super().factors_on(ticker, days).items()
        }


class GovernmentRuntime:
    def __init__(self, simulation: Simulation, seed: int):
        self.sim = simulation
        self.seed = seed
        stored = repository.government.states(simulation.settings.id)
        if stored:
            self.state = stored[-1]
        else:
            rules = simulation.settings.government.model_copy(deep=True)
            if not rules.companies:
                classifications = repository.stock.get_classification()
                rules.companies = [
                    scenario_profile(
                        c.ticker,
                        classifications[c.ticker].sector
                        if c.ticker in classifications
                        else None,
                        classifications[c.ticker].segment
                        if c.ticker in classifications
                        else None,
                    )
                    for c in repository.stock.get_stocks_by_date(
                        simulation.settings.start_date
                    )
                ]
            self.state = GovernmentStateDTO(
                rules=rules,
                initialized_on=simulation.settings.start_date,
                processed_on=simulation.settings.start_date - timedelta(days=1),
                treasury=rules.initial_treasury,
            )
            ensure_ai(self.state)
        self.cursor = self.state.processed_on
        self._view_cache: tuple[tuple[date, int, int], GovernmentViewDTO] | None = None

    def users(self):
        return repository.simulation_player.participants(self.sim.settings.id)

    def _save(
        self,
        state: GovernmentStateDTO,
        kind: str,
        actor: int | None = None,
        debits: dict[int, Decimal] | None = None,
        request_key: str | None = None,
    ):
        state.revision = self.state.revision + 1
        repository.government.append(
            self.sim.settings.id, state, kind, actor, debits or {}, request_key
        )
        self.state = state
        for user in self.users():
            if user.id in (debits or {}):
                self.sim._engine._cash.pop(user.client_id, None)

    def advance(self, until: date):
        users = self.users()
        balances: dict[int, Decimal] | None = None
        day = self.cursor + timedelta(days=1)
        while day <= until:
            last = calendar.monthrange(day.year, day.month)[1]
            due = (
                day.day in (1, last)
                or (day.month == 10 and day.day in (7, 28))
                or any(p.effective_on == day for p in self.state.policies)
                or (
                    self.state.rules.manual_selic
                    and self.state.term
                    and self.state.term.president < 0
                    and not self.state.term.neutral
                    and (
                        not self.state.selic_decisions
                        or day == self.state.selic_decisions[-1].on + timedelta(days=45)
                    )
                )
            )
            if due or self.state.revision == 0:
                balances = balances or {
                    u.id: self.sim.get_cash(u.client_id) for u in users
                }
                state = self.state.model_copy(deep=True)
                if day.day == last:
                    collected = repository.government.collected_taxes(
                        self.sim.settings.id, day
                    )
                    state.treasury += max(Decimal(0), collected - state.collected_tax)
                    state.collected_tax = collected
                debits = advance_day(
                    state,
                    day,
                    self.seed,
                    balances,
                    self.inflation(day),
                    self.market_return(day),
                    float(raw_annual_index_rate(IndicatorSeries.SELIC, day)),
                )
                self._save(state, "calendar", debits=debits)
                for key, amount in debits.items():
                    balances[key] -= amount
            day += timedelta(days=1)
        self.cursor = until
        # Ordens anteriores à posse também são bloqueadas, antes do matching do pregão.
        if self.state.term and self.state.term.president > 0:
            president = next(
                (u for u in users if u.id == self.state.term.president), None
            )
            if president:
                for order in list(
                    self.sim._engine.matching_engine.order_book._orders_by_id.values()
                ):
                    if order.client_id == president.client_id:
                        self.sim._engine.matching_engine.cancel(
                            order_id=order.id, client_id=president.client_id
                        )

    def inflation(self, on: date) -> float:
        return (
            float(raw_annual_index_rate(IndicatorSeries.IPCA, on))
            + macro_effect(self.state, on).inflation
        )

    def close_day(self, on: date):
        """Inclui também DARFs e retenções recebidos no último pregão do mês."""
        if next_business_day(on).month == on.month:
            return
        collected = repository.government.collected_taxes(self.sim.settings.id, on)
        if collected > self.state.collected_tax:
            state = self.state.model_copy(deep=True)
            state.processed_on = on
            state.treasury += collected - state.collected_tax
            state.collected_tax = collected
            self._save(state, "treasury")

    def market_return(self, on: date) -> float:
        history = repository.economic.get_history(IndicatorSeries.IBOV)
        current, previous = (
            history.last_known(on),
            history.last_known(on - timedelta(days=365)),
        )
        if current is None or not previous:
            return 0
        factor = max(0.1, 1 - 2.9 * macro_effect(self.state, on).selic)
        before = state_on(self.sim.settings.id, on - timedelta(days=365))
        previous_factor = max(
            0.1, 1 - 2.9 * macro_effect(before, on - timedelta(days=365)).selic
        )
        return float(current / previous) * factor / previous_factor - 1

    def frozen(self, client_id: UUID) -> bool:
        return bool(
            self.state.term
            and self.state.term.president == UserManager.get_user_id(client_id)
        )

    def assert_trading(self, client_id: UUID):
        if self.frozen(client_id):
            raise ConflictError(
                "A carteira do presidente está congelada durante o mandato. Ordens abertas são canceladas na posse; vencimentos e rendimentos continuam automáticos."
            )

    def command(
        self, client_id: UUID, command: GovernmentActionDTO
    ) -> GovernmentViewDTO:
        request_key = (
            f"{UserManager.get_user_id(client_id)}:{command.request_id}"
            if command.request_id
            else None
        )
        if request_key and repository.government.has_request(
            self.sim.settings.id, request_key
        ):
            return self.view(client_id)
        users = self.users()
        user = next((u for u in users if u.client_id == client_id), None)
        require(
            user is not None,
            "Somente participantes da partida podem atuar na política.",
        )
        assert user is not None
        EventManager.flush()
        state = self.state.model_copy(deep=True)
        state.processed_on = self.sim.get_current_date()
        debits = action(
            state,
            user.id,
            command,
            self.sim.get_cash(client_id),
            {u.id for u in users},
            float(raw_annual_index_rate(IndicatorSeries.SELIC, state.processed_on)),
            self.inflation(state.processed_on),
        )
        self._save(state, command.action, user.id, debits, request_key)
        if command.action == "selic":
            # A decisão vale no dia atual: cotações e book precisam usar o mesmo
            # nível mesmo quando nenhum tick chega porque a partida está pausada.
            self.sim._price_impact.refresh(state.processed_on)
            self.sim._engine.update_market_data(
                self.sim.get_stocks(), replace_current=True
            )
            EventManager.flush()
        # Campanha altera o caixa; atualizar snapshot preserva o valor do ranking pausado.
        if debits or command.action == "selic":
            entries = self.sim._create_daily_snapshots(users, False)
            self.sim._last_snapshots = {e.snapshot.user_id: e.snapshot for e in entries}
        return self.view(client_id)

    def view(self, client_id: UUID) -> GovernmentViewDTO:
        today = self.sim.get_current_date()
        uid = UserManager.get_user_id(client_id)
        key = (today, self.state.revision, id(self.sim._last_snapshots))
        if self._view_cache and self._view_cache[0] == key:
            return self._personalize(self._view_cache[1], uid)
        users = self.users()
        state = self.state
        quotes = {c.ticker: c for c in repository.stock.get_stocks_by_date(today)}
        profiles = {p.ticker: p for p in state.rules.companies}
        impacts = []
        for ticker, quote in quotes.items():
            factor, product, monetary = company_effect(state, ticker, today)
            profile = profiles.get(ticker)
            baseline = round(
                quote.close * self.sim._price_impact._factors.get(ticker, 1), 2
            )
            impacts.append(
                GovernmentImpactDTO(
                    ticker=ticker,
                    sector=profile.sector if profile else None,
                    source=profile.source if profile else "Sem perfil empresarial",
                    covered=bool(profile and profile.exposures),
                    baseline_price=baseline,
                    effective_price=round(baseline * factor, 2),
                    impact=factor - 1,
                    product_effect=product,
                    monetary_effect=monetary,
                    exposures=profile.exposures if profile else [],
                )
            )
        rankings = []
        for p in state.parties:
            if p.is_ai or not p.members:
                continue
            members = [u for u in users if u.id in p.members]
            rankings.append(
                PartyRankingDTO(
                    party_id=p.id,
                    name=p.name,
                    members=[u.nickname for u in members],
                    networth=sum(
                        (
                            self.sim._last_snapshots[u.id].total_networth
                            for u in members
                            if u.id in self.sim._last_snapshots
                        ),
                        Decimal(0),
                    ),
                )
            )
        rankings.sort(key=lambda p: p.networth, reverse=True)
        president = next(
            (u for u in users if state.term and u.id == state.term.president), None
        )
        portfolio = (
            self.sim._engine.get_positions(president.client_id) if president else {}
        )
        last_selic = state.selic_decisions[-1] if state.selic_decisions else None
        macro = macro_effect(state, today)
        taxes = [
            CurrentTaxDTO(
                label=label,
                value=tax_value(state, today, kind, Decimal(default)),
                unit="money" if kind == "STOCK_EXEMPTION" else "percent",
            )
            for kind, label, default in [
                ("COMMON_TAX", "Renda variável · operação comum", "0.15"),
                ("DAY_TRADE_TAX", "Renda variável · day trade", "0.20"),
                ("FII_TAX", "FIIs · venda com lucro", "0.20"),
                ("STOCK_EXEMPTION", "Isenção mensal de vendas de ações", "20000"),
            ]
        ]
        taxes.append(
            CurrentTaxDTO(
                label="LCI e LCA", value=income_tax_rate(FixedIncomeType.LCI, 0, today)
            )
        )
        taxes.extend(
            CurrentTaxDTO(
                label=f"Renda fixa · até {b.max_days} dias"
                if b.max_days
                else "Renda fixa · acima de 720 dias",
                value=b.rate,
            )
            for b in income_tax_brackets(today)
        )
        taxes.extend(
            CurrentTaxDTO(
                label=f"{'Ajuste de IR' if p.kind == 'SECTOR_TAX' else 'Tarifa'} · {p.target}",
                value=p.value,
            )
            for p in active_policies(state, today)
            if p.kind in ("SECTOR_TAX", "PRODUCT_TARIFF")
        )
        view = GovernmentViewDTO(
            state=state,
            today=today,
            election_year=election_year(state, today),
            phase=phase(state, today),
            can_govern=bool(
                state.term and not state.term.neutral and state.term.president == uid
            ),
            trading_frozen=self.frozen(client_id),
            users={str(u.id): u.nickname for u in users},
            my_id=uid,
            impacts=impacts,
            party_ranking=rankings,
            president_portfolio={ticker: p.size for ticker, p in portfolio.items()},
            president_finances=self.sim.get_portfolio(president.client_id)
            if president
            else None,
            current_selic=float(annual_index_rate(IndicatorSeries.SELIC, today)),
            current_inflation=self.inflation(today),
            inflation_delta=macro.inflation,
            selic_delta=macro.selic,
            next_selic_meeting=last_selic.on + timedelta(days=45)
            if last_selic
            else (state.term.start if state.term else None),
            approval_factors=approval_factors(
                state, self.inflation(today), self.market_return(today)
            ),
            current_taxes=taxes,
        )
        self._view_cache = key, view
        return self._personalize(view, uid)

    def _personalize(self, view: GovernmentViewDTO, uid: int) -> GovernmentViewDTO:
        term = self.state.term
        return view.model_copy(
            update={
                "my_id": uid,
                "can_govern": bool(term and not term.neutral and term.president == uid),
                "trading_frozen": bool(term and term.president == uid),
            }
        )

    def preview(
        self, client_id: UUID, command: GovernmentActionDTO
    ) -> GovernmentPreviewDTO:
        today = self.sim.get_current_date()
        state = self.state.model_copy(deep=True)
        state.processed_on = today
        # A fila operacional não limita comparações públicas de hipóteses.
        state.policies = [p for p in state.policies if p.status == "approved"]
        if state.term is None or state.term.neutral:
            state.term = TermDTO(
                party_id=0, president=0, start=today, end=today + timedelta(days=1461)
            )
        propose(state, state.term.president, command)
        hypothetical = state.policies[-1]
        hypothetical.status, hypothetical.effective_on = "approved", today
        horizon = 30 if hypothetical.kind == "PUBLIC_SPENDING" else 0
        scenario_on = today + timedelta(days=horizon)
        impacts = []
        for current in self.view(client_id).impacts:
            factor, product, monetary = company_effect(
                state, current.ticker, scenario_on
            )
            impacts.append(
                current.model_copy(
                    update={
                        "effective_price": round(current.baseline_price * factor, 2),
                        "impact": factor - 1,
                        "product_effect": product,
                        "monetary_effect": monetary,
                    }
                )
            )
        month_end = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        return GovernmentPreviewDTO(
            as_of=today,
            horizon_days=horizon,
            earliest_effective_on=month_end + timedelta(days=90),
            inflation_delta=macro_effect(state, today + timedelta(days=30)).inflation,
            impacts=impacts,
            assumptions=f"Hipótese de aprovação no próximo fechamento mensal. Efeito {horizon} dia(s) após a vigência, mantendo a referência de preços de hoje. IR altera a cobrança sobre ganhos; tarifa afeta os produtos cobertos. Perfis empresariais são hipóteses do cenário. Prévia pública: não grava medidas nem movimenta dinheiro.",
        )
