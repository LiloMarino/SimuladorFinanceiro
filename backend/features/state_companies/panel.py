"""O painel das estatais: a leitura da sala, as prévias de ordem e de fundação."""

from collections.abc import Callable, Mapping
from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.government import MeasurePreviewDTO
from backend.core.dto.state_company import (
    StateCompaniesPanelDTO,
    StateCompanyDTO,
    StateCompanyRowDTO,
    StateFoundingPreviewDTO,
    StateLeverRuleDTO,
    StateMovementDTO,
    StateOfferDTO,
    StateOrderDTO,
    StateOrderPreviewDTO,
    StatePolicyEffectDTO,
    StateRulesDTO,
    StateSizeRuleDTO,
    StateStepEffectDTO,
    StateSummaryDTO,
)
from backend.core.enum import (
    DividendPolicy,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
    StateMovementKind,
)
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.features.state_companies import fair_value, gdp, levers, payout, price
from backend.features.state_companies.book import (
    FOUNDING_GOVERNMENT_SHARE,
    PRIVATIZATION_SESSIONS,
    MarketPrice,
    StateCompanyBook,
    government_shares,
    invested_by,
)
from backend.features.state_companies.orders import StateOrder, order_changes

# Quantos movimentos o painel mostra
MOVEMENTS_SHOWN = 20

# Meses fechados que somam o "Ao Tesouro em 12 meses"
TREASURY_MONTHS = 12

FACTOR_PLACES = Decimal("0.0001")

NO_LEVER_REASON = "Essa estatal não tem preço a segurar."

type Given = Mapping[str, StateOrder]


def _order_dto(order: StateOrder) -> StateOrderDTO:
    return StateOrderDTO(control=order.control, dividend_policy=order.dividend_policy)


