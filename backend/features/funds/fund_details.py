import math
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from backend.core import repository
from backend.core.dto.events.cashflow import CashflowEventDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import (
    FundComanagerViewDTO,
    FundCompositionDTO,
    FundDetailsDTO,
    FundDirectedIssuanceViewDTO,
    FundDistributionDTO,
    FundFeesDTO,
    FundHolderDTO,
    FundHolderKind,
    FundHoldingClass,
    FundIssuanceRulesDTO,
    FundIssuanceStatusDTO,
    FundMonthlyReportDTO,
    FundMovementDTO,
    FundOfferBuyerDTO,
    FundOfferSaleDTO,
    FundPositionDTO,
    FundReportDTO,
    FundSeriesPointDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import FixedIncomeType, FundComanagerStatus
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.fund_reference import PREMIUM_LIMIT
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import last_month_turn, next_month_turn, ratio
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.fixed_broker import load_fixed_assets
from backend.features.fixed_income.quotes import FixedIncomeQuotes
from backend.features.funds import fund_ledger
from backend.features.funds.distribution import drained_since, paid_since
from backend.features.funds.fees import management_fee, performance_charge
from backend.features.funds.fund_book import (
    LEFTOVER_SESSIONS,
    PREFERENCE_SESSIONS,
    Fund,
    FundBook,
    cdi_growth,
)
from backend.features.funds.fund_comanagers import expires_on, manager_share
from backend.features.funds.fund_directed import expires_on as directed_expires_on
from backend.features.funds.fund_estimate import IssuanceEstimator
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.strategy.fair_value_trading import OPINION_RANGE
from backend.features.variable_income.broker import replay_positions

# Pregões lidos da série de fechamentos: de sobra para os últimos 12 meses
SERIES_LIMIT = 500

MAKER_NICKNAME = "Mercado"
BOTS_NICKNAME = "Bots"

_CLASSES: tuple[FundHoldingClass, ...] = (
    "cash",
    "stocks",
    "fixed_income",
    "treasury",
)

# (ticker, nome, classe, quantidade, valor em reais) de uma posição, antes das frações
type Line = tuple[str | None, str, FundHoldingClass, Decimal | None, Decimal]


def control_quotas(total: Decimal) -> Decimal:
    """As cotas que dão o controle: mais da metade das em circulação."""
    return Decimal(math.floor(total / 2) + 1)


def positions_of(lines: Iterable[Line]) -> list[FundPositionDTO]:
    """As linhas com a fração do patrimônio; o caixa vem primeiro e o resto do maior valor ao menor."""
    lines = list(lines)
    total = sum((line[4] for line in lines), Decimal(0))
    ordered = sorted(lines, key=lambda line: (line[2] != "cash", -line[4]))
    return [
        FundPositionDTO(
            ticker=ticker,
            name=name,
            asset_class=asset_class,
            quantity=quantity,
            value=value,
            fraction=ratio(value, total),
        )
        for ticker, name, asset_class, quantity, value in ordered
    ]


def composition_of(lines: Iterable[Line]) -> list[FundCompositionDTO]:
    """O patrimônio somado por classe; as quatro classes saem sempre, na mesma ordem."""
    lines = list(lines)
    total = sum((line[4] for line in lines), Decimal(0))
    by_class: dict[FundHoldingClass, Decimal] = defaultdict(Decimal)
    for _, _, asset_class, _, value in lines:
        by_class[asset_class] += value
    return [
        FundCompositionDTO(
            asset_class=asset_class,
            value=by_class[asset_class],
            fraction=ratio(by_class[asset_class], total),
        )
        for asset_class in _CLASSES
    ]


class FundDetailsBuilder:
    """A página da gestora: monta o detalhe que uma pessoa da sala vê, pelo que o motor guarda
    agora e pelo livro de eventos.

    Quem consulta vê a carteira viva só se for o gestor; a sala toda vê o relatório mensal, as
    taxas, os movimentos e quem tem as cotas.
    """

    def __init__(
        self,
        book: FundBook,
        engine: SimulationEngine,
        simulation_id: int,
        colors: Callable[[], dict[int, str]],
        estimator: IssuanceEstimator,
    ) -> None:
        self._book = book
        self._engine = engine
        self._simulation_id = simulation_id
        self._colors = colors
        self._estimator = estimator

    def build(self, fund: Fund, viewer: UserDTO) -> FundDetailsDTO:
        engine = self._engine
        book = self._book
        terms = fund.terms
        account = fund.account
        today = engine.current_date
        users = book.participants()
        summary = book.summary(fund, {user.id: user.nickname for user in users})
        is_manager = viewer.id == terms.manager_user_id
        operators = book.operators(fund)
        is_operator = viewer.id in operators
        live = self._live_lines(fund)

        holders = self._holders(fund, users)
        manager_quotas = next(
            (
                holder.quotas
                for holder in holders
                if holder.user_id == terms.manager_user_id
            ),
            Decimal(0),
        )
        control = control_quotas(account.quotas)

        cash_events = repository.event.get_cashflow_events(
            self._simulation_id, terms.portfolio_id
        )
        fund_equity = repository.fund.portfolio_equity_events(
            self._simulation_id, terms.portfolio_id
        )
        trades = repository.fund.quota_trades(self._simulation_id, terms.stock_id)

        series = self._series(fund, today)
        return_12m, return_since, cdi_12m = self._returns(
            series, summary.nav, terms.listed_on, today
        )
        offer = self._offer(fund, users)
        manager = next(
            (user for user in users if user.id == terms.manager_user_id), None
        )
        manager_portfolio = (
            UserManager.get_portfolio_id(manager.client_id) if manager else None
        )
        my_quotas, my_value, my_return = self._mine(fund, viewer)

        return FundDetailsDTO(
            **summary.model_dump(),
            holders=holders,
            control_quotas=control,
            sellable_keeping_control=(
                max(Decimal(0), manager_quotas - control) if is_manager else None
            ),
            composition=composition_of(live),
            return_12m=return_12m,
            return_since=return_since,
            cdi_12m=cdi_12m,
            series=series,
            last_report=self._report(fund, today, cash_events, fund_equity),
            fees=self._fees(fund, summary.nav, today, cash_events),
            distribution=book.distribution_plan(fund),
            distributions=list(reversed(fund.distributions)),
            total_return_12m=self._total_return(
                series, summary.nav, fund.distributions
            ),
            movements=fund_ledger.movements(
                cash_events=cash_events,
                contributed_stocks=fund_equity,
                manager_trades=[
                    trade for trade in trades if trade.portfolio_id == manager_portfolio
                ],
                offer=offer.facts,
                issuances=repository.fund.issuances(terms.id),
                buybacks=repository.fund.buybacks(terms.id),
                comanager_events=repository.fund_comanager.events(terms.id),
                directed_issuances=repository.fund_directed_issuance.settled_of_fund(
                    terms.id
                ),
                nicknames={user.id: user.nickname for user in users},
                today=today,
            ),
            offer_sold=offer.facts.totals.sold if offer.facts else None,
            offer_raised=offer.facts.totals.raised if offer.facts else None,
            offer_buyers=offer.buyers,
            offer_buyers_count=offer.buyers_count,
            issuance=self._issuance(fund, viewer, today),
            issuance_rules=FundIssuanceRulesDTO(
                preference_sessions=PREFERENCE_SESSIONS,
                leftover_sessions=LEFTOVER_SESSIONS,
                bot_premium_limit=PREMIUM_LIMIT,
                bot_opinion_range=OPINION_RANGE,
            ),
            buyback=book.buyback_of(fund),
            assembly=book.assembly_panel(
                fund, viewer, {user.id: user.nickname for user in users}, self._colors()
            ),
            positions=positions_of(live) if is_operator else None,
            comanagers=self._comanagers(fund, users),
            manager_share=manager_share(fund),
            my_role="manager"
            if is_manager
            else "comanager"
            if is_operator
            else "viewer",
            my_share=self._my_share(fund, viewer),
            my_quotas=my_quotas,
            my_value=my_value,
            my_return=my_return,
            directed_issuance=self._directed_issuance(fund, viewer, users),
        )

    # =========================
    # Co-gestores
    # =========================

    def _comanagers(
        self, fund: Fund, users: list[UserDTO]
    ) -> list[FundComanagerViewDTO]:
        """Os co-gestores ativos e os convites pendentes, com apelido e cor."""
        names = {user.id: user.nickname for user in users}
        colors = self._colors()
        return [
            FundComanagerViewDTO(
                **comanager.model_dump(),
                nickname=names.get(comanager.user_id, "?"),
                color=colors.get(comanager.user_id),
                expires_on=expires_on(comanager)
                if comanager.status is FundComanagerStatus.INVITED
                else None,
            )
            for comanager in fund.comanagers
        ]

    def _directed_issuance(
        self, fund: Fund, viewer: UserDTO, users: list[UserDTO]
    ) -> FundDirectedIssuanceViewDTO | None:
        """A oferta de cotas novas que espera resposta, para o principal e para o comprador."""
        offer = fund.directed
        if offer is None or viewer.id not in (
            fund.terms.manager_user_id,
            offer.buyer_user_id,
        ):
            return None
        names = {user.id: user.nickname for user in users}
        return FundDirectedIssuanceViewDTO(
            **offer.model_dump(),
            buyer_nickname=names.get(offer.buyer_user_id, "?"),
            expires_on=directed_expires_on(offer),
        )

    def _my_share(self, fund: Fund, viewer: UserDTO) -> Decimal | None:
        """A parte das taxas em vigor de quem consulta; nula para quem não gere a gestora."""
        if viewer.id == fund.terms.manager_user_id:
            return manager_share(fund)
        comanager = next(
            (c for c in fund.comanagers if c.user_id == viewer.id),
            None,
        )
        if comanager is None or comanager.status is not FundComanagerStatus.ACTIVE:
            return None
        return comanager.share

    # =========================
    # Quem tem as cotas
    # =========================

    def _holders(self, fund: Fund, users: list[UserDTO]) -> list[FundHolderDTO]:
        """Jogadores, bots e o formador de mercado com cotas, do maior para o menor."""
        total = fund.account.quotas
        colors = self._colors()
        holders: list[FundHolderDTO] = []
        for user in users:
            position = self._engine.broker.get_positions(user.client_id).get(
                fund.ticker
            )
            if position is None or position.size <= 0:
                continue
            holders.append(
                FundHolderDTO(
                    kind="bot" if user.is_bot else "player",
                    user_id=user.id,
                    nickname=user.nickname,
                    color=colors.get(user.id),
                    quotas=position.size,
                    share=ratio(position.size, total),
                )
            )
        maker = fund.account.maker_quotas
        if maker > 0:
            holders.append(
                FundHolderDTO(
                    kind="maker",
                    user_id=None,
                    nickname=MAKER_NICKNAME,
                    color=None,
                    quotas=maker,
                    share=ratio(maker, total),
                )
            )
        return sorted(holders, key=lambda holder: holder.quotas, reverse=True)

    def _mine(
        self, fund: Fund, viewer: UserDTO
    ) -> tuple[Decimal, Decimal, Decimal | None]:
        """As cotas de quem consulta, o valor ao preço de ranking e o retorno sobre o custo médio."""
        position = self._engine.broker.get_positions(viewer.client_id).get(fund.ticker)
        if position is None or position.size <= 0:
            return Decimal(0), Decimal(0), None
        price = self._engine.get_current_price(position)
        value = price * position.size
        if position.total_cost <= 0:
            return position.size, value, None
        return position.size, value, value / position.total_cost - 1

    # =========================
    # Carteira
    # =========================

    def _live_lines(self, fund: Fund) -> list[Line]:
        """O caixa e cada posição da gestora, pelo valor de hoje."""
        engine = self._engine
        client = fund.account.client_id
        lines: list[Line] = [(None, "Caixa", "cash", None, engine.get_cash(client))]
        lines.extend(
            (
                position.ticker,
                engine.stocks[position.ticker].name,
                "stocks",
                position.size,
                engine.get_current_price(position) * position.size,
            )
            for position in engine.broker.get_positions(client).values()
            if position.size > 0
        )
        quotes = engine.fixed_quotes()
        lines.extend(
            self._fixed_line(held, engine.current_date, quotes)
            for held in engine.fixed_broker.get_fixed_positions(client).values()
        )
        return lines

    @staticmethod
    def _fixed_line(
        held: FixedIncomePosition, day: date, quotes: FixedIncomeQuotes
    ) -> Line:
        treasury = held.asset.investment_type is FixedIncomeType.TESOURO_DIRETO
        return (
            None,
            held.asset.name,
            "treasury" if treasury else "fixed_income",
            None,
            held.market_value(day, quotes),
        )

    def _report(
        self,
        fund: Fund,
        today: date,
        cash_events: list[CashflowEventDTO],
        equity_events: list[EquityEventDTO],
    ) -> FundReportDTO | None:
        """As posições no último pregão do mês fechado, valorizadas aos preços daquele dia.

        O relatório existe depois da primeira virada de mês seguinte à oferta e fica o mesmo
        até a virada seguinte.
        """
        listed_on = fund.terms.listed_on
        if listed_on is None:
            return None
        turn = last_month_turn(today)
        if turn <= listed_on:
            return None
        if fund.report is not None and fund.report[0] == turn:
            return fund.report[1]
        report = self._report_at(fund, turn, cash_events, equity_events)
        fund.report = (turn, report)
        return report

    def _report_at(
        self,
        fund: Fund,
        turn: date,
        cash_events: list[CashflowEventDTO],
        equity_events: list[EquityEventDTO],
    ) -> FundReportDTO:
        """As posições da gestora no último pregão antes da virada `turn`, a preços daquele dia."""
        engine = self._engine
        close = fund_ledger.last_business_day_before(turn)
        client = fund.account.client_id
        cash = sum(
            (
                event.amount * event.event_type.sign
                for event in cash_events
                if event.event_date < turn
            ),
            Decimal(0),
        )
        lines: list[Line] = [(None, "Caixa", "cash", None, cash)]
        closes = repository.stock.get_closes_on(close, self._simulation_id)
        held = replay_positions(e for e in equity_events if e.event_date < turn)
        for ticker, position in held.items():
            last = closes.get(ticker)
            price = Decimal(str(last)) if last is not None else position.avg_price
            lines.append(
                (
                    ticker,
                    engine.stocks[ticker].name,
                    "stocks",
                    position.size,
                    price * position.size,
                )
            )
        quotes = FixedIncomeQuotes(
            engine.risk_premium_on(close.replace(day=1)), engine.dollar_on(close)
        )
        lines.extend(
            self._fixed_line(position, close, quotes)
            for position in load_fixed_assets(
                self._simulation_id, client, close
            ).values()
        )

        # A taxa a pagar do fechamento daquele pregão, gravada junto do PL do dia
        closed = repository.fund.days(fund.terms.id, turn, 1)
        report = FundReportDTO(
            day=close,
            positions=positions_of(lines),
            fee_payable=closed[-1].fee_payable
            if closed and closed[-1].day == close
            else Decimal(0),
        )
        return report

    # =========================
    # Relatório de um mês
    # =========================

    @staticmethod
    def report_months(fund: Fund, today: date) -> list[date]:
        """Os meses com relatório publicado, do mais antigo ao mais novo: cada um sai na virada seguinte."""
        listed_on = fund.terms.listed_on
        if listed_on is None:
            return []
        last = last_month_turn(today)
        months: list[date] = []
        month = listed_on.replace(day=1)
        while (turn := next_month_turn(month)) <= last:
            if turn > listed_on:
                months.append(month)
            month = (month + timedelta(days=32)).replace(day=1)
        return months

    def monthly_report(self, fund: Fund, month: date) -> FundMonthlyReportDTO:
        """O relatório de `month` (o primeiro dia do mês): posições, o mês em números e as operações."""
        terms = fund.terms
        months = self.report_months(fund, self._engine.current_date)
        if month not in months:
            raise NotFoundError("Este mês ainda não tem relatório")
        turn = next_month_turn(month)
        cash_events = repository.event.get_cashflow_events(
            self._simulation_id, terms.portfolio_id
        )
        equity_events = repository.fund.portfolio_equity_events(
            self._simulation_id, terms.portfolio_id
        )
        report = self._report_at(fund, turn, cash_events, equity_events)
        # Os fechamentos do mês, com o último do mês anterior para abrir a conta
        closes = repository.fund.days(terms.id, turn, 40)
        in_month = [day for day in closes if day.day >= month]
        before = [day for day in closes if day.day < month]
        if not in_month:
            raise NotFoundError("Este mês ainda não tem relatório")
        start_nav = before[-1].nav if before else terms.offer_price or in_month[0].nav
        start_day = before[-1].day if before else terms.listed_on or month
        end = in_month[-1]
        management, performance = fund_ledger.fees_paid_between(
            cash_events, month, turn
        )
        movements = fund_ledger.movements(
            cash_events=cash_events,
            contributed_stocks=equity_events,
            manager_trades=[],
            offer=None,
            issuances=repository.fund.issuances(terms.id),
            buybacks=repository.fund.buybacks(terms.id),
            comanager_events=repository.fund_comanager.events(terms.id),
            directed_issuances=repository.fund_directed_issuance.settled_of_fund(
                terms.id
            ),
            nicknames={user.id: user.nickname for user in self._book.participants()},
            asset_trades=equity_events,
            limit=None,
            today=self._engine.current_date,
        )
        operations: list[FundMovementDTO] = [
            movement
            for movement in reversed(movements)
            if month <= movement.day < turn
            and movement.type
            not in ("management_fee", "performance_fee", "report_published")
        ]
        return FundMonthlyReportDTO(
            month=month,
            months=months,
            report=report,
            loan_debt=end.loan_debt,
            nav_start=start_nav,
            nav_end=end.nav,
            cdi_return=cdi_growth(start_day, end.day) - 1,
            distribution=next(
                (d for d in fund.distributions if d.data_com.replace(day=1) == month),
                None,
            ),
            management_fee_paid=management,
            performance_fee_paid=performance,
            operations=operations,
        )

    # =========================
    # Desempenho
    # =========================

    def _series(self, fund: Fund, today: date) -> list[FundSeriesPointDTO]:
        """O fechamento, o PL por cota e o preço de ranking de cada pregão dos últimos 12 meses."""
        terms = fund.terms
        start = fund_ledger.one_year_before(today)
        days = [
            day
            for day in repository.fund.days(
                terms.id, today + timedelta(days=1), SERIES_LIMIT
            )
            if day.day >= start
        ]
        # A série abre no dia da oferta, ao preço dela; o primeiro fechamento gravado é o do dia seguinte
        opening = (
            [FundSeriesPointDTO(day=terms.listed_on, close=None, nav=terms.offer_price)]
            if terms.listed_on is not None
            and terms.offer_price is not None
            and terms.listed_on >= start
            else []
        )
        if not days:
            return opening
        closes = repository.stock.get_closes_between(
            [fund.ticker], start, today, self._simulation_id
        )[fund.ticker]
        return [
            *opening,
            *(
                FundSeriesPointDTO(
                    day=day.day,
                    close=Decimal(str(closes[day.day])) if day.day in closes else None,
                    nav=day.nav,
                    ranking_price=day.ranking_price,
                )
                for day in days
            ),
        ]

    @staticmethod
    def _returns(
        series: list[FundSeriesPointDTO],
        nav: Decimal | None,
        listed_on: date | None,
        today: date,
    ) -> tuple[Decimal | None, date | None, Decimal | None]:
        """A rentabilidade do PL por cota e o CDI do mesmo período.

        O período é de 12 meses; numa gestora mais nova começa na abertura da oferta, e
        `return_since` diz desde quando.
        """
        if not series or nav is None or series[0].nav <= 0:
            return None, None, None
        first = series[0]
        younger = listed_on is not None and listed_on > fund_ledger.one_year_before(
            today
        )
        return (
            nav / first.nav - 1,
            first.day if younger else None,
            cdi_growth(first.day, today) - 1,
        )

    @staticmethod
    def _total_return(
        series: list[FundSeriesPointDTO],
        nav: Decimal | None,
        distributions: list[FundDistributionDTO],
    ) -> Decimal | None:
        """O retorno total do período da série: a variação do PL por cota mais o rendimento pago por cota."""
        if not series or nav is None or series[0].nav <= 0:
            return None
        first = series[0]
        return (nav + paid_since(distributions, first.day)) / first.nav - 1

    def _fees(
        self,
        fund: Fund,
        nav: Decimal | None,
        today: date,
        cash_events: list[CashflowEventDTO],
    ) -> FundFeesDTO:
        terms = fund.terms
        account = fund.account
        performance_estimate = next_on = None
        if (
            nav is not None
            and terms.listed_on is not None
            and terms.high_water_mark is not None
            and terms.high_water_mark_on is not None
        ):
            performance_estimate = performance_charge(
                nav=nav,
                quotas=account.quotas,
                outside_quotas=account.outside_quotas,
                rate=terms.performance_fee,
                high_water_mark=terms.high_water_mark,
                high_water_mark_on=terms.high_water_mark_on,
                today=today,
                cdi_growth=cdi_growth(terms.high_water_mark_on, today),
                drained_per_quota=drained_since(
                    fund.distributions, terms.high_water_mark_on, account.quotas
                ),
            ).fee
            next_on = fund_ledger.next_performance_on(
                terms.last_performance_on or terms.listed_on
            )
        return FundFeesDTO(
            management_fee=terms.management_fee,
            management_monthly_estimate=(
                management_fee(nav, account.outside_quotas, terms.management_fee)
                if nav is not None
                else Decimal(0)
            ),
            performance_fee=terms.performance_fee,
            performance_estimate=performance_estimate,
            next_performance_on=next_on,
            high_water_mark=terms.high_water_mark,
            high_water_mark_on=terms.high_water_mark_on,
            received_12m=fund_ledger.fees_received(
                cash_events, fund_ledger.one_year_before(today)
            ),
            payable=terms.fee_payable,
            loan_debt=self._engine.credit_book.loan_debt(account.client_id, today),
        )

    # =========================
    # Emissão
    # =========================

    def _issuance(
        self, fund: Fund, viewer: UserDTO, today: date
    ) -> FundIssuanceStatusDTO | None:
        """A emissão aberta com a fase de hoje e o direito de preferência de quem consulta."""
        issuance = fund.issuance
        phase = fund.issuance_phase(today)
        if issuance is None or phase is None:
            return None
        right = fund.issuance_rights.get(viewer.id)
        return FundIssuanceStatusDTO(
            **issuance.model_dump(),
            phase=phase,
            raised=issuance.sold * issuance.price,
            my_rights=right.rights if right else None,
            my_bought=right.bought if right else None,
            estimate=(
                None
                if issuance.closed_on is not None
                else self._estimator.estimate(
                    fund,
                    issuance.quotas - issuance.sold,
                    issuance.price,
                    issuance.book_price,
                )
            ),
        )

    # =========================
    # Oferta
    # =========================

    def _offer(self, fund: Fund, users: list[UserDTO]) -> "_Offer":
        """A oferta como a gestora a gravou e quem comprou nela; sem oferta fica vazia."""
        terms = fund.terms
        if terms.listed_on is None:
            return _Offer(None, None, None)
        sales = repository.fund.offer_sales(terms.id)
        facts = fund_ledger.OfferFacts(
            listed_on=terms.listed_on,
            price=terms.offer_price,
            offered=terms.offer_quotas,
            totals=fund_ledger.offer_totals(sales),
            closed_on=terms.offer_closed_on,
        )
        buyers = self._buyers(sales, users) if facts.in_progress else None
        count = len({sale.buyer_user_id for sale in sales if sale.buyer_user_id})
        return _Offer(facts, buyers, count)

    def _buyers(
        self, sales: list[FundOfferSaleDTO], users: list[UserDTO]
    ) -> list[FundOfferBuyerDTO]:
        """Os compradores da oferta: cada jogador com as cotas dele, os bots somados e o
        formador de mercado, quando ele levou cotas."""
        colors = self._colors()
        bots_by_user = {user.id: user.is_bot for user in users}
        players: dict[int, Decimal] = defaultdict(Decimal)
        bots = maker = Decimal(0)
        for sale in sales:
            if sale.buyer_user_id is None:
                maker += sale.quotas
            elif bots_by_user.get(sale.buyer_user_id, False):
                bots += sale.quotas
            else:
                players[sale.buyer_user_id] += sale.quotas
        nicknames = {user.id: user.nickname for user in users}
        buyers = [
            FundOfferBuyerDTO(
                kind="player",
                user_id=user_id,
                nickname=nicknames[user_id],
                color=colors.get(user_id),
                quotas=quotas,
            )
            for user_id, quotas in sorted(
                players.items(), key=lambda item: item[1], reverse=True
            )
            if user_id in nicknames
        ]
        others: list[tuple[FundHolderKind, str, Decimal]] = [
            ("bot", BOTS_NICKNAME, bots),
            ("maker", MAKER_NICKNAME, maker),
        ]
        for kind, nickname, quotas in others:
            if quotas > 0:
                buyers.append(
                    FundOfferBuyerDTO(
                        kind=kind,
                        user_id=None,
                        nickname=nickname,
                        color=None,
                        quotas=quotas,
                    )
                )
        return buyers


@dataclass
class _Offer:
    """A oferta lida do livro: os fatos dela e os compradores (nulos quando não está em andamento)."""

    facts: fund_ledger.OfferFacts | None
    buyers: list[FundOfferBuyerDTO] | None
    # Quantos compradores a oferta teve, mesmo depois de fechada
    buyers_count: int | None
