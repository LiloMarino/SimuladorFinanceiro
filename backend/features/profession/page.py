"""
A leitura da página Profissão: o cabeçalho, os indicadores que mexem na renda e o bloco
da mecânica da profissão. Só funções do orçamento, do dia e do que o motor entrega.
"""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from itertools import pairwise

from backend.core.clt import (
    FGTS_ANNUAL_RATE,
    MONTHS_PER_YEAR,
    OVERTIME_INCOME_RATE,
    OVERTIME_MIN_GROWTH,
    fgts_deposit,
    fgts_payout,
)
from backend.core.dto.credit import PayrollLoanDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.profession import CltState
from backend.core.dto.profession_page import (
    AppointeeMechanicDTO,
    BankerMechanicDTO,
    CltMechanicDTO,
    HeirMechanicDTO,
    HouseCdbDTO,
    IncomeHeaderDTO,
    IncomeSeriesDTO,
    IncomeSeriesPointDTO,
    LeverChangeDTO,
    NoMechanicDTO,
    OffersBankerMechanicDTO,
    PublicServantMechanicDTO,
    SeriesGuideDTO,
)
from backend.core.enum import (
    IncomeSeriesEffect,
    IncomeSeriesKey,
    MeasureKind,
    MechanicStatus,
)
from backend.core.life_budget import LifeBudget, cents
from backend.core.professions import (
    DRIVER_CURVES,
    REFERENCE_WELFARE_SPENDING,
    IncomeDriver,
    LifeLevers,
    RealRaise,
)
from backend.features.credit.price import add_months
from backend.features.credit.rules import PAYROLL_SPREAD
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT
from backend.features.fixed_income.house_cdb import HOUSE_CDB_SPREAD
from backend.features.simulation.life_events import layoff_factor_of

# Quantos meses o gráfico de cada indicador mostra, contando o de hoje
SERIES_MONTHS = 12
# Até onde a alavanca do governo procura mudança, e quantas mostra
LEVER_LOOKBACK_MONTHS = 24
LEVER_MAX_CHANGES = 5

# Quem propôs a medida em vigor de um tipo num dia: (nome, sigla do partido), nulos sem autor
LeverAuthor = Callable[[MeasureKind, date], tuple[str | None, str | None]]

_DRIVER_KEYS = {
    IncomeDriver.GDP: IncomeSeriesKey.GDP,
    IncomeDriver.DOLLAR: IncomeSeriesKey.DOLLAR,
    IncomeDriver.SELIC: IncomeSeriesKey.SELIC,
    IncomeDriver.STOCKS: IncomeSeriesKey.STOCKS,
}


def build_header(
    budget: LifeBudget, day: date, unemployment: Decimal
) -> IncomeHeaderDTO:
    """Os quatro números do topo: renda, reajuste acima do IPCA, chance de demissão e imprevisto de saúde."""
    rule = budget.rule
    income = budget.net_salary_on(day)
    factor = budget.current_mechanic_state().income_factor
    layoff = (
        None
        if budget.income_loss() is None
        else Decimal(str(round(layoff_factor_of(unemployment), 4)))
        * budget.layoff_weight_on(day)
    )
    return IncomeHeaderDTO(
        income=income,
        mechanic_income=cents(income - income / factor),
        real_raise=None
        if rule.real_raise is RealRaise.NONE
        else budget.real_raise_on(day),
        real_raise_source=rule.real_raise,
        inflation_indexed=budget.inflation_adjusted and rule.inflation_indexed,
        income_loss=budget.income_loss(),
        layoff_factor=layoff,
        unemployment=unemployment,
        neutral_unemployment=NEUTRAL_UNEMPLOYMENT,
        health_multiple=budget.health_multiple,
        health_multiple_base=rule.health_multiple,
    )


def _months_back(day: date) -> list[date]:
    """Os `SERIES_MONTHS` dias do gráfico, do mais antigo a hoje, um por mês."""
    return [add_months(day, -back) for back in range(SERIES_MONTHS - 1, -1, -1)]