def _factor(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(FACTOR_PLACES)


def _treasury_12m(
    book: StateCompanyBook, company: StateCompanyDTO, today: date
) -> Decimal:
    """Ao Tesouro nos 12 últimos meses fechados: os meses gravados da fundada, o provento das datas ex da importada."""
    if company.origin is not StateCompanyOrigin.FOUNDED:
        return book.imported_dividends_12m(company, today)
    months = repository.state_company.months_of(company.id)[-TREASURY_MONTHS:]
    return sum((m.treasury_dividend for m in months), Decimal(0))


def _rules() -> StateRulesDTO:
    """As constantes de regra que o painel entrega: o front lê daqui e não repete número."""
    return StateRulesDTO(
        founding_share=FOUNDING_GOVERNMENT_SHARE,
        offer_sessions=PRIVATIZATION_SESSIONS,
        sizes=[
            StateSizeRuleDTO(
                size=size,
                capital=invested_by(size),
                government_debt=invested_by(size) * FOUNDING_GOVERNMENT_SHARE,
            )
            for size in StateCompanySize
        ],
        levers=[
            StateLeverRuleDTO(
                lever=lever,
                ipca_weight=levers.LEVER_WEIGHT[lever],
                credit_weight=levers.CREDIT_WEIGHT[lever],
            )
            for lever in StateLever
        ],
    )


def _movements(book: StateCompanyBook, today: date) -> list[StateMovementDTO]:
    """Os fatos das estatais até hoje: as datas de cada empresa e cada mudança de ordem que já vale."""
    moves: list[StateMovementDTO] = []

    def add(
        day: date,
        kind: StateMovementKind,
        ticker: str,
        order: StateOrder | None = None,
        amount: Decimal | None = None,
    ) -> None:
        moves.append(
            StateMovementDTO(
                day=day,
                kind=kind,
                ticker=ticker,
                control=None if order is None else order.control,
                dividend_policy=None if order is None else order.dividend_policy,
                amount=amount,
            )
        )

    for company in book.companies():
        if company.founded_on is not None:
            add(company.founded_on, StateMovementKind.FOUNDED, company.ticker)
        if company.offer_opened_on is not None:
            add(
                company.offer_opened_on,
                StateMovementKind.PRIVATIZATION_OPENED,
                company.ticker,
            )
        if company.privatized_on is not None:
            add(
                company.privatized_on,
                StateMovementKind.PRIVATIZED,
                company.ticker,
                amount=company.proceeds,
            )
    history = book.order_history()
    previous: Mapping[str, StateOrder] = {}
    for start in sorted(m for m in history if m <= today):
        for change in order_changes(previous, history[start]):
            company = book.company(change.ticker)
            if company is None:
                continue
            if change.control_changed:
                kind = (
                    StateMovementKind.CONTROL_RELEASED
                    if change.after.control is StateControl.NONE
                    else StateMovementKind.CONTROL_SET
                )
                add(start, kind, change.ticker, change.after)
            privatized = company.privatized_on is not None and (
                start >= company.privatized_on
            )
            if change.policy_changed and not privatized:
                add(
                    start,
                    StateMovementKind.DIVIDEND_POLICY_SET,
                    change.ticker,
                    change.after,
                )
        previous = history[start]
    return sorted(moves, key=lambda m: m.day, reverse=True)[:MOVEMENTS_SHOWN]


def _offer(
    book: StateCompanyBook,
    company: StateCompanyDTO,
    name: str,
    today: date,
    market_price: MarketPrice,
    portfolio_id: int | None,
    cash_of: Callable[[int], Decimal],
) -> StateOfferDTO | None:
    ends_on = book.offer_ends_on(company.ticker)
    if ends_on is None or company.offer_opened_on is None:
        return None
    reservations = repository.state_company.reservations_of(company.id)
    return StateOfferDTO(
        ticker=company.ticker,
        name=name,
        opened_on=company.offer_opened_on,
        ends_on=ends_on,
        shares=government_shares(company),
        price=book.offer_price(company, today),
        market_price=market_price(company.ticker),
        reserved=sum(reservations.values(), Decimal(0)),
        your_reservation=(
            None if portfolio_id is None else reservations.get(portfolio_id)
        ),
        your_cash=Decimal(0) if portfolio_id is None else cash_of(portfolio_id),
    )


def build_panel(
    book: StateCompanyBook,
    *,
    today: date,
    is_president: bool,
    given: Given,
    privatizing: Mapping[str, int],
    name_of: Callable[[str], str],
    market_price: MarketPrice,
    portfolio_id: int | None,
    cash_of: Callable[[int], Decimal],
) -> StateCompaniesPanelDTO:
    """
    O painel da sala. `given` são as ordens já dadas, mesmo as que só valem no mês seguinte;
    `privatizing` leva, por código, a medida de privatização na fila ou aprovada.
    """
    in_force = book.orders(today)
    rows: list[StateCompanyRowDTO] = []
    offers: list[StateOfferDTO] = []
    for company in book.companies():
        name = name_of(company.ticker)
        unit = market_price(company.ticker) or book.offer_price(company, today)
        sold = company.status is StateCompanyStatus.PRIVATIZED
        active = in_force.get(company.ticker, StateOrder())
        rows.append(
            StateCompanyRowDTO(
                ticker=company.ticker,
                name=name,
                origin=company.origin,
                status=company.status,
                lever=company.lever,
                size=company.size,
                government_share=Decimal(0) if sold else company.government_share,
                shares=company.shares,
                price=unit,
                government_value=(
                    Decimal(0)
                    if sold or unit is None
                    else unit * government_shares(company)
                ),
                invested=(
                    company.invested * FOUNDING_GOVERNMENT_SHARE
                    if company.origin is StateCompanyOrigin.FOUNDED
                    else None
                ),
                fair_price=None if sold else book.offer_price(company, today),
                order=_order_dto(given.get(company.ticker, StateOrder())),
                in_force=_order_dto(active),
                held_points=(
                    levers.held_points(company.lever, active.control)
                    if company.lever is not None
                    else Decimal(0)
                ),
                treasury_dividend_12m=_treasury_12m(book, company, today),
                can_command=(
                    is_president
                    and company.status is StateCompanyStatus.ACTIVE
                    and company.ticker not in privatizing
                ),
                privatization_measure_id=privatizing.get(company.ticker),
                founded_on=company.founded_on,
                privatized_on=company.privatized_on,
                proceeds=company.proceeds,
            )
        )
        offer = _offer(book, company, name, today, market_price, portfolio_id, cash_of)
        if offer is not None:
            offers.append(offer)
    return StateCompaniesPanelDTO(
        is_president=is_president,
        rules=_rules(),
        summary=StateSummaryDTO(
            government_value=sum((r.government_value for r in rows), Decimal(0)),
            treasury_dividends_12m=sum(
                (r.treasury_dividend_12m for r in rows), Decimal(0)
            ),
            backlog_points=book.backlog(today),
            held_points=book.held_points(today),
            cap_points=levers.IPCA_CAP_POINTS,
        ),
        companies=rows,
        movements=_movements(book, today),
        offers=offers,
    )


def _monthly_treasury(
    book: StateCompanyBook, company: StateCompanyDTO, today: date, order: StateOrder
) -> Decimal | None:
    """O dividendo esperado ao Tesouro por mês sob a ordem; None na fundada sem lucro modelado."""
    if company.origin is StateCompanyOrigin.IMPORTED:
        return book.expected_imported_dividend(company, today, order)
    profit = book.expected_month_profit(company, today)
    if profit is None:
        return None
    return payout.dividend(profit, order.dividend_policy, order.control) * (
        company.government_share
    )


def _step_effects(
    book: StateCompanyBook,
    company: StateCompanyDTO,
    today: date,
    current: StateOrder,
    others: Decimal,
) -> list[StateStepEffectDTO]:
    if company.lever is None:
        available = {
            control: (
                Decimal(0),
                None if control is StateControl.NONE else NO_LEVER_REASON,
            )
            for control in StateControl
        }
    else:
        available = {
            step.control: (step.points, step.blocked_reason)
            for step in levers.step_availability(company.lever, others)
        }
    effects: list[StateStepEffectDTO] = []
    for control, (points, reason) in available.items():
        order = StateOrder(control, current.dividend_policy)
        effects.append(
            StateStepEffectDTO(
                control=control,
                percent=control.percent,
                held_points=points,
                credit_points=(
                    levers.credit_points(company.lever, control)
                    if company.lever is not None
                    else Decimal(0)
                ),
                profit_cut=payout.profit_cut(control),
                price_factor=_factor(price.price_factor(order)),
                dividend_factor=_factor(price.dividend_factor(order)),
                monthly_treasury_dividend=_monthly_treasury(
                    book, company, today, order
                ),
                blocked_reason=reason,
            )
        )
    return effects


def build_order_preview(
    book: StateCompanyBook,
    ticker: str,
    *,
    today: date,
    can_command: bool,
    given: Given,
    name: str,
) -> StateOrderPreviewDTO:
    """O efeito de cada degrau (com a política de hoje) e de cada política (com o controle de hoje)."""
    company = book.company(ticker)
    if company is None:
        raise NotFoundError("Estatal não encontrada.")
    current = given.get(ticker, StateOrder())
    others = book.other_points(ticker, given)
    policies = [
        StatePolicyEffectDTO(
            dividend_policy=policy,
            payout=payout.payout_ratio(policy),
            price_factor=_factor(
                price.price_factor(StateOrder(current.control, policy))
                * price.sustained_policy_factor(policy)
            ),
            dividend_factor=_factor(
                price.dividend_factor(StateOrder(current.control, policy))
            ),
            monthly_treasury_dividend=_monthly_treasury(
                book, company, today, StateOrder(current.control, policy)
            ),
        )
        for policy in DividendPolicy
    ]
    return StateOrderPreviewDTO(
        ticker=ticker,
        name=name,
        lever=company.lever,
        can_command=can_command,
        order=_order_dto(current),
        cap_points=levers.IPCA_CAP_POINTS,
        other_points=others,
        backlog_points=book.backlog(today),
        steps=_step_effects(book, company, today, current, others),
        policies=policies,
    )


def build_founding_preview(
    book: StateCompanyBook,
    measure: MeasurePreviewDTO,
    *,
    size: StateCompanySize,
    lever: StateLever | None,
    real_interest: Decimal,
) -> StateFoundingPreviewDTO:
    """
    Os efeitos da empresa nova ao lado da medida: o capital, o gasto da fundação por mês, o
    empurrão no crescimento e o dividendo esperado ao Tesouro com a política normal.
    """
    invested = invested_by(size)
    mean = fair_value.mean_annual_return(real_interest)
    yearly_profit = max(invested * mean, Decimal(0))
    return StateFoundingPreviewDTO(
        measure=measure,
        invested=invested,
        monthly_spending=gdp.founding_installment(invested),
        spending_months=gdp.FOUNDING_MONTHS,
        gdp_push=book.founding_push(size, lever, measure.effective.replace(day=1)),
        expected_treasury_dividend_year=(
            payout.dividend(yearly_profit, DividendPolicy.NORMAL, StateControl.NONE)
            * FOUNDING_GOVERNMENT_SHARE
        ),
    )
