"""O livro das estatais da partida: as empresas, os meses das fundadas e o efeito das ordens no IPCA."""

import calendar
import logging
import random
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from backend.core import repository
from backend.core.dates import add_months
from backend.core.dto.corporate_event import CorporateEventDTO
from backend.core.dto.state_company import StateCompanyDTO, StateCompanyMonthDTO
from backend.core.enum import (
    CorporateEventKind,
    DividendPolicy,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateControl,
    StateLever,
    StateMonthReason,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import (
    last_day_of_month,
    next_business_day,
    required,
    subtract_months,
)
from backend.features.market_maker.sessions import window_end
from backend.features.state_companies import (
    fair_value,
    gdp,
    levers,
    payout,
    price,
)
from backend.features.state_companies.orders import StateOrder

logger = logging.getLogger(__name__)

# Fatia do governo na estatal que ele funda; o resto fica com o formador de mercado
FOUNDING_GOVERNMENT_SHARE = Decimal("0.51")

# Preço de lançamento da ação fundada, em reais: o porte dividido por ele dá o número de ações
FOUNDING_PRICE = Decimal(10)

BILLION = Decimal(10) ** 9

# O código da ação da estatal: quatro letras e um número, como PNOV3
TICKER_PATTERN = re.compile(r"[A-Z]{4}[0-9]")

# A oferta de privatização vale por cinco pregões, contando o da abertura
PRIVATIZATION_SESSIONS = 5

CENT = Decimal("0.01")

type OrderHistory = Callable[[], Mapping[date, Mapping[str, StateOrder]]]

# O preço de mercado da ação importada no dia; None quando ela não tem preço
type MarketPrice = Callable[[str], Decimal | None]

# O crescimento do PIB do último mês fechado antes do dia menos a tendência, em fração ao ano
type GrowthGap = Callable[[date], Decimal]


def no_growth_gap(_day: date) -> Decimal:
    return Decimal(0)


class OfferAccounts(Protocol):
    """As contas que a oferta de privatização move, pela carteira: o caixa e a entrega das ações."""

    def cash(self, portfolio_id: int) -> Decimal:
        """O caixa da conta; zero quando a conta não é mais da partida."""
        ...

    def deliver(
        self, portfolio_id: int, ticker: str, shares: int, price: Decimal
    ) -> None:
        """Debita `shares` x `price` do caixa da conta e abre a posição dela."""
        ...


@dataclass(frozen=True)
class PrivatizationResult:
    """O fechamento da oferta: o preço, as ações de cada carteira, a sobra e o que o governo recebeu."""

    price: Decimal
    delivered: Mapping[int, int]
    leftover: int
    proceeds: Decimal


def invested_by(size: StateCompanySize) -> Decimal:
    """O capital que a fundação põe na empresa, em reais, pelo porte."""
    return Decimal(size.billions) * BILLION


def government_shares(company: StateCompanyDTO) -> int:
    return int(company.shares * company.government_share)


def maker_shares(company: StateCompanyDTO) -> int:
    """As ações do formador de mercado: as que o governo não tem."""
    return company.shares - government_shares(company)


def _month_start(day: date) -> date:
    return day.replace(day=1)


def _effect_month(day: date) -> date:
    """O primeiro dia do mês do orçamento em que o fato do dia entra: o do dia, ou o seguinte se o dia é o último."""
    return _month_start(day + timedelta(days=1))


def _next_month(month: date) -> date:
    return date(month.year + month.month // 12, month.month % 12 + 1, 1)


def _months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def _month_fraction(day: date) -> float:
    """Quanto do mês já correu no início do dia: 0 no dia 1, perto de 1 no último dia."""
    return (day.day - 1) / calendar.monthrange(day.year, day.month)[1]


class StateCompanyBook:
    """
    As estatais da partida ficam em memória e cada mudança passa pelo repositório. As
    ordens do presidente vêm do histórico do governo: `history` devolve, por mês de
    início da vigência, as ordens que valem desde então.
    """

    def __init__(
        self,
        simulation_id: int,
        random_seed: int,
        history: OrderHistory,
        companies: Iterable[StateCompanyDTO] = (),
        market_price: MarketPrice = lambda _ticker: None,
        growth_gap: GrowthGap = no_growth_gap,
    ):
        """
        `market_price` dá o preço do dia da ação importada, que é o da privatização dela.
        `growth_gap` dá o quanto o PIB cresce acima da tendência no último mês fechado
        antes do dia: o valor justo de cada mês da fundada usa o do mês anterior a ele.
        """
        self._simulation_id = simulation_id
        self._seed = random_seed
        self._history = history
        self._market_price = market_price
        self._growth_gap = growth_gap
        self._companies: dict[str, StateCompanyDTO] = {c.ticker: c for c in companies}

    # Empresas

    def companies(self) -> list[StateCompanyDTO]:
        return list(self._companies.values())

    def company(self, ticker: str) -> StateCompanyDTO | None:
        return self._companies.get(ticker)

    def state_tickers(self) -> set[str]:
        """Os papéis que o governo ainda controla: a privatizada já é uma empresa comum."""
        return {
            company.ticker
            for company in self._companies.values()
            if company.status is not StateCompanyStatus.PRIVATIZED
        }

    def is_founded(self, ticker: str) -> bool:
        """A ação é de uma estatal fundada na partida: preço e provento próprios, fora da bolsa."""
        company = self._companies.get(ticker)
        return company is not None and company.origin is StateCompanyOrigin.FOUNDED

    def ticker_free(self, ticker: str) -> bool:
        """O código é livre quando nenhuma estatal da partida o usa e as letras são de ninguém."""
        if ticker in self._companies:
            return False
        return not repository.state_company.letters_taken(ticker)

    def found(
        self,
        *,
        ticker: str,
        name: str,
        size: StateCompanySize,
        lever: StateLever | None,
        real_interest: Decimal,
        today: date,
    ) -> StateCompanyDTO | None:
        """
        Cria a ação (STOCK) e a estatal ativa: o governo com 51% e o formador com o resto.
        O retorno médio do valor justo parte do juro real histórico do dia da fundação.
        Devolve None quando as letras do código já são de outro ativo.
        """
        stock = repository.state_company.claim_stock(ticker, name)
        if stock is None:
            logger.warning("Fundação de %s sem ticker livre", ticker)
            return None
        invested = invested_by(size)
        company = repository.state_company.insert_founded(
            simulation_id=self._simulation_id,
            stock_id=stock.id,
            ticker=ticker,
            government_share=FOUNDING_GOVERNMENT_SHARE,
            shares=int(invested / FOUNDING_PRICE),
            lever=lever,
            size=size,
            invested=invested,
            mean_return=fair_value.mean_annual_return(real_interest),
            seed=random.Random(f"{self._seed}:{ticker}").getrandbits(31),
            founded_on=today,
        )
        self._companies[ticker] = company
        return company

    def open_privatization(self, ticker: str, today: date) -> StateCompanyDTO:
        """A estatal passa à oferta de privatização, aberta no dia."""
        company = self._companies[ticker]
        repository.state_company.open_offer(company.id, today)
        opened = company.model_copy(
            update={
                "status": StateCompanyStatus.PRIVATIZING,
                "offer_opened_on": today,
            }
        )
        self._companies[ticker] = opened
        return opened

    def offer_ends_on(self, ticker: str) -> date | None:
        """O último pregão da oferta aberta da estatal; None sem oferta."""
        company = self._companies.get(ticker)
        if (
            company is None
            or company.status is not StateCompanyStatus.PRIVATIZING
            or company.offer_opened_on is None
        ):
            return None
        return window_end(company.offer_opened_on, PRIVATIZATION_SESSIONS)

    def reserve(
        self, ticker: str, portfolio_id: int, quantity: Decimal, today: date
    ) -> None:
        """
        A conta pede `quantity` ações na oferta, sem reservar caixa: cada chamada substitui
        o pedido anterior e o caixa só paga no fechamento.
        """
        company = self._companies.get(ticker)
        if company is None:
            raise NotFoundError("Estatal não encontrada.")
        ends_on = self.offer_ends_on(ticker)
        opened_on = company.offer_opened_on
        if ends_on is None or opened_on is None or not opened_on <= today <= ends_on:
            raise ConflictError("A oferta de privatização não está aberta.")
        if quantity <= 0 or quantity != quantity.to_integral_value():
            raise UnprocessableEntityError("Informe uma quantidade inteira de ações.")
        repository.state_company.save_reservation(
            company.id, portfolio_id, quantity, today
        )

    def offer_price(self, company: StateCompanyDTO, day: date) -> Decimal | None:
        """O preço por ação da oferta: o valor justo do dia na fundada, o preço de mercado na importada."""
        if company.origin is StateCompanyOrigin.FOUNDED:
            per_share = self.fair_value_on(company, day) / company.shares
        else:
            per_share = self._market_price(company.ticker)
        if per_share is None or per_share <= 0:
            return None
        return per_share.quantize(CENT, ROUND_HALF_UP)

    def close_privatization(
        self, ticker: str, today: date, accounts: OfferAccounts
    ) -> PrivatizationResult:
        """
        Fecha a oferta: as ações do governo vão aos pedidos pelo preço do dia. Com pedido
        acima da oferta cada conta recebe a parte proporcional; cada uma paga com o caixa
        que tem e leva só as ações inteiras que ele cobre. O governo recebe o preço da fatia
        inteira, vendida ou não, e a estatal passa a privatizada.
        """
        company = self._companies.get(ticker)
        if company is None or company.status is not StateCompanyStatus.PRIVATIZING:
            raise ConflictError("A estatal não está em oferta de privatização.")
        unit = self.offer_price(company, today)
        if unit is None:
            raise ConflictError("A estatal ainda não tem preço para a oferta.")
        offered = government_shares(company)
        requested = repository.state_company.reservations_of(company.id)
        demand = sum(requested.values(), Decimal(0))
        delivered: dict[int, int] = {}
        for portfolio_id, quantity in requested.items():
            share = quantity if demand <= offered else quantity * offered / demand
            affordable = max(accounts.cash(portfolio_id), Decimal(0)) // unit
            shares = int(min(share // 1, affordable))
            if shares > 0:
                accounts.deliver(portfolio_id, ticker, shares, unit)
                delivered[portfolio_id] = shares
        proceeds = unit * offered
        repository.state_company.mark_privatized(company.id, today, proceeds)
        self._companies[ticker] = company.model_copy(
            update={
                "status": StateCompanyStatus.PRIVATIZED,
                "privatized_on": today,
                "proceeds": proceeds,
            }
        )
        return PrivatizationResult(
            price=unit,
            delivered=delivered,
            leftover=offered - sum(delivered.values()),
            proceeds=proceeds,
        )

    def assets_in(self, month_end: date) -> Decimal:
        """O que as privatizações renderam ao Tesouro no mês, em reais; a venda do último dia do mês cai no seguinte."""
        return sum(
            (
                company.proceeds
                for company in self._companies.values()
                if company.privatized_on is not None
                and company.proceeds is not None
                and last_day_of_month(_effect_month(company.privatized_on)) == month_end
            ),
            Decimal(0),
        )

    # Mês

    def fair_value_after(
        self, company: StateCompanyDTO, months: int, through: date | None = None
    ) -> Decimal:
        """
        O valor justo da fundada depois de `months` meses; a importada segue a história. O
        crescimento de cada mês acompanha o porte efetivo da política em vigor nele; os
        meses depois de `through` seguem a política em vigor nesse dia. O mês de ordem m
        (o primeiro é o da fundação) usa o crescimento do PIB acima da tendência do último
        mês fechado antes dele.
        """
        if (
            company.origin is not StateCompanyOrigin.FOUNDED
            or company.seed is None
            or company.mean_return is None
        ):
            return Decimal(0)
        policies: list[DividendPolicy] = []
        growth_path: list[Decimal] = []
        if company.founded_on is not None:
            founded_month = _month_start(company.founded_on)
            first = _next_month(founded_month)
            policies = self._policies(
                company.ticker, first, add_months(first, months - 1), through
            )
            growth_path = [
                self._growth_gap(add_months(founded_month, month) - timedelta(days=1))
                for month in range(months)
            ]
        return fair_value.fair_value(
            company.invested,
            company.seed,
            company.mean_return,
            months,
            gdp.size_path(policies),
            growth_path,
        )

    def fair_value_on(self, company: StateCompanyDTO, day: date) -> Decimal:
        """
        O valor justo da fundada no dia: o de cada virada de mês, e entre elas cresce em
        fatores iguais ao dia. Na fundação vale o capital posto.
        """
        founded_on = company.founded_on
        if founded_on is None or day <= founded_on:
            return self.fair_value_after(company, 0)
        elapsed = (
            _months_between(founded_on, day)
            + _month_fraction(day)
            - _month_fraction(founded_on)
        )
        whole = int(elapsed)
        start = self.fair_value_after(company, whole, day)
        end = self.fair_value_after(company, whole + 1, day)
        if start <= 0:
            return start
        return start * Decimal(str(float(end / start) ** (elapsed - whole)))

    def _month_profit_missing(self, company: StateCompanyDTO, month: date) -> bool:
        """A fundada ainda não fechou um mês inteiro em `month`: é o da fundação."""
        return (
            company.founded_on is None or _months_between(company.founded_on, month) < 1
        )

    def _month_profit(self, company: StateCompanyDTO, month: date) -> Decimal | None:
        """O que o valor justo andou no mês; None enquanto a fundada não fechou um mês inteiro."""
        if self._month_profit_missing(company, month):
            return None
        months = _months_between(required(company.founded_on), month)
        return self.fair_value_after(company, months) - self.fair_value_after(
            company, months - 1
        )

    def _pays_dividends(self, company: StateCompanyDTO, month: date) -> bool:
        """A fundada que ainda é do governo no mês fecha o mês e paga dividendo."""
        if company.origin is not StateCompanyOrigin.FOUNDED:
            return False
        return company.privatized_on is None or month < _effect_month(
            company.privatized_on
        )

    def month_dividend(self, company: StateCompanyDTO, month: date) -> Decimal:
        """
        O dividendo total do mês, a todos os acionistas: o payout da política sobre o lucro
        que sobra do corte do controle, pelas ordens que valeram no mês.
        """
        profit = self._month_profit(company, month)
        if profit is None or not self._pays_dividends(company, month):
            return Decimal(0)
        order = self.orders(month).get(company.ticker, StateOrder())
        return payout.dividend(
            max(profit, Decimal(0)), order.dividend_policy, order.control
        )

    def month_reason(
        self, company: StateCompanyDTO, month: date, profit: Decimal | None
    ) -> StateMonthReason:
        """
        Por que o mês da fundada tem ou não dividendo, pela mesma decisão de `month_dividend`:
        sem lucro modelado é o mês da fundação, depois da venda é a privatização, com lucro
        não positivo é prejuízo e nos demais a política paga.
        """
        if self._month_profit_missing(company, month):
            return StateMonthReason.FOUNDING
        if not self._pays_dividends(company, month):
            return StateMonthReason.PRIVATIZED
        if profit is not None and profit <= 0:
            return StateMonthReason.LOSS
        return StateMonthReason.PAID

    def privatized_month(self, company: StateCompanyDTO) -> date | None:
        """O primeiro mês em que a estatal já não paga dividendo ao governo; None enquanto ela não foi vendida."""
        if company.privatized_on is None:
            return None
        return _effect_month(company.privatized_on)

    def _dividend_events(
        self, company: StateCompanyDTO, until: date
    ) -> list[CorporateEventDTO]:
        """Os dividendos e JCP da ação importada com data ex até `until`, na escala da história."""
        return [
            event
            for event in repository.corporate_event.get_for_stock(
                company.stock_id, until, self._simulation_id
            )
            if event.kind is CorporateEventKind.DIVIDEND
        ]

    def _imported_dividend(
        self, company: StateCompanyDTO, first: date, last: date, *, deviation: bool
    ) -> Decimal:
        """
        O que o Tesouro recebe da importada nas datas ex de `first` a `last`: o provento
        histórico por ação vezes o fator do dia da data ex vezes as ações do governo.
        Com `deviation`, só o que passa do histórico (fator menos 1): a receita do orçamento
        já traz o dividendo que a União recebeu na história, e depois da privatização o
        desvio é o histórico inteiro com o sinal trocado.
        """
        held = government_shares(company)
        total = Decimal(0)
        for event in self._dividend_events(company, last):
            if event.ex_date < first:
                continue
            if self._privatized_by(company, event.ex_date):
                factor = Decimal(0)
            else:
                factor = Decimal(
                    str(self.dividend_factor(company.ticker, event.ex_date))
                )
            scale = factor - 1 if deviation else factor
            total += Decimal(str(event.value)) * scale * held
        return total

    def _treasury_dividend(
        self, company: StateCompanyDTO, month: date, *, deviation: bool
    ) -> Decimal:
        """O dividendo do mês ao Tesouro: a fatia do governo na fundada, as datas ex do mês na importada."""
        start = _month_start(month)
        if company.origin is StateCompanyOrigin.FOUNDED:
            return self.month_dividend(company, start) * company.government_share
        return self._imported_dividend(
            company, start, last_day_of_month(start), deviation=deviation
        )

    def treasury_dividends(self, month: date) -> Decimal:
        """O total que o Tesouro recebe das estatais no mês de `month`, fundadas e importadas."""
        return sum(
            (
                self._treasury_dividend(company, month, deviation=False)
                for company in self._companies.values()
            ),
            Decimal(0),
        )

    def budget_dividends(self, month: date) -> Decimal:
        """
        O que as estatais somam à receita do orçamento no mês de `month`: a fundada inteira
        e, na importada, só o desvio do provento sobre o histórico.
        """
        return sum(
            (
                self._treasury_dividend(company, month, deviation=True)
                for company in self._companies.values()
            ),
            Decimal(0),
        )

    def imported_dividends_12m(self, company: StateCompanyDTO, today: date) -> Decimal:
        """O que o Tesouro recebeu da importada nos 12 meses fechados antes do mês de `today`."""
        this_month = _month_start(today)
        return self._imported_dividend(
            company,
            subtract_months(this_month, 12),
            this_month - timedelta(days=1),
            deviation=False,
        )

    def imported_dividend_per_share_12m(
        self, company: StateCompanyDTO, today: date
    ) -> Decimal:
        """O provento por ação da importada nos 12 meses fechados antes do mês de `today`, com o fator da ordem de cada data ex."""
        this_month = _month_start(today)
        first = subtract_months(this_month, 12)
        last = this_month - timedelta(days=1)
        return sum(
            (
                Decimal(str(event.value))
                * Decimal(str(self.dividend_factor(company.ticker, event.ex_date)))
                for event in self._dividend_events(company, last)
                if event.ex_date >= first
            ),
            Decimal(0),
        )

    def expected_imported_dividend(
        self, company: StateCompanyDTO, day: date, order: StateOrder
    ) -> Decimal:
        """
        O dividendo esperado por mês ao Tesouro na importada sob `order`: o provento
        histórico do mês de `day` (sem evento nele, a média mensal dos 12 meses anteriores)
        vezes o fator da ordem vezes as ações do governo.
        """
        if self._privatized_by(company, day):
            return Decimal(0)
        first = _month_start(day)
        events = self._dividend_events(company, last_day_of_month(day))
        in_month = [e for e in events if e.ex_date >= first]
        if in_month:
            per_share = sum((Decimal(str(e.value)) for e in in_month), Decimal(0))
        else:
            window_start = subtract_months(first, 12)
            per_share = sum(
                (Decimal(str(e.value)) for e in events if e.ex_date >= window_start),
                Decimal(0),
            ) / Decimal(12)
        return (
            per_share
            * Decimal(str(price.dividend_factor(order)))
            * government_shares(company)
        )

    def on_month(self, today: date) -> list[StateCompanyMonthDTO]:
        """
        Fecha o mês das estatais fundadas ainda do governo: o valor justo, o lucro (o que
        o valor justo andou no mês) e o dividendo que cabe ao Tesouro pela ordem em vigor.
        O dividendo vira evento da ação, pago por cota a todos os acionistas no pregão
        seguinte; a parte do governo chega ao Tesouro pela receita do orçamento.
        """
        month = _month_start(today)
        closed: list[StateCompanyMonthDTO] = []
        for company in self._companies.values():
            profit = self._month_profit(company, month)
            if profit is None or not self._pays_dividends(company, month):
                continue
            months = _months_between(required(company.founded_on), month)
            dividend = self.month_dividend(company, month)
            row = StateCompanyMonthDTO(
                state_company_id=company.id,
                month=month,
                fair_value=self.fair_value_after(company, months),
                profit=profit,
                treasury_dividend=dividend * company.government_share,
            )
            repository.state_company.save_month(row)
            if dividend > 0 and company.shares > 0:
                repository.corporate_event.save_dividend(
                    company.stock_id,
                    next_business_day(today),
                    float(dividend / company.shares),
                    self._simulation_id,
                )
            closed.append(row)
        return closed

    # Preço e provento da ação

    def _order_of(self, ticker: str, day: date) -> StateOrder | None:
        """A ordem em vigor na estatal importada e ainda do governo; None nas demais ações."""
        company = self._companies.get(ticker)
        if (
            company is None
            or company.origin is not StateCompanyOrigin.IMPORTED
            or self._privatized_by(company, day)
        ):
            return None
        return self.orders(day).get(ticker, StateOrder())

    def _privatized_by(self, company: StateCompanyDTO, day: date) -> bool:
        """A estatal já é privada no dia: a ordem e o controle de preço acabam com a venda."""
        return company.privatized_on is not None and day >= company.privatized_on

    def _policy_price_factor(self, ticker: str, day: date) -> float:
        """
        O efeito acumulado da política de dividendos no preço da importada, desde o primeiro
        mês com ordens: cada mês fechado entra inteiro e o mês do dia entra pela fração
        que já correu.
        """
        history = self._history()
        if not history:
            return 1.0
        this_month = _month_start(day)
        path = gdp.size_path(self._policies(ticker, min(history), this_month))
        closed = price.policy_price_factor(path[:-1])
        current = price.policy_price_factor(path[-1:])
        return closed * current ** _month_fraction(day)

    def price_factor(self, ticker: str, day: date) -> float:
        """O fator das ordens sobre o preço histórico da estatal importada: o controle e o histórico da política; 1 sem ordem."""
        order = self._order_of(ticker, day)
        if order is None:
            return 1.0
        return price.price_factor(order) * self._policy_price_factor(ticker, day)

    def dividend_factor(self, ticker: str, day: date) -> float:
        """O fator da ordem sobre o provento histórico da estatal importada; 1 sem ordem."""
        order = self._order_of(ticker, day)
        return 1.0 if order is None else price.dividend_factor(order)

    def founded_price_factor(self, ticker: str, day: date) -> float:
        """O fator do controle de preço sobre o valor justo por ação da estatal fundada; 1 sem ordem e depois da venda. A política de dividendos já está no valor justo."""
        company = self._companies.get(ticker)
        if company is not None and self._privatized_by(company, day):
            return 1.0
        return price.price_factor(self.orders(day).get(ticker, StateOrder()))

    # Ordens e IPCA

    def orders(self, day: date) -> Mapping[str, StateOrder]:
        """As ordens que valem no dia: as da última virada de mês que já chegou."""
        history = self._history()
        started = [month for month in history if month <= day]
        return history[max(started)] if started else {}

    def order_history(self) -> Mapping[date, Mapping[str, StateOrder]]:
        """As ordens de cada vigência, por mês de início."""
        return self._history()

    def latest_orders(self) -> Mapping[str, StateOrder]:
        """As ordens da vigência mais recente, mesmo a que só começa no mês seguinte."""
        return self.orders(date.max)

    def _levered(
        self, orders: Mapping[str, StateOrder]
    ) -> list[tuple[StateLever, StateControl]]:
        """O par (alavanca, degrau) de cada ordem cuja empresa tem preço a segurar."""
        pairs: list[tuple[StateLever, StateControl]] = []
        for ticker, order in orders.items():
            company = self._companies.get(ticker)
            if company is not None and company.lever is not None:
                pairs.append((company.lever, order.control))
        return pairs

    def held_points(self, day: date) -> Decimal:
        """Pontos de IPCA que as ordens em vigor no dia seguram juntas."""
        return levers.total_held_points(self._levered(self.orders(day)))

    def other_points(self, ticker: str, orders: Mapping[str, StateOrder]) -> Decimal:
        """Pontos que as ordens das outras estatais seguram: o teto que sobra à de `ticker`."""
        return levers.total_held_points(
            self._levered({t: o for t, o in orders.items() if t != ticker})
        )

    def _held_series(self, through: date) -> Sequence[Decimal]:
        """Os pontos segurados em cada mês, do primeiro com ordem até o mês de `through`."""
        history = self._history()
        if not history:
            return []
        last = _month_start(through)
        series: list[Decimal] = []
        month = min(history)
        while month <= last:
            series.append(self.held_points(month))
            month = _next_month(month)
        return series

    def inflation_points(self, month: date) -> Decimal:
        """
        O efeito no IPCA do mês, em pontos: negativo enquanto o controle segura o preço e,
        no primeiro mês sem controle, a inflação represada inteira.
        """
        path = levers.inflation_path(self._held_series(month))
        return path[-1] if path else Decimal(0)

    def backlog(self, day: date) -> Decimal:
        """A inflação represada hoje, em pontos de nível de preços."""
        return levers.backlog_points(self._held_series(day))

    def released_points(self, month: date) -> Decimal:
        """A inflação represada que volta no mês, em pontos de nível de preços; 0 fora da soltura."""
        return levers.price_level_points(max(self.inflation_points(month), Decimal(0)))

    def credit_points(self, month: date) -> Decimal:
        """Pontos de juro que o crédito perde no mês, pelas ordens no banco estatal."""
        return levers.total_credit_points(self._levered(self.orders(month)))

    # Fundação e PIB

    def _first_month(self, company: StateCompanyDTO) -> date | None:
        """O primeiro mês do orçamento que conta a fundada: o da vigência, ou o seguinte se ela vigorou no último dia."""
        if (
            company.origin is not StateCompanyOrigin.FOUNDED
            or company.founded_on is None
        ):
            return None
        return _effect_month(company.founded_on)

    def founding_spending(self, month: date) -> Decimal:
        """O gasto primário da fundação no mês, em reais: a parcela de cada fundada nos 12 meses a partir da vigência."""
        start = _month_start(month)
        total = Decimal(0)
        for company in self._companies.values():
            first = self._first_month(company)
            if (
                first is not None
                and 0 <= _months_between(first, start) < gdp.FOUNDING_MONTHS
            ):
                total += gdp.founding_installment(company.invested)
        return total

    def _policies(
        self, ticker: str, first: date, last: date, through: date | None = None
    ) -> list[DividendPolicy]:
        """
        A política de dividendos de cada mês, do primeiro ao último, pelas ordens em vigor.
        Com `through`, os meses depois dele seguem a ordem em vigor nesse dia.
        """
        history = self._history()
        starts = sorted(history)
        policies: list[DividendPolicy] = []
        started = 0
        month = first
        while month <= last:
            day = month if through is None else min(month, through)
            while started < len(starts) and starts[started] <= day:
                started += 1
            orders = history[starts[started - 1]] if started else {}
            policies.append(orders.get(ticker, StateOrder()).dividend_policy)
            month = _next_month(month)
        return policies

    def _sector_billions(self, month: date) -> dict[StateLever | None, Decimal]:
        """O porte efetivo, em bilhões, das fundadas que ainda são do governo no mês, por setor."""
        start = _month_start(month)
        totals: dict[StateLever | None, Decimal] = {}
        for company in self._companies.values():
            first = self._first_month(company)
            if first is None or first > start:
                continue
            if company.privatized_on is not None and start >= _effect_month(
                company.privatized_on
            ):
                continue
            multiplier = gdp.size_multiplier(
                self._policies(company.ticker, first, start)
            )
            billions = Decimal(required(company.size).billions) * multiplier
            totals[company.lever] = totals.get(company.lever, Decimal(0)) + billions
        return totals

    def gdp_push(self, month: date) -> Decimal:
        """
        O empurrão permanente das fundadas no crescimento, em fração ao ano. O porte de cada
        uma anda com a política de dividendos (reinvestir cresce, apertar encolhe) e conta
        até a venda; o setor é a alavanca, e as sem alavanca formam um grupo.
        """
        return gdp.permanent_push(self._sector_billions(month))

    def founding_push(
        self, size: StateCompanySize, lever: StateLever | None, month: date
    ) -> Decimal:
        """O que uma fundação nova soma ao empurrão permanente: a segunda do mesmo setor vale menos que a primeira."""
        totals = self._sector_billions(month)
        before = gdp.permanent_push(totals)
        totals[lever] = totals.get(lever, Decimal(0)) + Decimal(size.billions)
        return gdp.permanent_push(totals) - before

    def expected_month_profit(
        self, company: StateCompanyDTO, day: date
    ) -> Decimal | None:
        """
        O lucro de um mês que a fundada rende em média, sobre o valor justo do dia; None na
        importada, que não tem lucro modelado. Não usa o sorteio, que é o futuro da partida.
        """
        if (
            company.origin is not StateCompanyOrigin.FOUNDED
            or company.mean_return is None
        ):
            return None
        return max(
            fair_value.expected_monthly_profit(
                self.fair_value_on(company, day), company.mean_return
            ),
            Decimal(0),
        )