def _points(
    day: date, value_on: Callable[[date], Decimal]
) -> list[IncomeSeriesPointDTO]:
    return [IncomeSeriesPointDTO(month=d, value=value_on(d)) for d in _months_back(day)]


def _lever_changes(
    day: date,
    value_of: Callable[[LifeLevers], Decimal],
    levers_on: Callable[[date], LifeLevers],
    kind: MeasureKind,
    author_on: LeverAuthor,
) -> list[LeverChangeDTO]:
    """As mudanças da alavanca nos últimos meses, da mais recente à mais antiga, cada uma com o autor da medida que passou a valer."""
    changes: list[LeverChangeDTO] = []
    months = [add_months(day, -back) for back in range(LEVER_LOOKBACK_MONTHS, -1, -1)]
    for before, after in pairwise(months):
        old, new = value_of(levers_on(before)), value_of(levers_on(after))
        if old != new:
            name, party = author_on(kind, after)
            changes.append(
                LeverChangeDTO(
                    change_date=after,
                    before=old,
                    after=new,
                    proposer_name=name,
                    proposer_party=party,
                )
            )
    return changes[::-1][:LEVER_MAX_CHANGES]


def build_series(
    budget: LifeBudget,
    day: date,
    unemployment_on: Callable[[date], Decimal],
    author_on: LeverAuthor,
) -> list[IncomeSeriesDTO]:
    """
    Cada indicador que mexe na renda da profissão: o PIB, o desemprego, a variável da
    renda e a alavanca do governo. Vazio quando a renda só sobe com o IPCA.
    """
    rule = budget.rule
    series: list[IncomeSeriesDTO] = []
    gdp_raise = rule.real_raise is RealRaise.GDP_SHARE
    if gdp_raise or rule.driver is IncomeDriver.GDP:
        series.append(
            IncomeSeriesDTO(
                key=IncomeSeriesKey.GDP,
                current=budget.growth_on(day),
                neutral=DRIVER_CURVES[IncomeDriver.GDP].neutral,
                points=_points(day, budget.growth_on),
                # A hora extra do CLT só existe a partir de PIB zero
                guides=[SeriesGuideDTO(value=OVERTIME_MIN_GROWTH, overtime=True)]
                if gdp_raise
                else [],
                effect=budget.real_raise_on(day)
                if gdp_raise
                else budget.driver_factor_on(day),
                effect_kind=IncomeSeriesEffect.REAL_RAISE
                if gdp_raise
                else IncomeSeriesEffect.INCOME_FACTOR,
                changes=[],
                lever=False,
            )
        )
    if budget.income_loss() is not None:
        current = unemployment_on(day)
        series.append(
            IncomeSeriesDTO(
                key=IncomeSeriesKey.UNEMPLOYMENT,
                current=current,
                neutral=NEUTRAL_UNEMPLOYMENT,
                points=_points(day, unemployment_on),
                guides=[],
                effect=Decimal(str(round(layoff_factor_of(current), 4)))
                * budget.layoff_weight_on(day),
                effect_kind=IncomeSeriesEffect.LAYOFF_FACTOR,
                changes=[],
                lever=False,
            )
        )
    driver = rule.driver
    if driver is not None and driver is not IncomeDriver.GDP:
        value_on = {
            IncomeDriver.DOLLAR: budget.dollar_change_on,
            IncomeDriver.SELIC: budget.selic_on,
            IncomeDriver.STOCKS: budget.stocks_return_on,
        }[driver]
        series.append(
            IncomeSeriesDTO(
                key=_DRIVER_KEYS[driver],
                current=value_on(day),
                neutral=DRIVER_CURVES[driver].neutral,
                points=_points(day, value_on),
                guides=[],
                effect=budget.driver_factor_on(day),
                effect_kind=IncomeSeriesEffect.INCOME_FACTOR,
                changes=[],
                lever=False,
            )
        )
    levers = budget.levers_on(day)
    lever_keys = {
        RealRaise.SERVANTS: (
            IncomeSeriesKey.SERVANT_RAISE,
            lambda lv: lv.servant_raise,
            MeasureKind.SERVANT_RAISE,
        ),
        RealRaise.RETIREES: (
            IncomeSeriesKey.RETIREE_RAISE,
            lambda lv: lv.retiree_raise,
            MeasureKind.RETIREE_RAISE,
        ),
    }
    if rule.real_raise in lever_keys:
        key, value_of, kind = lever_keys[rule.real_raise]
        series.append(
            IncomeSeriesDTO(
                key=key,
                current=value_of(levers),
                neutral=value_of(LifeLevers()),
                points=[],
                guides=[],
                effect=levers.real_raise_of(rule.real_raise),
                effect_kind=IncomeSeriesEffect.REAL_RAISE,
                changes=_lever_changes(
                    day, value_of, budget.levers_on, kind, author_on
                ),
                lever=True,
            )
        )
    if rule.benefit_multiple > 0:
        series.append(
            IncomeSeriesDTO(
                key=IncomeSeriesKey.WELFARE_SPENDING,
                current=levers.welfare_spending,
                neutral=REFERENCE_WELFARE_SPENDING,
                points=[],
                guides=[],
                effect=levers.welfare_spending / REFERENCE_WELFARE_SPENDING,
                effect_kind=IncomeSeriesEffect.BENEFIT,
                changes=_lever_changes(
                    day,
                    lambda lv: lv.welfare_spending,
                    budget.levers_on,
                    MeasureKind.WELFARE_SPENDING,
                    author_on,
                ),
                lever=True,
            )
        )
    return series


