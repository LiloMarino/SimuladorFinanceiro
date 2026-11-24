"""Renda e despesa mensais da partida e a meta do viver de renda que sai delas."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import ROUND_HALF_EVEN, Decimal

from backend.core.dates import add_months
from backend.core.dto.profession import (
    AdministratorState,
    BrokerState,
    ExchangeLock,
    ExporterState,
    FreelancerState,
    GraduateState,
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
from backend.core.house_report import Commission, commission
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


def no_rent_data(day: date) -> Decimal | None:
    return None


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
    # A variação do dólar em 12 meses e a SELIC ao ano da partida em cada dia, em fração;
    # o padrão é o valor neutro de cada curva
    dollar_change_on: Callable[[date], Decimal] = no_dollar_change
    # O dólar da partida em reais em cada dia; a trava de câmbio compara o dólar travado com o de 12 meses antes
    dollar_on: Callable[[date], Decimal] = parity_dollar
    selic_on: Callable[[date], Decimal] = neutral_selic
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
    # O dia em que o jogador entrou na profissão; a carreira e a casa dos pais contam daqui. Nulo é o início da partida
    profession_start: date | None = None
    # A soma dos aluguéis dos imóveis alugados do Locador em cada dia; nula (orçamento sem os imóveis do jogador) vale o aluguel dos imóveis iniciais
    rented_income_on: Callable[[date], Decimal | None] = no_rent_data

    @classmethod
    def of(
        cls,
        settings: SimulationSettingsDTO,
        growth_on: Callable[[date], Decimal] = no_growth,
        levers_on: Callable[[date], LifeLevers] = no_levers,
        dollar_change_on: Callable[[date], Decimal] = no_dollar_change,
        selic_on: Callable[[date], Decimal] = neutral_selic,
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

    def with_profession_start(self, profession_start: date) -> "LifeBudget":
        """O orçamento de quem entrou na profissão em `profession_start`: carreira e casa dos pais contam desse dia."""
        return replace(self, profession_start=profession_start)

    def with_rented_income(
        self, rented_income_on: Callable[[date], Decimal | None]
    ) -> "LifeBudget":
        """O orçamento do Locador: a renda é a soma dos aluguéis dos imóveis alugados."""
        return replace(self, rented_income_on=rented_income_on)

    def as_president(self, multiple: Decimal) -> "LifeBudget":
        """O orçamento de quem recebe `multiple` salários do host pela presidência; reajuste e imposto seguem os da profissão."""
        return replace(self, presidency_multiple=multiple)

    def administrator_state(self) -> AdministratorState | None:
        """O estado do Administrador, com o setor e a experiência; nulo para as demais profissões. Sem estado salvo vale o inicial."""
        if self.profession is not Profession.ADMINISTRATOR:
            return None
        state = self.current_mechanic_state()
        return state if isinstance(state, AdministratorState) else AdministratorState()

    @property
    def worked_profession(self) -> Profession:
        """A profissão cuja regra rende a renda: a própria, ou o setor onde o Administrador trabalha."""
        state = self.administrator_state()
        return self.profession if state is None else state.sector

    @property
    def base_rule(self) -> ProfessionRule:
        """A regra da profissão trabalhada, sem a experiência."""
        return PROFESSIONS[self.worked_profession]

    @property
    def experience_factor(self) -> Decimal:
        """O quanto da renda do setor o Administrador leva pela experiência; 1 nas demais profissões."""
        state = self.administrator_state()
        return Decimal(1) if state is None else state.experience_factor

    @property
    def rule(self) -> ProfessionRule:
        """A regra efetiva da renda: a da profissão trabalhada, com o múltiplo vezes a experiência do Administrador."""
        base = self.base_rule
        if self.administrator_state() is None:
            return base
        return replace(
            base, income_multiple=base.income_multiple * self.experience_factor
        )

    def sector_income_on(self, sector: Profession, day: date) -> Decimal:
        """
        O que o setor pagaria hoje ao Administrador, líquido, com a experiência que ele
        tem nele e sem troca nem estudo em andamento. Quem está fora do setor Corretor
        entra na divisão da comissão com mais um.
        """
        state = self.administrator_state()
        if state is None:
            return self.net_salary_on(day)
        brokers = state.brokers + (1 if state.sector is not Profession.BROKER else 0)
        hypothetical = state.model_copy(
            update={
                "sector": sector,
                "switching_to": None,
                "switch_started_on": None,
                "exam_enrolled_on": None,
                "brokers": brokers,
            }
        )
        return replace(self, current_mechanic_state=lambda: hypothetical).net_salary_on(
            day
        )

    @property
    def career_start(self) -> date:
        """O dia em que a carreira da profissão começa a contar: a entrada nela, ou o início da partida."""
        return self.profession_start or self.start_date

    @property
    def career_end(self) -> date:
        """O dia em que a curva inicial da carreira chega ao múltiplo final; sem carreira, o próprio início."""
        career = self.rule.career
        if career is None:
            return self.career_start
        return add_months(self.career_start, career.years * MONTHS_PER_YEAR)

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
        stipend = self.stipend_on(day)
        if stipend is not None:
            return stipend, self._benefit_on(day)
        mechanic = self.current_mechanic_state().income_factor
        if self.profession is Profession.LANDLORD:
            rent = self.rented_income_on(day)
            if rent is None:
                rent = cents(self.monthly_salary * rule.income_multiple)
            return rent, self._benefit_on(day)
        if self.worked_profession is Profession.FREELANCER:
            exposed = (
                self.price_on(day)
                * self.clients_on(day)
                * self.experience_factor
                * mechanic
            )
        else:
            exposed = self.monthly_salary * self.multiple_on(day) * factor * mechanic
        if rule.driver is not None:
            exposed *= self.driver_factor_on(day)
        exposed += self.broker_commission_on(day).amount * mechanic
        return cents(exposed), self._benefit_on(day)

    def _benefit_on(self, day: date) -> Decimal:
        """O benefício do mês, a parte da renda que a demissão não tira."""
        return cents(
            self.monthly_salary
            * self.rule.benefit_multiple
            * self._salary_factor(day)
            * self.levers_on(day).welfare_spending
            / REFERENCE_WELFARE_SPENDING
        )

    def base_income_on(self, day: date) -> Decimal:
        """A renda base do mês: o salário do host reajustado, antes do múltiplo da profissão."""
        return self.monthly_salary * self._salary_factor(day)

    def graduate_state(self) -> GraduateState | None:
        """O estado do Recém-formado, com a escada e a casa dos pais; nulo para as demais profissões. Sem estado salvo vale o inicial."""
        if self.profession is not Profession.NEW_GRADUATE:
            return None
        state = self.current_mechanic_state()
        return state if isinstance(state, GraduateState) else GraduateState()

    def stipend_on(self, day: date) -> Decimal | None:
        """A bolsa que o mestrado ou o doutorado em curso paga no lugar do salário; nula fora deles."""
        state = self.graduate_state()
        if state is None or self.presidency_multiple is not None:
            return None
        stipend = state.stipend_on(self.base_income_on(day))
        return None if stipend is None else cents(stipend)

    def tuition_on(self, day: date) -> Decimal:
        """A mensalidade da especialização em curso no mês; zero fora dela."""
        state = self.graduate_state()
        if state is None:
            return Decimal(0)
        return state.tuition_on(self.base_income_on(day))

    def fixed_income_on(self, day: date) -> Decimal:
        """A parte fixa do salário do mês: o salário do host vezes o múltiplo da profissão, reajustado, sem mecânica nem variável."""
        return cents(
            self.monthly_salary * self.multiple_on(day) * self._salary_factor(day)
        )

    def broker_commission_on(self, day: date) -> Commission:
        """A comissão do Corretor no mês, bruta: a do volume que a virada do mês guardou, até o teto sobre a parte fixa; vale para o Corretor e para o Administrador no setor Corretor, e é zero nas demais profissões."""
        state = self.current_mechanic_state()
        if (
            self.worked_profession is not Profession.BROKER
            or self.presidency_multiple is not None
            or not isinstance(state, BrokerState | AdministratorState)
        ):
            return Commission(Decimal(0), Decimal(0))
        return commission(state.volume, state.brokers, self.fixed_income_on(day))

    def broker_commission_net_on(self, day: date) -> Decimal:
        """A comissão do Corretor depois do imposto da profissão."""
        return cents(
            self.broker_commission_on(day).amount * (1 - self.tax_deviation_on(day))
        )

    def multiple_on(self, day: date) -> Decimal:
        """O múltiplo do salário do host que a profissão rende no dia: o da carreira sobe em linha reta desde a entrada na profissão, e cada degrau concluído da escada acadêmica abre um trecho novo."""
        rule = self.rule
        career = rule.career
        if rule.outside_multiple is not None and not self.in_government_on(day):
            return rule.outside_multiple
        if career is None:
            return rule.income_multiple
        state = self.graduate_state()
        segment = None if state is None else state.segment_on(day)
        if segment is not None:
            return segment.multiple_on(day)
        progress = career.progress((day - self.career_start).days)
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
            progress = career.progress((day - self.career_start).days)
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
        base = self.monthly_salary * self.base_rule.income_multiple / REFERENCE_CLIENTS
        if not self.inflation_adjusted:
            return base
        return base * monthly_inflation_factor(self.start_date, day)

    def price_on(self, day: date) -> Decimal:
        """O preço por atendimento do Autônomo; sem preço salvo vale a referência da data de início. O Administrador no setor Autônomo cobra a referência do dia."""
        if self.administrator_state() is not None:
            return self.reference_price_on(day)
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
        return cents(exposed * (1 - self._taxed_deviation_on(day)))

    def net_salary_on(self, day: date, income_lost: bool = False) -> Decimal:
        """
        A renda do mês depois do imposto da profissão: o desvio da alíquota em vigor
        contra a da lei corta a renda (alíquota abaixo dela soma). Com `income_lost`, a
        demissão sorteada tira a parte exposta, se a profissão está exposta a ela. A renda
        vitalícia convertida da previdência soma por fora, sem imposto.
        """
        exposed, protected = self.income_parts(day)
        kept = protected if income_lost and self.income_loss() else exposed + protected
        return cents(
            kept * (1 - self._taxed_deviation_on(day))
        ) + self.converted_income_on(day)

    def income_loss(self) -> IncomeLoss | None:
        """O que a demissão sorteada faz com a renda; a bolsa do mestrado e do doutorado não é demitida."""
        state = self.graduate_state()
        if self.presidency_multiple is not None or (
            state is not None and state.stipend_step is not None
        ):
            return None
        return self.rule.loss

    def _taxed_deviation_on(self, day: date) -> Decimal:
        """O desvio de imposto que corta a renda do mês; a bolsa é isenta."""
        if self.stipend_on(day) is not None:
            return Decimal(0)
        return self.tax_deviation_on(day)

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

    def expense_discount_on(self, day: date) -> Decimal:
        """O desconto sobre a despesa paga no dia: o da tarifa social da profissão e o da casa dos pais."""
        state = self.graduate_state()
        home = (
            Decimal(0)
            if state is None
            else state.home_discount_on(self.career_start, day)
        )
        return self.rule.expense_discount + home

    def paid_expense_on(self, day: date) -> Decimal:
        """A despesa que o jogador paga no mês: a cheia menos os descontos do dia, mais a mensalidade do curso em andamento."""
        return cents(
            self.expense_on(day) * (1 - self.expense_discount_on(day))
            + self.tuition_on(day)
        )

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
