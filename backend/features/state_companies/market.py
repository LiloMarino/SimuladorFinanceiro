"""O pregão das estatais fundadas: preço sintético em volta do valor justo, sem série histórica."""

import math
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from functools import cached_property

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.state_company import StateCompanyDTO
from backend.core.enum import IndicatorSeries, StateCompanyStatus
from backend.core.utils import required
from backend.features.market_maker.account import MakerAccount
from backend.features.market_maker.candle import close_candle
from backend.features.market_maker.maker import MarketMaker
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.state_companies import reference
from backend.features.state_companies.book import StateCompanyBook, maker_shares


@dataclass
class _Deviation:
    """O desvio em log de uma ação em cada pregão depois da fundação, calculado até onde já foi pedido."""

    values: list[float] = field(default_factory=list)


class StateCompanyMarket:
    """
    Dá liquidez às ações das estatais fundadas. O governo guarda a sua fatia fora do
    mercado e o formador negocia o resto: vende do estoque dele, que são as ações que
    nenhuma carteira da partida tem, e compra sem limite. O preço de referência do dia é o
    valor justo por ação sob a ordem de preço em vigor, vezes o desvio do dia: o Ibovespa
    da partida e um ruído próprio da ação, que voltam ao valor justo com o tempo. O desvio
    é calculado desde a fundação sobre os pregões da série do Ibovespa e guardado em memória.
    """

    def __init__(
        self,
        simulation_id: int,
        engine: SimulationEngine,
        book: StateCompanyBook,
        noise: reference.Noise = reference.seeded_noise,
    ) -> None:
        self._simulation_id = simulation_id
        self._engine = engine
        self._book = book
        self._noise = noise
        self._deviations: dict[str, _Deviation] = {}
        self._accounts: dict[str, MakerAccount] = {}
        self._last_close: dict[str, float | None] = {}
        for company in book.companies():
            if book.is_founded(company.ticker):
                self.register(company)

    @cached_property
    def _maker(self) -> MarketMaker:
        """O formador nasce no primeiro uso: sem estatal fundada, o motor de ordens não é tocado."""
        return MarketMaker(
            self._engine.matching_engine, self._engine.broker.maker_accounts
        )

    def register(self, company: StateCompanyDTO) -> None:
        """Põe a ação da fundada no motor: o estoque do formador é o que as carteiras não têm."""
        shares = Decimal(company.shares)
        held = repository.state_company.shares_held(
            self._simulation_id, company.stock_id, self._engine.current_date
        )
        # Privatizada, a fatia do governo também circula: o estoque do formador é o resto
        privatized = company.status is StateCompanyStatus.PRIVATIZED
        stock = shares if privatized else Decimal(maker_shares(company))
        account = MakerAccount(quotas=shares, maker_quotas=stock - held)
        self._accounts[company.ticker] = account
        self._last_close[company.ticker] = repository.fund.last_close(
            self._simulation_id, company.stock_id, self._engine.current_date
        )
        self._engine.broker.maker_accounts[company.ticker] = account
        self._engine.add_created_stock(
            required(repository.stock.get_by_ticker(company.ticker))
        )

    def maker_stock(self, ticker: str) -> Decimal:
        """As ações que o formador guarda da estatal, a vender; zero sem formador."""
        account = self._accounts.get(ticker)
        return account.maker_quotas if account is not None else Decimal(0)

    def add_leftover(self, ticker: str, shares: int) -> None:
        """A sobra da oferta de privatização vai ao estoque do formador, que segue dando liquidez."""
        self._accounts[ticker].receive_maker(Decimal(shares))

    def _trading(self) -> list[tuple[StateCompanyDTO, MakerAccount]]:
        """As fundadas com formador: depois de privatizada a ação segue negociando contra ele."""
        return [
            (company, account)
            for ticker, account in self._accounts.items()
            if (company := self._book.company(ticker)) is not None
        ]

    def deviation(self, company: StateCompanyDTO, day: date) -> float:
        """O desvio em log do preço contra o valor justo no pregão de `day`; 0 na fundação."""
        founded_on = company.founded_on
        if founded_on is None or day <= founded_on:
            return 0.0
        history = repository.economic.get_history(
            IndicatorSeries.IBOV, self._simulation_id
        )
        dates = history.dates
        first = bisect_right(dates, founded_on)
        end = bisect_right(dates, day)
        known = self._deviations.setdefault(company.ticker, _Deviation()).values
        if len(known) < end - first:
            start = first + len(known)
            returns = [
                (
                    dates[i],
                    reference.log_return(
                        float(history.values[dates[i - 1]]) if i > 0 else 0.0,
                        float(history.values[dates[i]]),
                    ),
                )
                for i in range(start, end)
            ]
            known.extend(
                reference.deviation_path(
                    returns,
                    company.seed or 0,
                    initial=known[-1] if known else 0.0,
                    noise=self._noise,
                )
            )
        return known[end - first - 1] if end > first else 0.0

    def fair_price(self, company: StateCompanyDTO, day: date) -> Decimal:
        """O valor justo por ação do dia, sob a ordem de preço em vigor."""
        per_share = self._book.fair_value_on(company, day) / company.shares
        factor = self._book.founded_price_factor(company.ticker, day)
        return per_share * Decimal(str(factor))

    def reference_price(self, company: StateCompanyDTO, day: date) -> Decimal:
        """O preço de referência do dia: o valor justo por ação com o desvio do pregão."""
        return self.fair_price(company, day) * Decimal(
            str(math.exp(self.deviation(company, day)))
        )

    def on_open(self, today: date) -> None:
        """A escada do formador refeita em volta do preço de referência do dia; o valor justo do dia vai ao motor para as estratégias."""
        for company, account in self._trading():
            self._engine.state_fair_values[company.ticker] = float(
                self.fair_price(company, today)
            )
            self._maker.refresh(
                company.ticker,
                float(self.reference_price(company, today)),
                account.quotas,
                today,
            )

    def on_close(self, today: date) -> list[CandleDTO]:
        """Fecha a vela do pregão de cada fundada e a grava na série da partida."""
        candles: list[CandleDTO] = []
        for company, account in self._trading():
            trades = account.take_day()
            stock = self._engine.stocks[company.ticker]
            reference_price = self.reference_price(company, today)
            candle = close_candle(
                stock,
                today,
                trades,
                self._last_close[company.ticker],
                reference_price,
                idle_close=reference_price,
            )
            self._last_close[company.ticker] = candle.close
            repository.fund.save_candle(self._simulation_id, candle)
            self._engine.update_market_data([candle])
            candles.append(candle)
        return candles