def clt_block(
    state: CltState, gross: Decimal, tr_monthly: Decimal, growth: Decimal
) -> CltMechanicDTO:
    """O bloco do CLT: o FGTS (saldo, depósito do mês, rendimento e saída na demissão) e a hora extra."""
    offered = growth >= OVERTIME_MIN_GROWTH
    tr_year = (1 + tr_monthly) ** MONTHS_PER_YEAR - 1
    if state.overtime:
        status = MechanicStatus.ACTIVE
    elif not offered:
        status = MechanicStatus.LOCKED
    else:
        status = MechanicStatus.AVAILABLE
    return CltMechanicDTO(
        status=status,
        fgts_balance=state.fgts_balance,
        fgts_deposit=fgts_deposit(gross),
        tr=tr_year,
        fgts_yield=(1 + FGTS_ANNUAL_RATE) * (1 + tr_year) - 1,
        layoff_payout=fgts_payout(state.fgts_balance),
        overtime=state.overtime,
        overtime_rate=OVERTIME_INCOME_RATE,
        overtime_income=cents(gross * OVERTIME_INCOME_RATE / (1 + OVERTIME_INCOME_RATE))
        if state.overtime
        else cents(gross * OVERTIME_INCOME_RATE),
        growth=growth,
        overtime_offered=offered,
        overtime_waiting=state.overtime_waiting,
    )


def public_servant_block(
    loans: list[PayrollLoanDTO],
    net_salary: Decimal,
    margin: Decimal,
    margin_used: Decimal,
    annual_rate: Decimal,
) -> PublicServantMechanicDTO:
    """O bloco do Servidor: a margem consignável, os contratos e a taxa de hoje."""
    free = max(margin - margin_used, Decimal(0))
    # A margem volta a abrir quando termina o contrato que acaba primeiro
    endings = [
        (
            add_months(
                loan.next_due, loan.total_installments - loan.paid_installments - 1
            ),
            loan.installment,
        )
        for loan in loans
        if loan.next_due is not None
    ]
    release = min((day for day, _ in endings), default=None)
    # Os contratos que acabam no mesmo dia liberam a soma das parcelas
    released = sum((fee for day, fee in endings if day == release), Decimal(0))
    if free > 0:
        status = MechanicStatus.ACTIVE if loans else MechanicStatus.AVAILABLE
    else:
        status = MechanicStatus.LOCKED
    return PublicServantMechanicDTO(
        status=status,
        net_salary=net_salary,
        margin=margin,
        margin_used=margin_used,
        margin_free=free,
        annual_rate=annual_rate,
        selic=annual_rate - PAYROLL_SPREAD,
        loans=loans,
        next_release=release,
        next_release_amount=released if release else None,
    )


