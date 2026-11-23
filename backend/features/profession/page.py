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
from backend.core.dates import add_months
from backend.core.dto.credit import PayrollLoanDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.profession import (
    CltState,
    EntrepreneurState,
    ExporterState,
    FreelancerState,
    RetireeState,
    WelfareState,
)
from backend.core.dto.profession_page import (
    AppointeeMechanicDTO,
    BankerMechanicDTO,
    CapitalSaleOptionDTO,
    CltMechanicDTO,
    EntrepreneurMechanicDTO,
    ExchangeLockDTO,
    ExchangeLockOptionDTO,
    ExporterMechanicDTO,
    FreelancerMechanicDTO,
    HeirMechanicDTO,
    HouseCdbDTO,
    IncomeHeaderDTO,
    IncomeSeriesDTO,
    IncomeSeriesPointDTO,
    LeverChangeDTO,
    NoMechanicDTO,
    OffersBankerMechanicDTO,
    PriceRowDTO,
    PublicServantMechanicDTO,
    RedeemBracketDTO,
    RetireeMechanicDTO,
    SeriesGuideDTO,
    WelfareMechanicDTO,
)
from backend.core.entrepreneur import (
    SALE_SHARES,
    capital_income,
    capital_rate,
    sale_part,
    sale_proceeds,
    split_profit,
)
from backend.core.enum import (
    IncomeSeriesEffect,
    IncomeSeriesKey,
    MeasureKind,
    MechanicStatus,
    Profession,
)
from backend.core.exporter import LOCK_TERMS_MONTHS
from backend.core.freelancer import (
    REFERENCE_EMPTY_MONTH,
    STALE_DEVIATION,
    TABLE_DEVIATIONS,
    clients_on,
)
from backend.core.life_budget import LifeBudget, cents, no_mechanic_state
from backend.core.pension import (
    REDEEM_BRACKETS,
    annual_yield,
    income_rate,
    months_in_plan,
    next_bracket,
    redeem_bracket,
)
from backend.core.professions import (
    DRIVER_CURVES,
    REFERENCE_WELFARE_SPENDING,
    IncomeDriver,
    LifeLevers,
    RealRaise,
)
from backend.core.welfare import (
    COURSE_INCOME_FACTOR,
    COURSE_MONTHS,
    course_ends_on,
    course_months_done,
    deposit_amount,
    deposit_cap,
    deposit_rate,
    next_release_on,
    releases_reached,
    spending_factor,
)
from backend.features.credit.rules import PAYROLL_SPREAD
from backend.features.economy.growth import NEUTRAL_UNEMPLOYMENT
from backend.features.fixed_income.house_cdb import HOUSE_CDB_SPREAD
from backend.features.profession.entrepreneur import capital_months_ago
from backend.features.profession.exporter import mix_change_allowed, next_mix_change
from backend.features.profession.freelancer import (
    next_price_change,
    price_change_allowed,
)
from backend.features.profession.pension import (
    converted_amount,
    converted_real_rate,
)
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
    converted = budget.converted_income_on(day)
    factor = budget.current_mechanic_state().income_factor
    layoff = (
        None
        if budget.income_loss() is None
        else Decimal(str(round(layoff_factor_of(unemployment), 4)))
        * budget.layoff_weight_on(day)
    )
    return IncomeHeaderDTO(
        income=income,
        mechanic_income=max(cents((income - converted) * (1 - 1 / factor)), Decimal(0))
        + converted,
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
    mixes_gdp = budget.exporter_state() is not None
    if gdp_raise or rule.driver is IncomeDriver.GDP or mixes_gdp:
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
                else budget.gdp_factor_on(day),
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
                effect=budget.dollar_factor_on(day)
                if driver is IncomeDriver.DOLLAR
                else budget.driver_factor_on(day),
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


def exporter_block(
    state: ExporterState, budget: LifeBudget, day: date, quotes: dict[int, Decimal]
) -> ExporterMechanicDTO:
    """
    O bloco do Exportador: o mix com os fatores de cada parte, a trava em vigor (com o
    ganho acumulado) e o dólar travado de cada prazo, que `quotes` traz por meses.
    """
    dollar = budget.dollar_on(day)
    exported = budget.dollar_factor_on(day)
    domestic = budget.gdp_factor_on(day)
    combined = budget.driver_factor_on(day)
    exported_part = state.export_share * exported
    lock = state.lock
    return ExporterMechanicDTO(
        status=MechanicStatus.AVAILABLE if lock is None else MechanicStatus.ACTIVE,
        dollar=dollar,
        dollar_change=budget.dollar_change_on(day),
        growth=budget.growth_on(day),
        export_share=state.export_share,
        exported_factor=exported,
        domestic_factor=domestic,
        mix_factor=combined,
        exported_revenue=cents(budget.salary_on(day) * exported_part / combined)
        if combined > 0
        else Decimal(0),
        can_change_mix=mix_change_allowed(state, day),
        next_mix_change=next_mix_change(state),
        lock_options=[
            ExchangeLockOptionDTO(months=months, locked_dollar=quotes[months])
            for months in LOCK_TERMS_MONTHS
        ],
        lock=None
        if lock is None
        else ExchangeLockDTO(
            locked_dollar=lock.locked_dollar,
            share=lock.share,
            months=lock.months,
            paid_months=lock.paid_months,
            expires_on=lock.expires_on,
            dollar_gap=lock.locked_dollar - dollar,
            gain=lock.gain,
        ),
    )


def _percent_note(value: Decimal) -> str:
    """Fração em percentual com a vírgula e sem a casa decimal zerada: 0.055 vira 5,5% e 0.09 vira 9%."""
    text = f"{value * 100:.1f}".replace(".", ",")
    return text.removesuffix(",0") + "%"


def _unemployment_note(unemployment: Decimal, neutral: Decimal) -> str:
    """A frase do desemprego de hoje contra o neutro e do que ele faz com a perda de clientes por cobrar caro."""
    now, base = _percent_note(unemployment), _percent_note(neutral)
    if unemployment < neutral:
        return f"Com o desemprego em {now}, abaixo do neutro de {base}, a perda de clientes por cobrar caro é menor."
    if unemployment > neutral:
        return f"Com o desemprego em {now}, acima do neutro de {base}, a perda de clientes por cobrar caro é maior."
    return f"Com o desemprego em {now}, no neutro, a perda de clientes por cobrar caro é a normal."


def freelancer_block(
    state: FreelancerState, budget: LifeBudget, day: date, unemployment: Decimal
) -> FreelancerMechanicDTO:
    """
    O bloco do Autônomo: o preço e a referência do mercado, os clientes e a renda do
    mês, a faixa que o novo preço aceita e a tabela do que cada preço renderia hoje.
    """
    price = budget.price_on(day)
    reference = budget.reference_price_on(day)
    deviation = budget.price_deviation_on(day)
    since = state.price_set_on or budget.start_date
    clients = budget.clients_on(day)
    ratio = budget.unemployment_ratio_on(day)
    low, high = budget.price_range_on(day)
    stale = deviation <= STALE_DEVIATION
    # A chance do mês sem clientes é a do sorteio: a da referência com o desemprego do dia, pesada pelo preço
    day_chance = REFERENCE_EMPTY_MONTH * Decimal(
        str(round(layoff_factor_of(unemployment), 4))
    )
    rows = []
    for step in (Decimal(0), *TABLE_DEVIATIONS):
        row_price = cents(reference * (1 + step))
        # Os clientes e a chance seguem o preço em centavos, o mesmo que o jogador salva
        priced = row_price / reference - 1
        row_clients = clients_on(priced, ratio)
        rows.append(
            PriceRowDTO(
                price=row_price,
                deviation=step,
                clients=row_clients,
                income=cents(row_price * row_clients),
                empty_month_chance=min(
                    day_chance * budget.layoff_weight_on(day, priced), Decimal(1)
                ),
            )
        )
    return FreelancerMechanicDTO(
        status=MechanicStatus.AVAILABLE
        if stale or state.price is None
        else MechanicStatus.ACTIVE,
        price=cents(price),
        price_since=since,
        deviation=deviation,
        reference=cents(reference),
        reference_rise=reference / budget.reference_price_on(since) - 1,
        clients=clients,
        month_income=cents(price * clients),
        unemployment_note=_unemployment_note(unemployment, NEUTRAL_UNEMPLOYMENT),
        min_price=low,
        max_price=high,
        can_change_price=price_change_allowed(state, day),
        next_price_change=next_price_change(state),
        stalled_months=(day.year - since.year) * MONTHS_PER_YEAR
        + day.month
        - since.month,
        stale=stale,
        rows=rows,
    )


def entrepreneur_block(
    state: EntrepreneurState,
    budget: LifeBudget,
    day: date,
    negative_quarters: int,
) -> EntrepreneurMechanicDTO:
    """
    O bloco do Empreendedor: o capital e o rendimento do mês pelo PIB de 12 meses, o
    lucro e a fração que volta para a empresa e o que cada venda de parte do capital
    põe no caixa.
    """
    growth = budget.growth_on(day)
    profit = budget.net_salary_on(day)
    reinvested, _ = split_profit(profit, state.reinvest_share)
    options = []
    for share in SALE_SHARES:
        part = sale_part(state.capital, share)
        options.append(
            CapitalSaleOptionDTO(share=share, part=part, proceeds=sale_proceeds(part))
        )
    active = state.capital > 0 or state.reinvest_share > 0
    return EntrepreneurMechanicDTO(
        status=MechanicStatus.ACTIVE if active else MechanicStatus.AVAILABLE,
        capital=state.capital,
        capital_months_ago=capital_months_ago(state),
        income=capital_income(state.capital, growth),
        rate=capital_rate(growth),
        growth=growth,
        profit=profit,
        reinvest_share=state.reinvest_share,
        reinvested=reinvested,
        recession=growth < 0,
        negative_quarters=negative_quarters,
        sale_options=options,
    )


def retiree_block(
    state: RetireeState,
    budget: LifeBudget,
    day: date,
    cdi: Decimal,
    selic: Decimal,
    expected_ipca: Decimal,
    expected_ipca_from_focus: bool,
    real_rate: Decimal,
) -> RetireeMechanicDTO:
    """
    O bloco do Aposentado: o saldo e o que ele rende, a renda já convertida, o juro real
    de hoje e o IR do resgate com a tabela e a faixa seguinte. O valor digitado o front
    calcula com as taxas daqui.
    """
    months = 0 if state.since is None else months_in_plan(state.since, day)
    bracket = redeem_bracket(months)
    later = next_bracket(months)
    wait = None if later is None else later.from_months - months
    return RetireeMechanicDTO(
        status=MechanicStatus.ACTIVE if state.conversions else MechanicStatus.AVAILABLE,
        balance=state.balance or Decimal(0),
        annual_rate=annual_yield(cdi),
        cdi=cdi,
        converted_income=budget.converted_income_on(day),
        converted_amount=converted_amount(state),
        converted_real_rate=converted_real_rate(state),
        real_rate=real_rate,
        selic=selic,
        expected_ipca=expected_ipca,
        expected_ipca_from_focus=expected_ipca_from_focus,
        income_rate=income_rate(real_rate) if real_rate > 0 else Decimal(0),
        inflation_indexed=budget.inflation_adjusted,
        redeem_rate=bracket.rate,
        months_in_plan=months,
        next_rate=None if later is None else later.rate,
        next_rate_months=wait,
        next_rate_on=None if wait is None else add_months(day, wait),
        brackets=[
            RedeemBracketDTO(label=item.label, rate=item.rate, current=item is bracket)
            for item in REDEEM_BRACKETS
        ],
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


def welfare_block(
    state: WelfareState,
    budget: LifeBudget,
    day: date,
    start: date,
    wealth: Decimal,
) -> WelfareMechanicDTO:
    """
    O bloco do Auxílio: o Pé-de-Meia com o depósito que o mês rende hoje (a sobra desde o
    início do mês, com o fator do gasto do governo), a tarifa social e o curso técnico com
    a renda do bico antes e durante ele e o salário que o CLT pagaria ao concluir.
    """
    factor = spending_factor(budget.levers_on(day).welfare_spending)
    net_income = budget.net_salary_on(day)
    surplus = (
        Decimal(0)
        if state.month_start_wealth is None
        else wealth - state.month_start_wealth
    )
    full = budget.with_mechanic_state(no_mechanic_state)
    return WelfareMechanicDTO(
        status=MechanicStatus.ACTIVE,
        balance=state.balance,
        next_release_on=next_release_on(start, releases_reached(start, day)),
        cash_was_negative=state.cash_was_negative,
        deposit=deposit_amount(surplus, net_income, factor),
        surplus=surplus,
        deposit_rate=deposit_rate(factor),
        deposit_cap=deposit_cap(net_income, factor),
        deposit_factor=factor,
        full_expense=budget.expense_on(day),
        paid_expense=budget.paid_expense_on(day),
        discount=budget.expense_on(day) - budget.paid_expense_on(day),
        gig_income=full.exposed_net_on(day),
        gig_income_in_course=cents(full.exposed_net_on(day) * COURSE_INCOME_FACTOR),
        clt_salary=full.for_profession(Profession.CLT).net_salary_on(day),
        in_course=state.in_course,
        course_months=COURSE_MONTHS,
        course_months_done=None
        if state.course_enrolled_on is None
        else course_months_done(state.course_enrolled_on, day),
        course_ends_on=None
        if state.course_enrolled_on is None
        else course_ends_on(state.course_enrolled_on),
    )


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
