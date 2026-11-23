"""Renda e despesa mensais da partida e a meta do viver de renda que sai delas."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.dto.profession import (
    ExchangeLock,
    ExporterState,
    FreelancerState,
    MechanicState,
    RetireeState,
)
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import IncomeLoss, IndicatorSeries, Profession
from backend.core.freelancer import (
    REFERENCE_CLIENTS,
    clients_on,
    empty_month_weight,
    price_range,
)
from backend.core.indicators import (
    anniversaries,
    annual_index_rate,
    inflation_factor,
    monthly_inflation_factor,
)
from backend.core.periods import MONTHS_PER_YEAR
from backend.core.professions import (
    DAYS_PER_YEAR,
    DOLLAR_WINDOW_DAYS,
    DRIVER_CURVES,
    PROFESSIONS,
    REFERENCE_RATES,
    REFERENCE_WELFARE_SPENDING,
    IncomeDriver,
    LifeLevers,
    ProfessionRule,
    RealRaise,
    StartingCapital,
    driver_factor,
    inheritance_rate,
    no_levers,
)

CENT = Decimal("0.01")

# Parte do crescimento real do PIB de 12 meses que entra no salário, além do IPCA
SALARY_GDP_SHARE = Decimal("0.5")


def no_growth(day: date) -> Decimal:
    return Decimal(0)


def never_in_government(day: date) -> bool:
    return False


def no_mechanic_state() -> MechanicState:
    return MechanicState()


def no_dollar_change(day: date) -> Decimal:
    return DRIVER_CURVES[IncomeDriver.DOLLAR].neutral


def parity_dollar(day: date) -> Decimal:
    return Decimal(1)


def neutral_unemployment_ratio(day: date) -> Decimal:
    return Decimal(1)


def neutral_selic(day: date) -> Decimal:
    return DRIVER_CURVES[IncomeDriver.SELIC].neutral


def neutral_stocks_return(day: date) -> Decimal:
    return DRIVER_CURVES[IncomeDriver.STOCKS].neutral


@dataclass(frozen=True)
class LifeBudget:
    """
    Renda e despesa mensais de uma profissão na partida. A renda é o salário do host
    vezes o múltiplo da profissão (a de carteira vale 1). Com `inflation_adjusted`, a
    despesa sobe pelo IPCA acumulado em 12 meses a cada aniversário da data de início e
    a meta sobe junto; a renda sobe pelo IPCA mais o reajuste real da profissão (a de
    carteira ganha `SALARY_GDP_SHARE` do crescimento do PIB de 12 meses, que na recessão
    não soma nada). A meta e os imprevistos são os mesmos para toda profissão; a despesa
    paga todo mês é a cheia menos o desconto da tarifa social, que só o Auxílio tem.
    """

    monthly_salary: Decimal
    monthly_expense: Decimal
    # Fração do patrimônio retirada por ano (0.04 = regra dos 4%)
    withdrawal_rate: Decimal
    inflation_adjusted: bool
    start_date: date
    # Crescimento do PIB de 12 meses da partida em cada dia, em fração (0.031)
    growth_on: Callable[[date], Decimal] = no_growth
    # A variação do dólar em 12 meses, a SELIC ao ano e o retorno do Ibovespa em 12
    # meses da partida em cada dia, em fração; o padrão é o valor neutro de cada curva
    dollar_change_on: Callable[[date], Decimal] = no_dollar_change
    # O dólar da partida em reais em cada dia; a trava de câmbio compara o dólar travado com o de 12 meses antes
    dollar_on: Callable[[date], Decimal] = parity_dollar
    selic_on: Callable[[date], Decimal] = neutral_selic
    stocks_return_on: Callable[[date], Decimal] = neutral_stocks_return
    # O desemprego da partida sobre o neutro em cada dia; os clientes do Autônomo perdem com ele
    unemployment_ratio_on: Callable[[date], Decimal] = neutral_unemployment_ratio
    profession: Profession = Profession.CLT
    # As medidas do governo que valem em cada dia; sem governo, o país padrão
    levers_on: Callable[[date], LifeLevers] = no_levers
    # No cargo de presidente a renda é este múltiplo do salário do host, no lugar da
    # renda da profissão, e nenhum sorteio de demissão a alcança
    presidency_multiple: Decimal | None = None
    # Se o partido escolhido pelo jogador está no governo no dia; lido por quem tem renda
    # presa ao partido (`outside_multiple` da profissão)
    in_government_on: Callable[[date], bool] = never_in_government
    # O estado da mecânica da profissão do jogador, lido a cada cálculo da renda
    current_mechanic_state: Callable[[], MechanicState] = no_mechanic_state

    @classmethod
    def of(
        cls,
        settings: SimulationSettingsDTO,
        growth_on: Callable[[date], Decimal] = no_growth,
        levers_on: Callable[[date], LifeLevers] = no_levers,
        dollar_change_on: Callable[[date], Decimal] = no_dollar_change,
        selic_on: Callable[[date], Decimal] = neutral_selic,
        stocks_return_on: Callable[[date], Decimal] = neutral_stocks_return,
        dollar_on: Callable[[date], Decimal] = parity_dollar,
        unemployment_ratio_on: Callable[[date], Decimal] = neutral_unemployment_ratio,
    ) -> "LifeBudget":
        return cls(
            monthly_salary=settings.monthly_salary,
            monthly_expense=settings.monthly_expense,
            withdrawal_rate=settings.withdrawal_rate,
            inflation_adjusted=settings.inflation_adjusted,
            start_date=settings.start_date,
            growth_on=growth_on,
            levers_on=levers_on,
            dollar_change_on=dollar_change_on,
            selic_on=selic_on,
            stocks_return_on=stocks_return_on,
            dollar_on=dollar_on,
            unemployment_ratio_on=unemployment_ratio_on,
        )

    def for_profession(self, profession: Profession) -> "LifeBudget":
        return replace(self, profession=profession)

    def with_party(self, in_government_on: Callable[[date], bool]) -> "LifeBudget":
        """O orçamento de quem escolheu um partido: a renda acompanha se ele está no governo."""
        return replace(self, in_government_on=in_government_on)

    def with_mechanic_state(
        self, current_mechanic_state: Callable[[], MechanicState]
    ) -> "LifeBudget":
        """O orçamento de quem tem mecânica na profissão: a renda acompanha o estado dela."""
        return replace(self, current_mechanic_state=current_mechanic_state)

    def as_president(self, multiple: Decimal) -> "LifeBudget":
        """O orçamento de quem recebe `multiple` salários do host pela presidência; reajuste e imposto seguem os da profissão."""
        return replace(self, presidency_multiple=multiple)

    @property
    def rule(self) -> ProfessionRule:
        return PROFESSIONS[self.profession]

    @property
    def health_multiple(self) -> Decimal:
        """Quantas vezes o imprevisto de saúde pesa: o da profissão vezes o do estado da mecânica."""
        return self.rule.health_multiple * self.current_mechanic_state().health_factor

    def income_parts(self, day: date) -> tuple[Decimal, Decimal]:
        """A renda bruta do mês em duas partes: a que a demissão sorteada tira e a que fica."""
        rule = self.rule
        factor = self._salary_factor(day)
        if self.presidency_multiple is not None:
            return Decimal(0), cents(
                self.monthly_salary * self.presidency_multiple * factor
            )
        mechanic = self.current_mechanic_state().income_factor
        freelancer = self.freelancer_state()
        if freelancer is None:
            exposed = self.monthly_salary * self.multiple_on(day) * factor * mechanic
        else:
            exposed = self.price_on(day) * self.clients_on(day)
        if rule.driver is not None:
            exposed *= self.driver_factor_on(day)
        benefit = (
            self.monthly_salary
            * rule.benefit_multiple
            * factor
            * self.levers_on(day).welfare_spending
            / REFERENCE_WELFARE_SPENDING
        )
        return cents(exposed), cents(benefit)

    def multiple_on(self, day: date) -> Decimal:
        """O múltiplo do salário do host que a profissão rende no dia: o da carreira sobe em linha reta desde o início da partida."""
        rule = self.rule
        career = rule.career
        if rule.outside_multiple is not None and not self.in_government_on(day):
            return rule.outside_multiple
        if career is None:
            return rule.income_multiple
        progress = career.progress((day - self.start_date).days)
        return rule.income_multiple + progress * (
            career.final_multiple - rule.income_multiple
        )

    def layoff_weight_on(self, day: date, deviation: Decimal | None = None) -> Decimal:
        """
        Quantas vezes a chance de demissão da sala pesa para a profissão no dia; 1 sem
        carreira. O Autônomo pesa pelo desvio do preço: o salvo, ou o `deviation` dado.
        """
        weight = Decimal(1)
        career = self.rule.career
        if career is not None:
            progress = career.progress((day - self.start_date).days)
            weight = career.layoff_weight - progress * (career.layoff_weight - 1)
        if self.freelancer_state() is not None:
            if deviation is None:
                deviation = self.price_deviation_on(day)
            weight *= empty_month_weight(deviation)
        return weight

    def driver_value_on(self, day: date) -> Decimal | None:
        """O valor da variável que move a renda da profissão no dia; nulo sem variável."""
        match self.rule.driver:
            case IncomeDriver.GDP:
                return self.growth_on(day)
            case IncomeDriver.DOLLAR:
                return self.dollar_change_on(day)
            case IncomeDriver.SELIC:
                return self.selic_on(day)
            case IncomeDriver.STOCKS:
                return self.stocks_return_on(day)
            case None:
                return None

    def freelancer_state(self) -> FreelancerState | None:
        """O estado do Autônomo, com o preço que move a renda; nulo para as demais profissões."""
        if self.profession is not Profession.FREELANCER:
            return None
        state = self.current_mechanic_state()
        return state if isinstance(state, FreelancerState) else FreelancerState()

    def converted_income_on(self, day: date) -> Decimal:
        """
        A renda vitalícia que o Aposentado converteu da previdência, no dia: cada parcela
        fica no valor de quando foi convertida, e a sala com correção a sobe pelo IPCA todo
        mês. Fica fora do imposto, do reajuste e da perda de renda; zero nas demais profissões.
        """
        if self.profession is not Profession.RETIREE:
            return Decimal(0)
        state = self.current_mechanic_state()
        if not isinstance(state, RetireeState):
            return Decimal(0)
        return cents(
            sum(
                (
                    part.income * self._conversion_factor(part.converted_on, day)
                    for part in state.conversions
                ),
                Decimal(0),
            )
        )

    def _conversion_factor(self, converted_on: date, day: date) -> Decimal:
        if not self.inflation_adjusted:
            return Decimal(1)
        return monthly_inflation_factor(converted_on, day)

    def reference_price_on(self, day: date) -> Decimal:
        """
        A referência do mercado do Autônomo no dia: a renda base do mês dividida pelos
        clientes da referência na data de início, corrida pelo IPCA mês a mês.
        """
        base = self.monthly_salary * self.rule.income_multiple / REFERENCE_CLIENTS
        if not self.inflation_adjusted:
            return base
        return base * monthly_inflation_factor(self.start_date, day)

    def price_on(self, day: date) -> Decimal:
        """O preço por atendimento do Autônomo; sem preço salvo vale a referência da data de início."""
        state = self.freelancer_state()
        if state is None or state.price is None:
            return self.reference_price_on(self.start_date)
        return state.price

    def price_deviation_on(self, day: date) -> Decimal:
        """O preço do Autônomo sobre a referência do dia, menos 1: positivo é preço acima do mercado."""
        return self.price_on(day) / self.reference_price_on(day) - 1

    def clients_on(self, day: date) -> Decimal:
        """Os clientes do Autônomo no mês, pela curva do preço e pelo desemprego do dia; fracionários."""
        return clients_on(self.price_deviation_on(day), self.unemployment_ratio_on(day))

    def price_range_on(self, day: date) -> tuple[Decimal, Decimal]:
        """O menor e o maior preço que o Autônomo pode salvar no dia, em centavos."""
        return price_range(self.reference_price_on(day))

    def exporter_state(self) -> ExporterState | None:
        """O estado do Exportador, com o mix e a trava que movem a renda; nulo para as demais profissões."""
        state = self.current_mechanic_state()
        return state if isinstance(state, ExporterState) else None

    def gdp_factor_on(self, day: date) -> Decimal:
        """O fator que o PIB de 12 meses põe na renda do dia."""
        return driver_factor(DRIVER_CURVES[IncomeDriver.GDP], self.growth_on(day))

    def free_dollar_factor_on(self, day: date) -> Decimal:
        """O fator que o dólar do dia põe na renda, sem trava."""
        return driver_factor(
            DRIVER_CURVES[IncomeDriver.DOLLAR], self.dollar_change_on(day)
        )

    def locked_dollar_factor_on(self, lock: ExchangeLock, day: date) -> Decimal:
        """O fator da mesma curva com o dólar travado no lugar do dólar do dia: variação = dólar travado ÷ dólar de 365 dias antes menos 1."""
        before = self.dollar_on(day - timedelta(days=DOLLAR_WINDOW_DAYS))
        return driver_factor(
            DRIVER_CURVES[IncomeDriver.DOLLAR], lock.locked_dollar / before - 1
        )

    def dollar_factor_on(self, day: date) -> Decimal:
        """O fator da receita exportada: a parte travada usa o dólar travado e a solta o dólar do dia."""
        free = self.free_dollar_factor_on(day)
        exporter = self.exporter_state()
        lock = None if exporter is None else exporter.lock
        if lock is None:
            return free
        return (
            lock.share * self.locked_dollar_factor_on(lock, day)
            + (1 - lock.share) * free
        )

    def lock_gain_on(self, day: date) -> Decimal:
        """
        O que a trava rende no mês: a renda da parte travada com o dólar travado menos a
        que ela daria com o dólar do dia, depois do imposto; zero sem trava.
        """
        exporter = self.exporter_state()
        if (
            exporter is None
            or exporter.lock is None
            or self.presidency_multiple is not None
        ):
            return Decimal(0)
        lock = exporter.lock
        base = self.monthly_salary * self.multiple_on(day) * self._salary_factor(day)
        difference = self.locked_dollar_factor_on(
            lock, day
        ) - self.free_dollar_factor_on(day)
        gain = base * exporter.export_share * lock.share * difference
        return cents(gain * (1 - self.tax_deviation_on(day)))

    def driver_factor_on(self, day: date) -> Decimal:
        """O fator que a variável da profissão põe na renda do dia; 1 sem variável. O Exportador pondera o dólar (com a trava) e o PIB pelo mix."""
        driver = self.rule.driver
        exporter = self.exporter_state()
        if exporter is not None and driver is IncomeDriver.DOLLAR:
            share = exporter.export_share
            return share * self.dollar_factor_on(day) + (
                1 - share
            ) * self.gdp_factor_on(day)
        value = self.driver_value_on(day)
        if driver is None or value is None:
            return Decimal(1)
        return driver_factor(DRIVER_CURVES[driver], value)

    def starting_capital(
        self, room_cash: Decimal, joined: date, end_date: date
    ) -> Decimal:
        """
        O caixa com que o jogador entra em `joined`: o da sala, o da sala mais a herança
        (o valor presente dos salários que faltam até `end_date`, à taxa de herança do modo da sala) ou zero.
        """
        match self.rule.starting_capital:
            case StartingCapital.ROOM:
                return room_cash
            case StartingCapital.ZERO:
                return Decimal(0)
            case StartingCapital.ROOM_PLUS_INHERITANCE:
                years = Decimal(max((end_date - joined).days, 0)) / DAYS_PER_YEAR
                rate = inheritance_rate(self.inflation_adjusted)
                annuity = (1 - (1 + rate) ** -years) / rate
                return room_cash + cents(
                    self.monthly_salary * MONTHS_PER_YEAR * annuity
                )

    def salary_on(self, day: date) -> Decimal:
        """A renda bruta do mês, antes do imposto."""
        return sum(self.income_parts(day), Decimal(0))

    def exposed_net_on(self, day: date) -> Decimal:
        """A parte exposta da renda do mês depois do imposto da profissão: o bico do Auxílio, sem o benefício."""
        exposed, _ = self.income_parts(day)
        return cents(exposed * (1 - self.tax_deviation_on(day)))

    def net_salary_on(self, day: date, income_lost: bool = False) -> Decimal:
        """
        A renda do mês depois do imposto da profissão: o desvio da alíquota em vigor
        contra a da lei corta a renda (alíquota abaixo dela soma). Com `income_lost`, a
        demissão sorteada tira a parte exposta, se a profissão está exposta a ela. A renda
        vitalícia convertida da previdência soma por fora, sem imposto.
        """
        exposed, protected = self.income_parts(day)
        kept = protected if income_lost and self.rule.loss else exposed + protected
        return cents(
            kept * (1 - self.tax_deviation_on(day))
        ) + self.converted_income_on(day)

    def income_loss(self) -> IncomeLoss | None:
        return None if self.presidency_multiple is not None else self.rule.loss

    def tax_rate_on(self, day: date) -> Decimal:
        """A alíquota em vigor do imposto que mexe na renda da profissão."""
        return self.levers_on(day).rate_of(self.rule.tax)

    def tax_reference(self) -> Decimal:
        return REFERENCE_RATES[self.rule.tax]

    def tax_deviation_on(self, day: date) -> Decimal:
        return self.tax_rate_on(day) - self.tax_reference()

    def salary_raise_inputs(self, anniversary: date) -> tuple[Decimal, Decimal]:
        """O IPCA de 12 meses e o crescimento do PIB de 12 meses que reajustam o salário no aniversário."""
        return (
            annual_index_rate(IndicatorSeries.IPCA, anniversary),
            self.growth_on(anniversary),
        )

    def real_raise_on(self, anniversary: date) -> Decimal:
        """O reajuste acima do IPCA que a profissão ganha no aniversário."""
        source = self.rule.real_raise
        if source is RealRaise.GDP_SHARE:
            return SALARY_GDP_SHARE * max(self.growth_on(anniversary), Decimal(0))
        return self.levers_on(anniversary).real_raise_of(source)

    def expense_on(self, day: date) -> Decimal:
        """A despesa cheia do mês, que a meta e os imprevistos usam."""
        return cents(self.monthly_expense * self._inflation_factor(day))

    def paid_expense_on(self, day: date) -> Decimal:
        """A despesa que o jogador paga no mês: a cheia menos o desconto da tarifa social da profissão."""
        return cents(self.expense_on(day) * (1 - self.rule.expense_discount))

    def readjustments(self, until: date) -> list[date]:
        """Os dias em que renda, despesa e meta sobem: o início e, com IPCA, cada aniversário."""
        if not self.inflation_adjusted:
            return [self.start_date]
        return [self.start_date, *anniversaries(self.start_date, until)]

    def goal_on(self, day: date) -> Decimal:
        """O patrimônio que paga a despesa do ano retirando `withdrawal_rate` dele."""
        return MONTHS_PER_YEAR * self.expense_on(day) / self.withdrawal_rate

    def _inflation_factor(self, day: date) -> Decimal:
        if not self.inflation_adjusted:
            return Decimal(1)
        return inflation_factor(self.start_date, day)

    def _salary_factor(self, day: date) -> Decimal:
        if not self.inflation_adjusted or not self.rule.inflation_indexed:
            return Decimal(1)
        factor = Decimal(1)
        for anniversary in anniversaries(self.start_date, day):
            ipca = annual_index_rate(IndicatorSeries.IPCA, anniversary)
            factor *= 1 + ipca + self.real_raise_on(anniversary)
        return factor


def cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)