def banker_block(
    terms: dict[int, FixedIncomeAssetDTO],
    applied_of: Callable[[FixedIncomeAssetDTO], Decimal],
    value_of: Callable[[FixedIncomeAssetDTO], Decimal],
) -> BankerMechanicDTO:
    """O bloco do Bancário: os CDBs da casa do mês, por prazo em anos, com taxa, teto, quanto foi aplicado em cada um e quanto vale hoje."""
    cdbs = []
    for years, asset in terms.items():
        cap = asset.player_cap or Decimal(0)
        cdbs.append(
            HouseCdbDTO(
                years=years,
                annual_rate=asset.interest_rate,
                treasury_rate=asset.interest_rate - HOUSE_CDB_SPREAD,
                cap=cap,
                applied=applied_of(asset),
                current_value=value_of(asset),
                maturity_date=asset.maturity_date,
            )
        )
    full = bool(cdbs) and all(c.applied >= c.cap for c in cdbs)
    applied_any = any(c.applied > 0 for c in cdbs)
    if full:
        status = MechanicStatus.LOCKED
    elif applied_any:
        status = MechanicStatus.ACTIVE
    else:
        status = MechanicStatus.AVAILABLE
    return BankerMechanicDTO(status=status, cdbs=cdbs)


def heir_block(
    budget: LifeBudget, day: date, joined: date, starting_cash: Decimal, end_date: date
) -> HeirMechanicDTO:
    """O bloco do Herdeiro: a herança que entrou com ele e quantos anos de despesa ela cobre."""
    inheritance = (
        budget.starting_capital(starting_cash, joined, end_date) - starting_cash
    )
    annual_expense = budget.expense_on(day) * MONTHS_PER_YEAR
    return HeirMechanicDTO(
        inheritance=inheritance,
        received_on=joined,
        annual_expense=annual_expense,
        covered_years=inheritance / annual_expense
        if annual_expense > 0
        else Decimal(0),
    )


def appointee_block(
    budget: LifeBudget, day: date, party: str | None, election_day: date | None
) -> AppointeeMechanicDTO:
    """O bloco do Comissionado: o partido, quanto a renda rende com ele dentro e fora do governo e a distância até a votação."""
    rule = budget.rule
    return AppointeeMechanicDTO(
        party=party,
        in_government=budget.in_government_on(day),
        multiple_now=budget.multiple_on(day),
        multiple_in_government=rule.income_multiple,
        multiple_outside=rule.outside_multiple or rule.income_multiple,
        election_in_months=(
            None
            if election_day is None
            else max(
                (election_day.year - day.year) * 12 + election_day.month - day.month,
                0,
            )
        ),
    )


def offers_banker_block(
    commissions: list[tuple[date, Decimal]], day: date
) -> OffersBankerMechanicDTO:
    """O bloco do Banqueiro de ofertas: as comissões do mês e o total, cada comissão uma oferta fechada."""
    month = [
        amount
        for when, amount in commissions
        if (when.year, when.month) == (day.year, day.month)
    ]
    return OffersBankerMechanicDTO(
        month_commission=sum(month, Decimal(0)),
        month_offers=len(month),
        total_commission=sum((amount for _, amount in commissions), Decimal(0)),
        total_offers=len(commissions),
    )


def no_block() -> NoMechanicDTO:
    return NoMechanicDTO()
