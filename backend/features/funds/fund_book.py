import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_FLOOR, Decimal
from typing import Literal
from uuid import UUID, uuid4

from backend.core import repository
from backend.core.dto.candle import CandleDTO
from backend.core.dto.fund import (
    FundAssemblyBlock,
    FundAssemblyDTO,
    FundAssemblyMergeDTO,
    FundAssemblyOptionDTO,
    FundAssemblyPanelDTO,
    FundAssemblyTallyDTO,
    FundBuybackDTO,
    FundComanagerDTO,
    FundDayDTO,
    FundDirectedIssuanceDTO,
    FundDistributionDTO,
    FundDistributionPlanDTO,
    FundDTO,
    FundIssuanceDTO,
    FundIssuancePhase,
    FundIssuanceRightDTO,
    FundMergePreviewDTO,
    FundMergeSideDTO,
    FundOfferSaleDTO,
    FundReportDTO,
    FundSummaryDTO,
    FundTermsDTO,
)
from backend.core.dto.stock import StockDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    AssetClass,
    FundAssemblyAgenda,
    FundAssemblyStatus,
    FundComanagerStatus,
    FundDirectedIssuanceStatus,
    IndicatorSeries,
    OrderAction,
    OrderStatus,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.fund_reference import FundReference
from backend.core.indicators import index_daily_rate
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.utils import (
    format_quantity,
    next_business_day,
    next_month_turn,
    ratio,
)
from backend.features.funds import headlines
from backend.features.funds.distribution import (
    drained_since,
    holder_payment,
    payout_per_quota,
    realized_profit,
    settle_month,
)
from backend.features.funds.fees import (
    management_fee,
    performance_charge,
    split_payable,
)
from backend.features.funds.fund_account import FundAccount
from backend.features.funds.fund_assembly import (
    FEE,
    MERGE,
    SWAP,
    FundAssemblies,
    raises_fee,
)
from backend.features.funds.fund_assembly import block_message as assembly_block_message
from backend.features.funds.fund_comanagers import (
    FundComanagers,
    expires_on,
    heir_of,
    operators_of,
    split_fee,
)
from backend.features.funds.fund_directed import (
    FundDirectedIssuances,
    cap_room,
    directed_price,
)
from backend.features.funds.fund_directed import expires_on as directed_expires_on
from backend.features.funds.fund_ledger import PERFORMANCE_PERIOD_MONTHS
from backend.features.funds.fund_merge import (
    MergeExit,
    MergePlan,
    MergeValuation,
    circular_navs,
    conversion_remainder,
    converted_quotas,
    exchange_ratio,
    exit_price,
    settle_exits,
)
from backend.features.funds.fund_offer import FundOffer
from backend.features.funds.performance import (
    PERFORMANCE_WINDOW,
    NavPoint,
    cut_window,
    excess_return,
)
from backend.features.funds.ranking_price import (
    RANKING_WINDOW,
    TradedDay,
    ranking_price,
)
from backend.features.market_maker.account import DayTrades
from backend.features.market_maker.candle import close_candle
from backend.features.market_maker.maker import MarketMaker
from backend.features.market_maker.sessions import window_end, window_session
from backend.features.notifications.news import Headline
from backend.features.simulation.simulation_engine import (
    RealizedKind,
    SimulationEngine,
)
from backend.features.variable_income.broker import to_money
from backend.features.variable_income.entities.order import LimitOrder

# Fração das cotas que o formador subscreve na oferta pública
STOCK_SHARE = 0.10

# O PL por cota da primeira integralização
FIRST_NAV = Decimal(100)

# Pregões da oferta pública, contando o da abertura: ao fim do último ela fecha sozinha
OFFER_SESSIONS = 5

# Pregões da emissão, contando o do anúncio: primeiro a preferência dos cotistas, depois a
# sobra aberta a todos. Ao fim do último, o que não vendeu não nasce
PREFERENCE_SESSIONS = 10
LEFTOVER_SESSIONS = 5

# O tamanho máximo de uma emissão, como fração das cotas em circulação no anúncio
ISSUANCE_LIMIT = Decimal(1)


def nav_per_quota(
    cash: Decimal,
    equity: Decimal,
    fixed: Decimal,
    debt: Decimal,
    quotas: Decimal,
) -> Decimal | None:
    """O patrimônio líquido (PL) por cota: (caixa + ações + renda fixa - dívida) / cotas.

    Sem cota em circulação o PL por cota não existe.
    """
    if quotas <= 0:
        return None
    return (cash + equity + fixed - debt) / quotas


def _payable_column(performance: bool) -> str:
    """O campo da gestora que guarda a taxa a pagar de cada tipo."""
    return "performance_fee_payable" if performance else "management_fee_payable"


def maker_stake(quotas: Decimal) -> Decimal:
    """As cotas que o formador subscreve na oferta de abertura: `STOCK_SHARE` do total, para baixo."""
    return Decimal(math.floor(float(quotas) * STOCK_SHARE))


def takeover_offer_size(held: Decimal, quotas: Decimal, cap: Decimal) -> Decimal:
    """As cotas novas que a oferta de abertura emite para o gestor, com `held` das `quotas`,
    ficar com `cap` ou menos do total final.

    O total final é o das cotas depois da oferta mais a subscrição do formador sobre ele, e
    o gestor mantém o que tem: a conta pede o menor total que dá `held / cap`.
    """
    needed = held / cap
    total = max(quotas + 1, Decimal(math.floor(float(needed) / (1 + STOCK_SHARE))))
    while total + maker_stake(total) < needed:
        total += 1
    return total - quotas


def cdi_growth(start: date, end: date) -> Decimal:
    """O fator do CDI acumulado nos dias úteis depois de `start` até `end` (1,05 é 5% acumulados)."""
    factor = Decimal(1)
    day = next_business_day(start)
    while day <= end:
        rate = index_daily_rate(IndicatorSeries.CDI, day)
        if rate is not None:
            factor *= 1 + rate
        day = next_business_day(day)
    return factor


def offer_ends_on(listed_on: date) -> date:
    """O último pregão da oferta: o quinto dia útil a partir da abertura, contando o dia dela."""
    return window_end(listed_on, OFFER_SESSIONS)


def offer_session(listed_on: date, today: date) -> int:
    """O pregão da oferta em `today`: 1 no dia da abertura, até `OFFER_SESSIONS`."""
    return window_session(listed_on, today, OFFER_SESSIONS)


def issuance_windows(announced_on: date) -> tuple[date, date]:
    """O último pregão da preferência e o da sobra de uma emissão anunciada em `announced_on`."""
    preference_ends_on = window_end(announced_on, PREFERENCE_SESSIONS)
    leftover_starts_on = next_business_day(preference_ends_on)
    return preference_ends_on, window_end(leftover_starts_on, LEFTOVER_SESSIONS)


def is_data_com(day: date) -> bool:
    """Se `day` é o último pregão do mês: o dia em que o lucro realizado do mês fecha."""
    return next_business_day(day).month != day.month


def data_com_of_month(day: date) -> date:
    """O último pregão do mês de `day`."""
    last = day
    while not is_data_com(last):
        last = next_business_day(last)
    return last


# O campo de `funds` em que cada origem de lucro realizado se acumula no mês
_REALIZED_FIELDS: dict[RealizedKind, str] = {
    "dividends": "month_dividends",
    "interest": "month_interest",
    "sales_gain": "month_sales_gain",
}


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def _decimal_or_none(value: float | None) -> Decimal | None:
    return None if value is None else Decimal(str(value))


@dataclass
class Fund:
    """O estado vivo de uma gestora: os termos gravados, a conta do motor e o último PL."""

    terms: FundDTO
    account: FundAccount
    # Os últimos pregões negociados, em ordem cronológica, para o preço de ranking
    days: list[TradedDay] = field(default_factory=list)
    # O PL por cota dos últimos pregões fechados, em ordem cronológica, para o desempenho
    navs: list[NavPoint] = field(default_factory=list)
    nav: Decimal | None = None
    last_close: float | None = None
    # O preço do último negócio da cota, de pregões já fechados; nulo se nunca negociou
    last_trade_price: Decimal | None = None
    # O relatório mensal do último fechamento de mês, guardado pelo dia da virada que o gerou
    report: tuple[date, FundReportDTO] | None = None
    # A emissão aberta e o direito de preferência de cada jogador (por id de usuário)
    issuance: FundIssuanceDTO | None = None
    issuance_rights: dict[int, FundIssuanceRightDTO] = field(default_factory=dict)
    # A recompra aberta e a ordem de compra dela no livro
    buyback: FundBuybackDTO | None = None
    buyback_order: LimitOrder | None = None
    # A assembleia em andamento de cada pauta (convite ou votação), os votos dela por id de
    # usuário e as votações concluídas, da mais antiga à mais nova: delas sai o intervalo até
    # a próxima troca de gestor
    assemblies: dict[FundAssemblyAgenda, FundAssemblyDTO] = field(default_factory=dict)
    assembly_votes: dict[FundAssemblyAgenda, dict[int, bool]] = field(
        default_factory=dict
    )
    assembly_history: list[FundAssemblyDTO] = field(default_factory=list)
    # Os co-gestores: convites pendentes e ativos, que operam a carteira e dividem as taxas
    comanagers: list[FundComanagerDTO] = field(default_factory=list)
    # A oferta de cotas novas do principal que espera a resposta de um co-gestor
    directed: FundDirectedIssuanceDTO | None = None
    # Os rendimentos mensais já apurados, do mais antigo ao mais novo; o último ainda pode
    # estar sem pagamento (entre a data-com e o primeiro pregão do mês seguinte)
    distributions: list[FundDistributionDTO] = field(default_factory=list)

    @property
    def ticker(self) -> str:
        return self.terms.ticker

    @property
    def listed(self) -> bool:
        return self.terms.listed_on is not None

    def issuance_phase(self, today: date) -> FundIssuancePhase | None:
        """A fase da emissão aberta em `today`; nula sem emissão aberta."""
        if self.issuance is None:
            return None
        return "preference" if today <= self.issuance.preference_ends_on else "leftover"


class FundBook:
    """As gestoras da partida, ligadas ao motor: o PL do dia, o formador de mercado, a oferta
    pública, a vela da cota e as taxas.

    O dia tem duas pontas, na ordem do tick: `on_open` recalcula o PL e refaz as ordens do
    formador e da oferta antes de qualquer jogador ou bot operar; `on_close` fecha a vela com
    os negócios do pregão, fecha a oferta que chegou ao último pregão, grava e deixa o preço de
    ranking pronto para o snapshot.

    A gestora congela enquanto o gestor governa o país: `frozen_until` devolve o último dia do
    mandato dele, lido do governo a cada consulta. A sala segue negociando a cota; só a conta da
    gestora e o que o gestor decide nela (aporte, oferta, taxas) param, e as taxas não correm.
    Com uma estratégia ligada na carteira, a gestora segue operando por ela: a carteira descongela
    (`portfolio_frozen_until`) e as decisões do gestor continuam congeladas.
    """

    def __init__(
        self,
        simulation_id: int,
        engine: SimulationEngine,
        client_of_user: Callable[[int], UUID],
        publish: Callable[[date, Headline], None] | None = None,
        frozen_until: Callable[[int], date | None] | None = None,
        participants: Callable[[], list[UserDTO]] | None = None,
        grace_ends: date | None = None,
        manager_cap: Decimal | None = None,
        automatic: Callable[[UUID], bool] | None = None,
        stop_automatic: Callable[[Fund, str], None] | None = None,
    ) -> None:
        self._simulation_id = simulation_id
        self._engine = engine
        self._client_of_user = client_of_user
        self._publish = publish
        # O último dia do mandato do gestor que governa, por id de usuário; nulo se ele não governa
        self._manager_frozen_until = frozen_until or (lambda _user_id: None)
        # Se a conta da gestora (por client_id) tem uma estratégia ligada, e como desligá-la com o motivo
        self._automatic = automatic or (lambda _client_id: False)
        self._stop_automatic = stop_automatic or (lambda _fund, _reason: None)
        # Os jogadores e bots da partida, lidos a cada consulta
        self.participants = participants or (lambda: [])
        # No modo aquisição hostil, a fração das cotas que o gestor mantém depois da carência;
        # nulo sem o modo
        self._manager_cap = manager_cap
        # A ordem de venda das cotas do gestor acima do limite, por ticker
        self._takeover_orders: dict[str, LimitOrder] = {}
        # No modo aquisição hostil, o dia em que cada fundador perdeu a assembleia da própria
        # gestora e passou a só assistir, por id de usuário
        self._eliminated: dict[int, date] = {}
        if manager_cap is not None:
            self._eliminated = {
                user_id: day
                for _, user_id, _, day in repository.fund.founder_removals(
                    [simulation_id]
                )
            }
        self._funds: dict[str, Fund] = {}
        # As gestoras incorporadas por fusão, por id: saíram do mercado e só guardam o nome
        self._merged: dict[int, FundDTO] = {}
        self._accounts: dict[str, FundAccount] = {}
        self._maker = MarketMaker(engine.matching_engine, engine.broker.maker_accounts)
        self._offer = FundOffer(engine.matching_engine, self._accounts)
        self._assemblies = FundAssemblies(
            simulation_id, engine, lambda: self.participants(), grace_ends
        )
        self._comanagers = FundComanagers(lambda: self.participants())
        self._directed = FundDirectedIssuances()
        engine.broker.on_fund_offer_sale = self._record_offer_sale
        engine.broker.on_fund_buyback = self._record_buyback
        engine.on_realized = self._record_realized
        for terms in repository.fund.of_simulation(simulation_id):
            if terms.merged_into_fund_id is not None:
                self._merged[terms.id] = terms
                continue
            self._load(terms)

    @property
    def eliminated(self) -> dict[int, date]:
        """Os eliminados do modo aquisição hostil e o dia da eliminação, por id de usuário."""
        return dict(self._eliminated)

    @property
    def manager_cap(self) -> Decimal | None:
        """No modo aquisição hostil, a fração das cotas que o principal e os co-gestores mantêm; nulo sem o modo."""
        return self._manager_cap

    @property
    def client_ids(self) -> list[UUID]:
        """As contas das gestoras no motor."""
        return [fund.account.client_id for fund in self._funds.values()]

    def funds(self) -> list[Fund]:
        return list(self._funds.values())

    def get(self, ticker: str) -> Fund:
        return self._funds[ticker]

    def find(self, ticker: str) -> Fund | None:
        """A gestora dona do ticker, ou nulo quando ele não é de cota."""
        return self._funds.get(ticker)

    def is_merged(self, ticker: str) -> bool:
        """Se o ticker é de uma gestora incorporada por fusão: a cota deixou o mercado."""
        return any(terms.ticker == ticker for terms in self._merged.values())

    def by_id(self, fund_id: int) -> Fund:
        for fund in self._funds.values():
            if fund.terms.id == fund_id:
                return fund
        raise NotFoundError("Gestora não encontrada")

    def founder_of(self, ticker: str) -> int | None:
        """O fundador da gestora que já tem este ticker na partida."""
        fund = self._funds.get(ticker)
        return fund.terms.founder_user_id if fund else None

    def of_client(self, client_id: UUID) -> Fund | None:
        """A gestora dona da conta `client_id` no motor."""
        for fund in self._funds.values():
            if fund.account.client_id == client_id:
                return fund
        return None

    def managed_by(self, user_id: int) -> list[Fund]:
        """As gestoras de que o jogador é o gestor principal."""
        return [f for f in self._funds.values() if f.terms.manager_user_id == user_id]

    def held_by(self, user_id: int) -> list[Fund]:
        """As gestoras que o jogador tem: as que gere e as que passou ao herdeiro e retoma no fim do mandato."""
        return [
            f
            for f in self._funds.values()
            if user_id in (f.terms.manager_user_id, f.terms.leave_manager_user_id)
        ]

    def operated_by(self, user_id: int) -> list[Fund]:
        """As gestoras cuja carteira o jogador opera: como principal ou como co-gestor ativo."""
        return [f for f in self._funds.values() if user_id in operators_of(f)]

    def operators(self, fund: Fund) -> list[int]:
        """Os ids de quem opera a carteira da gestora: o principal e os co-gestores ativos."""
        return operators_of(fund)

    def audience_of(self, client_id: UUID) -> tuple[tuple[UUID, ...], int] | None:
        """Para a conta de uma gestora: o client_id de cada operador e o id dela; nulo para qualquer outra conta."""
        fund = self.of_client(client_id)
        if fund is None:
            return None
        clients = tuple(self._client_of_user(u) for u in operators_of(fund))
        return clients, fund.terms.id

    def frozen_until(self, fund: Fund) -> date | None:
        """O último dia em que a gestora fica congelada: o fim do mandato do gestor presidente."""
        return self._manager_frozen_until(fund.terms.manager_user_id)

    def automatic(self, fund: Fund) -> bool:
        """Se uma estratégia opera a carteira da gestora."""
        return self._automatic(fund.account.client_id)

    def portfolio_frozen_until(self, fund: Fund) -> date | None:
        """O último dia em que a carteira da gestora fica sem operar: o do congelamento, e nenhum com a estratégia ligada."""
        return None if self.automatic(fund) else self.frozen_until(fund)

    def price(self, fund: Fund) -> Decimal | None:
        """O preço do último negócio da cota: o de hoje se já negociou, senão o do último pregão com negócio."""
        today = fund.account.day
        return today.close if today.open is not None else fund.last_trade_price

    def summary(
        self, fund: Fund, nicknames: Mapping[int, str] | None = None
    ) -> FundSummaryDTO:
        """A gestora com o PL por cota de agora, o preço de ranking, o último negócio, a oferta e o congelamento.

        `nicknames` são os apelidos por id de usuário; sem eles a consulta lê os participantes.
        """
        if nicknames is None:
            nicknames = {user.id: user.nickname for user in self.participants()}
        listed_on = fund.terms.listed_on
        # A oferta de abertura é a única que o resumo mostra; a emissão tem estado próprio,
        # e a sobra dela não faz a gestora voltar ao estágio de oferta
        opening_offer = fund.issuance is None
        open_on = (
            listed_on
            if fund.account.offer_remaining is not None and opening_offer
            else None
        )
        terms = fund.terms.model_dump(include=set(FundTermsDTO.model_fields))
        if not opening_offer:
            terms["offer_remaining"] = None
        return FundSummaryDTO(
            **terms,
            nav=self._nav(fund),
            ranking_price=self._engine.ranking_prices.get(fund.ticker),
            price=self.price(fund),
            manager_nickname=nicknames.get(fund.terms.manager_user_id),
            offer_session=(
                offer_session(open_on, self._engine.current_date) if open_on else None
            ),
            offer_ends_on=offer_ends_on(open_on) if open_on else None,
            frozen_until=self.frozen_until(fund),
            automatic=self.automatic(fund),
            leave_until=(
                self._manager_frozen_until(fund.terms.leave_manager_user_id)
                if fund.terms.leave_manager_user_id is not None
                else None
            ),
        )

    def summaries(self) -> list[FundSummaryDTO]:
        """A lista de gestoras da partida, com os apelidos lidos uma vez."""
        nicknames = {user.id: user.nickname for user in self.participants()}
        return [self.summary(fund, nicknames) for fund in self._funds.values()]

    # =========================
    # Criação e oferta
    # =========================

    def found(
        self,
        *,
        ticker: str,
        name: str,
        founder_user_id: int,
        manager_user_id: int,
        management_fee: Decimal,
        performance_fee: Decimal,
    ) -> Fund:
        """Cria a gestora vazia: a cota entra no catálogo da partida e a carteira dela, no motor."""
        if ticker in self._funds:
            raise ConflictError("Já existe uma gestora com este ticker na partida")
        stock = repository.fund.claim_stock(ticker, name)
        if stock is None:
            raise ConflictError("As quatro letras deste ticker já são de um ativo")
        terms = repository.fund.create(
            simulation_id=self._simulation_id,
            stock_id=stock.id,
            ticker=ticker,
            client_id=uuid4(),
            founder_user_id=founder_user_id,
            manager_user_id=manager_user_id,
            name=name,
            management_fee=management_fee,
            performance_fee=performance_fee,
            manager_since=self._engine.current_date,
        )
        return self._load(terms)

    def contribute(
        self,
        ticker: str,
        manager: UUID,
        cash: Decimal,
        stocks: Mapping[str, Decimal],
    ) -> Decimal:
        """Integraliza caixa e ações do gestor na gestora e devolve as cotas emitidas a ele.

        As cotas valem o que foi levado a preço de mercado, ao PL do dia (R$ 100 na primeira
        integralização), arredondadas para baixo; a sobra fica na gestora. O custo médio das
        ações vai junto e as cotas nascem com o custo contábil do que foi levado, de modo que a
        integralização não gera venda nem DARF.
        """
        fund = self._funds[ticker]
        if fund.listed:
            raise ConflictError("A integralização só vale antes da oferta pública")
        if cash <= 0 and not stocks:
            raise UnprocessableEntityError("Informe o que integralizar")
        engine = self._engine
        if engine.get_cash(manager) < cash:
            raise UnprocessableEntityError("Caixa insuficiente para integralizar")

        # Confere tudo antes de mover qualquer coisa
        value = cost = cash
        positions = engine.broker.get_positions(manager)
        for held_ticker, quantity in stocks.items():
            stock = engine.stocks.get(held_ticker)
            if stock is None or stock.asset_class is AssetClass.FUND:
                raise UnprocessableEntityError(
                    f"{held_ticker} não pode ser integralizado"
                )
            if quantity <= 0:
                raise UnprocessableEntityError(
                    "A quantidade precisa ser maior que zero"
                )
            engine.check_quantity(held_ticker, quantity)
            position = positions.get(held_ticker)
            if position is None or position.size - position.reserved < quantity:
                raise UnprocessableEntityError(f"Posição insuficiente em {held_ticker}")
            value += engine.get_current_price(position) * quantity
            cost += position.avg_price * quantity

        nav = self._nav(fund) if fund.account.quotas > 0 else FIRST_NAV
        if nav is None or nav <= 0:
            raise ConflictError("A gestora não tem patrimônio para emitir cotas")
        issued = (value / nav).to_integral_value(rounding=ROUND_FLOOR)
        if issued <= 0:
            raise UnprocessableEntityError("O valor não chega a uma cota")

        fund_client = fund.account.client_id
        if cash > 0:
            engine.transfer_cash(manager, fund_client, cash)
        for held_ticker, quantity in stocks.items():
            engine.broker.transfer_position(manager, fund_client, held_ticker, quantity)
        fund.account.quotas += issued
        engine.broker.receive_position(manager, ticker, issued, cost / issued)
        # O preço de ranking da cota já vale na carteira do gestor
        fund.nav = self._nav(fund)
        if fund.nav is not None:
            engine.ranking_prices[ticker] = ranking_price(fund.days, fund.nav)
        self._save(fund)
        return issued

    def open_offer(self, ticker: str, size: Decimal) -> None:
        """Abre a oferta pública de `size` cotas novas ao PL de hoje e anuncia no jornal."""
        self._open_offer(ticker, size)
        fund = self._funds[ticker]
        today = self._engine.current_date
        manager = next(
            (
                user.nickname
                for user in self.participants()
                if user.id == fund.terms.manager_user_id
            ),
            None,
        )
        self._announce(
            today,
            headlines.offer_opened(
                fund.terms.name,
                ticker,
                manager,
                size,
                fund.terms.offer_price or Decimal(0),
                offer_ends_on(today),
                OFFER_SESSIONS,
            ),
        )

    def _open_offer(self, ticker: str, size: Decimal) -> None:
        """Lista a gestora com a oferta pública de `size` cotas novas ao PL de hoje.

        O formador subscreve `STOCK_SHARE x (cotas + size)` ao PL de antes da subscrição e paga
        as cotas dele ao PL em dinheiro sintético, que entra no caixa da gestora: o PL por cota segue o
        mesmo e é ele que vale dali em diante, na oferta, nas ordens e na marca d'água da
        performance.
        """
        fund = self._funds[ticker]
        nav = self._nav(fund)
        if nav is None or fund.listed:
            raise ValueError("A oferta abre uma vez, numa gestora com cotas")
        today = self._engine.current_date
        account = fund.account
        account.offer_remaining = size
        stake = maker_stake(account.quotas + size)
        account.subscribe_maker(stake, nav)
        self._engine.credit_fund_subscription(account.client_id, stake * nav)
        fund.nav = nav
        fund.terms = fund.terms.model_copy(
            update={
                "listed_on": today,
                "offer_quotas": size,
                "offer_price": Decimal(str(round(float(nav), 2))),
                "high_water_mark": nav,
                "high_water_mark_on": today,
            }
        )
        self._refresh_orders(fund, today)
        self._save(fund)

    def close_offer(self, ticker: str) -> None:
        """Encerra a oferta: o que não vendeu não é emitido."""
        fund = self._funds[ticker]
        if fund.issuance is not None:
            raise ConflictError("A emissão encerra sozinha ao fim dos pregões dela")
        self._close_offer(fund, self._engine.current_date)

    # =========================
    # Oferta automática do modo aquisição hostil
    # =========================

    def _advance_takeover(self, fund: Fund, today: date) -> None:
        """A abertura do dia da oferta automática: depois da carência, o gestor que passa do
        limite de cotas entra numa oferta ao PL de 5 pregões, uma vez por gestora.

        Com a oferta aberta, a venda das cotas do gestor é refeita todo dia ao PL novo.
        """
        cap, grace_ends = self._manager_cap, self._assemblies.grace_ends
        if cap is None or grace_ends is None or today < grace_ends:
            return
        started = fund.terms.takeover_offer_on
        if started is None:
            self._open_takeover_offer(fund, cap, today)
        elif not self._takeover_by_offer(fund) and today <= offer_ends_on(started):
            self._sell_takeover_excess(fund, cap, today)

    def _takeover_by_offer(self, fund: Fund) -> bool:
        """A oferta automática foi a de abertura da gestora (cotas novas), e não a venda das
        cotas do gestor: a gestora listou no mesmo dia em que a oferta automática abriu."""
        return fund.terms.listed_on == fund.terms.takeover_offer_on

    def _manager_held(self, fund: Fund) -> Decimal:
        """As cotas do gestor na carteira pessoal dele."""
        return self._assemblies.holdings(fund).get(
            fund.terms.manager_user_id, Decimal(0)
        )

    def _takeover_excess(self, fund: Fund, cap: Decimal) -> Decimal:
        """As cotas do gestor acima do limite, em cotas inteiras; zero ou menos dentro dele."""
        limit = (cap * fund.account.quotas).to_integral_value(rounding=ROUND_FLOOR)
        return self._manager_held(fund) - limit

    def _open_takeover_offer(self, fund: Fund, cap: Decimal, today: date) -> None:
        """Abre a oferta automática se o gestor passa do limite e a gestora não está em oferta
        ou emissão (que correm até o fim; a conferência volta no pregão seguinte)."""
        account = fund.account
        if account.offer_remaining is not None or fund.issuance is not None:
            return
        # A recompra queima cotas e levaria o gestor de volta acima do limite
        self._sync_buyback(fund)
        if fund.buyback is not None:
            self.cancel_buyback(fund.ticker)
        excess = self._takeover_excess(fund, cap)
        if excess <= 0:
            return
        by_offer = not fund.listed
        if by_offer:
            size = takeover_offer_size(self._manager_held(fund), account.quotas, cap)
            self._open_offer(fund.ticker, size)
        else:
            size = excess
        fund.terms = fund.terms.model_copy(update={"takeover_offer_on": today})
        self._save(fund)
        if not by_offer:
            self._sell_takeover_excess(fund, cap, today)
        self._announce(today, headlines.takeover_offer_opened(fund.ticker, size))

    def _sell_takeover_excess(self, fund: Fund, cap: Decimal, today: date) -> None:
        """Refaz a ordem de venda das cotas do gestor acima do limite, ao PL do dia.

        O excesso sai das posições de agora do gestor, e por isso a ordem refeita cobre só o
        que ainda não vendeu, também depois de parar e retomar a partida.
        """
        ticker = fund.ticker
        self._cancel_takeover_order(ticker)
        excess = self._takeover_excess(fund, cap)
        if excess <= 0 or fund.nav is None:
            return
        manager_client = self._client_of_user(fund.terms.manager_user_id)
        # A posição do gestor na cota fica livre para a ordem: as outras vendas dele saem
        matching = self._engine.matching_engine
        for order in matching.order_book.orders_of(manager_client):
            if order.ticker == ticker and order.action == OrderAction.SELL:
                matching.cancel(order_id=order.id, client_id=order.client_id)
        order = LimitOrder(
            client_id=manager_client,
            ticker=ticker,
            size=excess,
            action=OrderAction.SELL,
            placed_on=today,
            price=round(float(fund.nav), 2),
        )
        matching.submit(order)
        if order.remaining > 0:
            self._takeover_orders[ticker] = order

    def _cancel_takeover_order(self, ticker: str) -> None:
        order = self._takeover_orders.pop(ticker, None)
        if order is not None:
            self._engine.matching_engine.cancel(
                order_id=order.id, client_id=order.client_id
            )

    def _settle_takeover(self, fund: Fund, today: date) -> None:
        """No último pregão da oferta automática, o formador compra ao PL o que não vendeu."""
        cap, started = self._manager_cap, fund.terms.takeover_offer_on
        if (
            cap is None
            or started is None
            or fund.nav is None
            or today != offer_ends_on(started)
        ):
            return
        account = fund.account
        price = Decimal(str(round(float(fund.nav), 2)))
        if self._takeover_by_offer(fund):
            left = account.offer_remaining
            if left is None:
                return
            # A sobra da oferta nasce já nas mãos do formador, paga em dinheiro sintético
            self._offer.close(fund.ticker)
            account.subscribe_maker(left, price)
            self._engine.credit_fund_subscription(account.client_id, left * price)
            repository.fund.record_offer_sale(
                fund.terms.id,
                FundOfferSaleDTO(
                    day=today,
                    buyer_user_id=None,
                    quotas=left,
                    price=price,
                    issuance_id=None,
                ),
            )
            fund.terms = fund.terms.model_copy(update={"offer_closed_on": today})
        else:
            self._cancel_takeover_order(fund.ticker)
            left = self._takeover_excess(fund, cap)
            if left <= 0:
                return
            # As cotas que o gestor não vendeu passam ao formador
            manager_client = self._client_of_user(fund.terms.manager_user_id)
            self._engine.broker.sell_to_fund(manager_client, fund.ticker, left, price)
            account.maker_trade(OrderAction.BUY, left, price)
        account.record_trade(left, price)

    # =========================
    # Emissão
    # =========================

    def announce_issuance(self, ticker: str, size: Decimal) -> FundIssuanceDTO:
        """Anuncia a emissão de `size` cotas novas ao PL por cota de hoje, que fica fixo até o fim.

        Cada jogador cotista ganha o direito de comprar `size x (cotas dele / cotas em
        circulação)` cotas, arredondado para baixo, nos primeiros pregões; o que sobra abre a todos.
        O caixa recebido sobe junto com as cotas, e por isso o PL por cota de quem não comprou
        segue o mesmo.
        """
        fund = self._funds[ticker]
        self._sync_buyback(fund)
        nav = self._nav(fund)
        account = fund.account
        if nav is None or not fund.listed:
            raise ConflictError(
                "A emissão vale para uma gestora com a oferta pública aberta"
            )
        if account.offer_remaining is not None or fund.issuance is not None:
            raise ConflictError("A gestora já tem uma oferta ou emissão em andamento")
        if fund.buyback is not None:
            raise ConflictError("Encerre a recompra antes de emitir cotas")
        if SWAP in fund.assemblies or MERGE in fund.assemblies:
            raise ConflictError(
                "A gestora tem uma assembleia em andamento e não emite cotas até o resultado"
            )
        if size <= 0 or size != size.to_integral_value():
            raise UnprocessableEntityError("Informe uma quantidade inteira de cotas")
        if size > account.quotas * ISSUANCE_LIMIT:
            raise UnprocessableEntityError(
                f"Uma emissão vai até {format_quantity(account.quotas * ISSUANCE_LIMIT)} cotas"
            )

        today = self._engine.current_date
        preference_ends_on, ends_on = issuance_windows(today)
        rights = self._rights_of(fund, size)
        issuance = repository.fund.create_issuance(
            fund.terms.id,
            FundIssuanceDTO(
                id=0,
                announced_on=today,
                quotas=size,
                price=Decimal(str(round(float(nav), 2))),
                preference_ends_on=preference_ends_on,
                ends_on=ends_on,
                sold=Decimal(0),
                closed_on=None,
            ),
            rights,
        )
        fund.issuance = issuance
        fund.issuance_rights = {right.user_id: right for right in rights}
        self._announce(today, headlines.issuance_opened(ticker, size, issuance.price))
        return issuance

    # =========================
    # Emissão dirigida
    # =========================

    def directed_terms(self, fund: Fund) -> tuple[Decimal, Decimal, Decimal]:
        """O PL por cota, o preço de ranking e o preço da emissão dirigida: o maior dos dois, ao centavo."""
        nav = self._nav(fund)
        if nav is None or nav <= 0:
            raise ConflictError("A gestora ainda não tem PL por cota")
        ranking = self._engine.ranking_prices.get(fund.ticker, nav)
        return nav, ranking, directed_price(nav, ranking)

    def operators_quotas(self, fund: Fund) -> Decimal:
        """As cotas do principal e dos co-gestores ativos, somadas, nas carteiras pessoais deles."""
        held = self._assemblies.holdings(fund)
        return sum((held.get(u, Decimal(0)) for u in operators_of(fund)), Decimal(0))

    def directed_room(self, fund: Fund) -> Decimal:
        """O máximo de cotas novas de uma emissão dirigida agora.

        Fora do modo aquisição hostil, uma emissão vai até o total de cotas em circulação; no
        modo, o teto vale para o principal e os co-gestores somados e a conta é a de `cap_room`.
        """
        total = fund.account.quotas
        cap = self._manager_cap
        if cap is None:
            return total * ISSUANCE_LIMIT
        return cap_room(self.operators_quotas(fund), total, cap)

    def ensure_directed_open(self, fund: Fund) -> None:
        """A emissão dirigida vale numa gestora listada, sem oferta, emissão, recompra nem assembleia em andamento."""
        self._sync_buyback(fund)
        if not fund.listed:
            raise ConflictError(
                "A emissão dirigida vale depois da oferta pública da gestora"
            )
        if fund.account.offer_remaining is not None or fund.issuance is not None:
            raise ConflictError("A gestora já tem uma oferta ou emissão em andamento")
        if fund.buyback is not None:
            raise ConflictError("Encerre a recompra antes de emitir cotas")
        if SWAP in fund.assemblies or MERGE in fund.assemblies:
            raise ConflictError(
                "A gestora tem uma assembleia em andamento e não emite cotas até o resultado"
            )

    def offer_directed(
        self, ticker: str, buyer_nickname: str, quotas: Decimal
    ) -> FundDirectedIssuanceDTO:
        """O principal oferece `quotas` cotas novas a um co-gestor ativo; preço e teto nascem na aceitação."""
        fund = self._funds[ticker]
        buyer = next(
            (
                u
                for u in self.participants()
                if u.nickname == buyer_nickname and not u.is_bot
            ),
            None,
        )
        if buyer is None:
            raise UnprocessableEntityError("O comprador precisa ser um jogador da sala")
        self._ensure_directed_quantity(fund, quotas)
        return self._directed.offer(fund, buyer.id, quotas, self._engine.current_date)

    def issue_directed(self, ticker: str, buyer: UserDTO, quotas: Decimal) -> Decimal:
        """O principal emite `quotas` cotas novas para si e devolve o preço pago por cota."""
        fund = self._funds[ticker]
        if fund.directed is not None:
            raise ConflictError(
                "A gestora já tem uma oferta de cotas esperando resposta"
            )
        self._ensure_directed_quantity(fund, quotas)
        price = self._settle_directed(fund, buyer, quotas)
        self._directed.record_settled(
            fund, buyer.id, quotas, price, self._engine.current_date
        )
        return price

    def accept_directed(self, ticker: str, buyer: UserDTO) -> FundDirectedIssuanceDTO:
        """O co-gestor aceita a oferta: a emissão liquida ao preço e ao teto de agora."""
        fund = self._funds[ticker]
        offer = self._directed.pending_for(fund, buyer)
        price = self._settle_directed(fund, buyer, offer.quotas)
        today = self._engine.current_date
        self._directed.settle(fund, price, today)
        return offer.model_copy(
            update={
                "price": price,
                "settled_on": today,
                "status": FundDirectedIssuanceStatus.ACCEPTED,
            }
        )

    def decline_directed(self, ticker: str, buyer: UserDTO) -> FundDirectedIssuanceDTO:
        """O co-gestor recusa a oferta."""
        return self._directed.decline(self._funds[ticker], buyer)

    def cancel_directed(self, ticker: str) -> FundDirectedIssuanceDTO:
        """O principal cancela a oferta que espera resposta."""
        offer = self._directed.cancel(self._funds[ticker])
        if offer is None:
            raise NotFoundError("A gestora não tem oferta de cotas esperando resposta")
        return offer

    def directed_offers_for(
        self, user: UserDTO
    ) -> list[tuple[Fund, FundDirectedIssuanceDTO, str, date]]:
        """As ofertas de cotas que esperam `user`: a gestora, a oferta, o apelido do principal e o último dia dela."""
        names = self._nicknames()
        return [
            (
                fund,
                fund.directed,
                names.get(fund.terms.manager_user_id, "?"),
                directed_expires_on(fund.directed),
            )
            for fund in self._funds.values()
            if fund.directed is not None and fund.directed.buyer_user_id == user.id
        ]

    def _ensure_directed_quantity(self, fund: Fund, quotas: Decimal) -> None:
        self.ensure_directed_open(fund)
        if quotas <= 0 or quotas != quotas.to_integral_value():
            raise UnprocessableEntityError("Informe uma quantidade inteira de cotas")
        room = self.directed_room(fund)
        if quotas > room:
            raise UnprocessableEntityError(
                f"Uma emissão dirigida vai até {format_quantity(room)} cotas agora"
            )

    def _settle_directed(self, fund: Fund, buyer: UserDTO, quotas: Decimal) -> Decimal:
        """Liquida a emissão dirigida ao preço e ao teto de agora e devolve o preço por cota.

        O caixa do comprador entra na gestora, a taxa a pagar sai primeiro dele e as cotas
        nascem na carteira do comprador ao preço pago. Sem comissão de banqueiro.
        """
        self.ensure_directed_open(fund)
        _, _, price = self.directed_terms(fund)
        room = self.directed_room(fund)
        if quotas > room:
            raise ConflictError(
                f"Uma emissão dirigida vai até {format_quantity(room)} cotas agora"
            )
        cost = price * quotas
        engine = self._engine
        if engine.get_cash(buyer.client_id) < cost:
            raise ConflictError("Caixa insuficiente para comprar as cotas")

        engine.transfer_cash(buyer.client_id, fund.account.client_id, cost)
        fund.account.subscribe(quotas)
        engine.broker.receive_position(buyer.client_id, fund.ticker, quotas, price)
        self.settle_payable(fund)
        fund.nav = self._nav(fund)
        if fund.nav is not None:
            engine.ranking_prices[fund.ticker] = ranking_price(fund.days, fund.nav)
        self._refresh_orders(fund, engine.current_date)
        self._save(fund)
        return price

    def subscribe_issuance(self, ticker: str, user: UserDTO, quotas: Decimal) -> None:
        """O cotista compra `quotas` da preferência ao preço da emissão, dentro do direito que resta.

        A compra é direta: o caixa dele paga, a cota vira posição e o dinheiro entra no caixa da
        gestora junto com a cota nova.
        """
        fund = self._funds[ticker]
        issuance = fund.issuance
        today = self._engine.current_date
        if issuance is None or fund.issuance_phase(today) != "preference":
            raise ConflictError("A preferência desta emissão não está aberta")
        if quotas <= 0 or quotas != quotas.to_integral_value():
            raise UnprocessableEntityError("Informe uma quantidade inteira de cotas")
        right = fund.issuance_rights.get(user.id)
        left = right.rights - right.bought if right else Decimal(0)
        if right is None or quotas > left:
            raise UnprocessableEntityError(
                f"Você tem direito a mais {format_quantity(left)} cotas nesta emissão"
            )
        cost = issuance.price * quotas
        if self._engine.get_cash(user.client_id) < cost:
            raise UnprocessableEntityError("Caixa insuficiente para comprar as cotas")

        account = fund.account
        self._engine.broker.buy_from_fund(
            user.client_id, ticker, quotas, issuance.price
        )
        account.subscribe(quotas)
        self._engine.credit_fund_offer(account.client_id, cost)
        repository.fund.record_offer_sale(
            fund.terms.id,
            FundOfferSaleDTO(
                day=today,
                buyer_user_id=user.id,
                quotas=quotas,
                price=issuance.price,
                issuance_id=issuance.id,
            ),
        )
        fund.issuance_rights[user.id] = right.model_copy(
            update={"bought": right.bought + quotas}
        )
        self._add_issuance_sold(fund, quotas)
        # A preferência que esgota a emissão a encerra na hora
        if fund.issuance is not None and fund.issuance.sold >= fund.issuance.quotas:
            self._close_issuance(fund, today)
        self._save(fund)

    def _rights_of(self, fund: Fund, size: Decimal) -> list[FundIssuanceRightDTO]:
        """O retrato dos cotistas no anúncio: o direito de cada jogador pela proporção que ele tem.

        Bots e formador de mercado ficam sem preferência e compram a sobra pelo livro.
        """
        total = fund.account.quotas
        rights: list[FundIssuanceRightDTO] = []
        for user in self.participants():
            if user.is_bot:
                continue
            position = self._engine.broker.get_positions(user.client_id).get(
                fund.ticker
            )
            if position is None or position.size <= 0:
                continue
            quotas = (size * position.size / total).to_integral_value(
                rounding=ROUND_FLOOR
            )
            if quotas > 0:
                rights.append(
                    FundIssuanceRightDTO(
                        user_id=user.id, rights=quotas, bought=Decimal(0)
                    )
                )
        return rights

    def _add_issuance_sold(self, fund: Fund, quotas: Decimal) -> None:
        """Soma as cotas que acabaram de nascer na emissão e grava o andamento."""
        issuance = fund.issuance
        if issuance is None:
            return
        fund.issuance = issuance.model_copy(update={"sold": issuance.sold + quotas})
        repository.fund.save_issuance(
            fund.issuance, list(fund.issuance_rights.values())
        )

    def _advance_issuance(self, fund: Fund, today: date) -> None:
        """A virada do dia da emissão: a sobra vira a oferta do emissor; passado o fim, ela encerra.

        O saldo da sobra sai de `quotas - sold`, gravados, e por isso a emissão em andamento
        sobrevive a parar e retomar a partida.
        """
        issuance = fund.issuance
        if issuance is None:
            return
        if today > issuance.ends_on:
            self._close_issuance(fund, today)
        elif fund.issuance_phase(today) == "leftover":
            leftover = issuance.quotas - issuance.sold
            fund.account.offer_remaining = leftover if leftover > 0 else None

    def _close_issuance(self, fund: Fund, day: date) -> None:
        """Encerra a emissão: tira a sobra do livro e grava o fechamento; o que não vendeu não nasce."""
        issuance = fund.issuance
        if issuance is None:
            return
        self._offer.close(fund.ticker)
        closed = issuance.model_copy(update={"closed_on": day})
        repository.fund.save_issuance(closed, list(fund.issuance_rights.values()))
        fund.issuance = None
        fund.issuance_rights = {}
        self._save(fund)
        self._announce(
            day, headlines.issuance_closed(fund.ticker, closed.sold, closed.quotas)
        )

    # =========================
    # Recompra
    # =========================

    def open_buyback(
        self, ticker: str, quantity: Decimal, max_price: Decimal
    ) -> FundBuybackDTO:
        """Abre a recompra: uma ordem de compra da gestora no livro, paga com o caixa dela.

        As cotas compradas deixam de existir. O PL por cota conta o caixa reservado da ordem,
        e por isso ele só se move com o negócio.
        """
        fund = self._funds[ticker]
        self._sync_buyback(fund)
        account = fund.account
        if fund.nav is None or not fund.listed:
            raise ConflictError(
                "A recompra vale para uma gestora com a oferta pública aberta"
            )
        if account.offer_remaining is not None or fund.issuance is not None:
            raise ConflictError("Encerre a oferta ou a emissão antes de recomprar")
        if fund.buyback is not None:
            raise ConflictError("A gestora já tem uma recompra em aberto")
        if MERGE in fund.assemblies:
            raise ConflictError(
                "A gestora tem uma fusão em votação e não recompra cotas até o resultado"
            )
        if quantity <= 0 or quantity != quantity.to_integral_value():
            raise UnprocessableEntityError("Informe uma quantidade inteira de cotas")
        if quantity >= account.quotas:
            raise UnprocessableEntityError("A recompra não pode levar todas as cotas")
        price = max_price.quantize(Decimal("0.01"))
        if price <= 0:
            raise UnprocessableEntityError("O preço máximo precisa ser maior que zero")
        if self._engine.get_cash(account.client_id) < price * quantity:
            raise UnprocessableEntityError(
                "O caixa da gestora não cobre a recompra ao preço máximo"
            )

        today = self._engine.current_date
        buyback = repository.fund.create_buyback(
            fund.terms.id,
            FundBuybackDTO(
                id=0,
                announced_on=today,
                quantity=quantity,
                max_price=price,
                bought=Decimal(0),
                paid=Decimal(0),
                state="open",
            ),
        )
        order = LimitOrder(
            client_id=account.client_id,
            ticker=ticker,
            size=quantity,
            action=OrderAction.BUY,
            placed_on=today,
            price=float(price),
        )
        # A recompra existe antes do envio: a ordem pode casar já na submissão
        fund.buyback = buyback
        fund.buyback_order = order
        try:
            self._engine.matching_engine.submit(order)
        except Exception:
            self._finish_buyback(fund, "canceled")
            raise
        self._announce(today, headlines.buyback_opened(ticker, quantity, price))
        self._sync_buyback(fund)
        return buyback

    def cancel_buyback(self, ticker: str) -> None:
        """Cancela o resto da recompra: o caixa reservado volta e o que já foi comprado fica queimado."""
        fund = self._funds[ticker]
        self._sync_buyback(fund)
        order = fund.buyback_order
        if fund.buyback is None or order is None:
            raise ConflictError("A gestora não tem recompra em aberto")
        self._engine.matching_engine.cancel(
            order_id=order.id, client_id=order.client_id
        )
        self._sync_buyback(fund)

    def buyback_of(self, fund: Fund) -> FundBuybackDTO | None:
        """A recompra em aberto da gestora, com o estado de agora."""
        self._sync_buyback(fund)
        return fund.buyback

    def _sync_buyback(self, fund: Fund) -> None:
        """A recompra termina quando a ordem sai do livro: executada por inteiro ou cancelada."""
        order = fund.buyback_order
        if fund.buyback is None or order is None:
            return
        if order.status in (OrderStatus.PENDING, OrderStatus.PARTIAL):
            return
        self._finish_buyback(
            fund, "done" if order.status is OrderStatus.EXECUTED else "canceled"
        )

    def _finish_buyback(self, fund: Fund, state: Literal["done", "canceled"]) -> None:
        buyback = fund.buyback
        if buyback is None:
            return
        repository.fund.save_buyback(buyback.model_copy(update={"state": state}))
        fund.buyback = None
        fund.buyback_order = None

    def _record_buyback(self, ticker: str, size: Decimal, price: Decimal) -> None:
        """Cada compra da recompra soma as cotas queimadas e o que foi pago por elas."""
        fund = self._funds[ticker]
        buyback = fund.buyback
        if buyback is None:
            return
        fund.buyback = buyback.model_copy(
            update={
                "bought": buyback.bought + size,
                "paid": buyback.paid + size * price,
            }
        )
        repository.fund.save_buyback(fund.buyback)
        self._save(fund)

    # =========================
    # Assembleia
    # =========================

    def convene_assembly(
        self, ticker: str, convener: UserDTO, candidate_nickname: str | None
    ) -> None:
        """Convoca a assembleia de troca de gestor; com o próprio convocador indicado a votação abre já."""
        fund = self._funds[ticker]
        today = self._engine.current_date
        self._assemblies.convene(fund, convener, candidate_nickname, today)
        self._announce_voting_opened(fund, today)

    def answer_assembly_invite(self, ticker: str, user: UserDTO, accept: bool) -> None:
        """O aliado indicado aceita (a votação abre) ou recusa o convite."""
        fund = self._funds[ticker]
        today = self._engine.current_date
        self._assemblies.answer(fund, user, accept, today)
        self._announce_voting_opened(fund, today)

    def cancel_assembly(self, ticker: str, user: UserDTO) -> None:
        """Quem convocou cancela o convite que o aliado ainda não respondeu."""
        self._assemblies.cancel(self._funds[ticker], user, self._engine.current_date)

    def propose_fee_increase(
        self,
        ticker: str,
        proposer: UserDTO,
        management_fee: Decimal,
        performance_fee: Decimal,
    ) -> None:
        """O gestor principal leva um aumento de taxa à votação dos cotistas."""
        fund = self._funds[ticker]
        self._assemblies.propose_fee(
            fund, proposer, management_fee, performance_fee, self._engine.current_date
        )

    # =========================
    # Fusão
    # =========================

    def merge_block(
        self, fund: Fund, user: UserDTO
    ) -> tuple[FundAssemblyBlock | None, date | None]:
        """Por que `user` não propõe a fusão a partir desta gestora; nulo quando pode.

        Vale a gestora e a existência de outra que o mesmo gestor gere e que também esteja livre.
        """
        block, next_allowed = self._merge_fund_block(fund, user)
        if block is not None:
            return block, next_allowed
        if not self.merge_partners(fund, user):
            return "no_partner", None
        return None, None

    def _merge_fund_block(
        self, fund: Fund, user: UserDTO
    ) -> tuple[FundAssemblyBlock | None, date | None]:
        """Os impedimentos desta gestora para entrar numa fusão: os da assembleia, o congelamento do gestor e as ofertas em aberto."""
        block, next_allowed = self._assemblies.block_for(
            fund, user, self._engine.current_date, MERGE
        )
        if block is not None:
            return block, next_allowed
        frozen_until = self.frozen_until(fund)
        if frozen_until is not None:
            return "frozen", frozen_until
        if self._merge_busy(fund):
            return "busy", None
        return None, None

    def merge_partners(self, fund: Fund, user: UserDTO) -> list[Fund]:
        """As outras gestoras que `user` gere e que podem se fundir com esta: as duas livres de impedimento para a fusão."""
        if self._merge_fund_block(fund, user)[0] is not None:
            return []
        return [
            other
            for other in self.managed_by(user.id)
            if other is not fund and self._merge_fund_block(other, user)[0] is None
        ]

    def _merge_busy(self, fund: Fund) -> bool:
        """Se a gestora tem emissão, oferta, recompra ou oferta dirigida em aberto."""
        return (
            fund.issuance is not None
            or fund.account.offer_remaining is not None
            or fund.buyback is not None
            or fund.directed is not None
        )

    def propose_merge(
        self, mother_id: int, daughter_id: int, proposer: UserDTO
    ) -> None:
        """O gestor principal das duas leva a fusão às duas assembleias: a primeira incorpora a segunda."""
        if mother_id == daughter_id:
            raise UnprocessableEntityError("A fusão junta duas gestoras diferentes")
        mother = self.by_id(mother_id)
        daughter = self.by_id(daughter_id)
        for fund in (mother, daughter):
            block, next_allowed = self._merge_fund_block(fund, proposer)
            if block == "manager_only":
                raise ForbiddenError("Só o gestor propõe a fusão.")
            if block is not None:
                raise ConflictError(assembly_block_message(block, next_allowed))
        self._assemblies.propose_merge(
            mother, daughter, proposer, self._engine.current_date
        )

    def merge_preview(self, mother_id: int, daughter_id: int) -> FundMergePreviewDTO:
        """A troca de cotas e a incorporadora depois da fusão, pelos números de hoje."""
        mother = self.by_id(mother_id)
        daughter = self.by_id(daughter_id)
        valuation = self._merge_valuation(mother, daughter)
        ratio = self._merge_ratio(valuation.mother_nav, valuation.daughter_nav)
        quotas_after = (
            mother.account.quotas
            - valuation.cancelled_mother_quotas
            + converted_quotas(
                daughter.account.quotas - valuation.cancelled_daughter_quotas, ratio
            )
            if ratio is not None
            else None
        )
        return FundMergePreviewDTO(
            mother=self._merge_side(mother, valuation.mother_nav),
            daughter=self._merge_side(daughter, valuation.daughter_nav),
            ratio=ratio,
            mother_quotas=mother.account.quotas,
            daughter_quotas=daughter.account.quotas,
            quotas_after=quotas_after,
            equity_after=quotas_after * valuation.mother_nav
            if quotas_after is not None and valuation.mother_nav is not None
            else None,
        )

    @staticmethod
    def _merge_ratio(
        mother_nav: Decimal | None, daughter_nav: Decimal | None
    ) -> Decimal | None:
        if mother_nav is None or daughter_nav is None or mother_nav <= 0:
            return None
        return exchange_ratio(daughter_nav, mother_nav)

    def _merge_valuation(self, mother: Fund, daughter: Fund) -> MergeValuation:
        """O PL por cota das duas e as cotas cruzadas que a fusão cancela.

        A cota de uma que está na carteira da outra vale o PL por cota da primeira, e não o
        preço de mercado: o PL por cota de cada gestora sai das duas contas resolvidas juntas.
        """
        held_by_mother = self._held_quotas(mother, daughter)
        held_by_daughter = self._held_quotas(daughter, mother)
        navs = circular_navs(
            self._assets_without(mother, daughter),
            self._assets_without(daughter, mother),
            mother.account.quotas,
            daughter.account.quotas,
            held_by_mother,
            held_by_daughter,
        )
        mother_nav, daughter_nav = navs if navs is not None else (None, None)
        return MergeValuation(
            mother_nav=mother_nav,
            daughter_nav=daughter_nav,
            cancelled_daughter_quotas=held_by_mother,
            cancelled_mother_quotas=held_by_daughter,
        )

    def _held_quotas(self, holder: Fund, other: Fund) -> Decimal:
        """As cotas de `other` na carteira da gestora `holder`."""
        position = self._engine.broker.get_positions(holder.account.client_id).get(
            other.ticker
        )
        return position.size if position is not None else Decimal(0)

    def _assets_without(self, fund: Fund, other: Fund) -> Decimal:
        """O patrimônio líquido da carteira de `fund` sem as cotas de `other` que ela tenha."""
        engine = self._engine
        balance = engine.balance_sheet(fund.account.client_id)
        net = (
            balance.total_cash
            + self._reserved_for_buyback(fund)
            + balance.total_equity
            + balance.total_fixed
            - balance.total_debt
        )
        position = engine.broker.get_positions(fund.account.client_id).get(other.ticker)
        if position is not None and position.size > 0:
            net -= engine.get_current_price(position) * position.size
        return net

    def _merge_side(self, fund: Fund, nav: Decimal | None) -> FundMergeSideDTO:
        return FundMergeSideDTO(
            fund_id=fund.terms.id,
            ticker=fund.ticker,
            name=fund.terms.name,
            nav=nav,
            cash=self._engine.get_cash(fund.account.client_id),
        )

    def merge_title(self, assembly: FundAssemblyDTO) -> str:
        """O que a fusão da votação faz com esta gestora, para o título da pendência: incorporar a outra ou ser incorporada por ela."""
        partner_id = assembly.partner_fund_id or 0
        partner = self._fund_by_id(partner_id)
        merged = self._merged.get(partner_id)
        name = (
            partner.terms.name
            if partner is not None
            else merged.name
            if merged is not None
            else "outra gestora"
        )
        return (
            f"ser incorporada pela {name}"
            if assembly.absorbed
            else f"incorporar a {name}"
        )

    def _fund_by_id(self, fund_id: int) -> Fund | None:
        return next((f for f in self._funds.values() if f.terms.id == fund_id), None)

    def _merge_plan(self, mother: Fund, daughter: Fund) -> MergePlan:
        """A troca de cotas e a saída de quem votou contra na incorporada, pelos números e votos de agora."""
        valuation = self._merge_valuation(mother, daughter)
        exits: list[MergeExit] = []
        if valuation.daughter_nav is not None:
            votes = daughter.assembly_votes.get(MERGE, {})
            price = exit_price(valuation.daughter_nav)
            exits = [
                MergeExit(user_id, quotas, price * quotas)
                for user_id, quotas in self._assemblies.holdings(daughter).items()
                if votes.get(user_id) is False
            ]
        return MergePlan(
            mother_nav=valuation.mother_nav,
            daughter_nav=valuation.daughter_nav,
            ratio=self._merge_ratio(valuation.mother_nav, valuation.daughter_nav),
            exits=exits,
            cash=settle_exits(
                sum((e.amount for e in exits), Decimal(0)),
                self._engine.get_cash(daughter.account.client_id),
                self._engine.get_cash(mother.account.client_id),
            ),
            cancelled_daughter_quotas=valuation.cancelled_daughter_quotas,
            cancelled_mother_quotas=valuation.cancelled_mother_quotas,
        )

    def _merge_view(
        self, fund: Fund, assembly: FundAssemblyDTO
    ) -> FundAssemblyMergeDTO | None:
        """A fusão da votação como a gestora `fund` a vê: as duas pontas, a troca e a saída de quem vota contra."""
        if assembly.agenda is not MERGE or assembly.partner_fund_id is None:
            return None
        other = self._fund_by_id(assembly.partner_fund_id)
        if other is None:
            return None
        mother, daughter = (other, fund) if assembly.absorbed else (fund, other)
        plan = self._merge_plan(mother, daughter)
        partner_score = self._assemblies.score(other, MERGE)
        voted = partner_score.in_favor + partner_score.against
        return FundAssemblyMergeDTO(
            mother=self._merge_side(mother, plan.mother_nav),
            daughter=self._merge_side(daughter, plan.daughter_nav),
            is_mother=fund is mother,
            ratio=plan.ratio,
            partner_tally=FundAssemblyTallyDTO(
                in_favor=partner_score.in_favor,
                against=partner_score.against,
                abstention=partner_score.abstention,
                total=partner_score.total,
                missing_to_win=partner_score.missing_to_win,
            ),
            partner_voted_share=ratio(voted, partner_score.total),
            partner_in_favor_share=partner_score.in_favor / voted
            if voted > 0
            else None,
            exit_quotas=plan.exit_quotas,
            exit_amount=plan.cash.total,
            shortfall=plan.cash.shortfall,
        )

    def _advance_merges(self, today: date) -> None:
        """O fechamento das fusões que chegaram ao último pregão: as duas assembleias apuradas juntas."""
        for mother in [
            f
            for f in self._funds.values()
            if (a := f.assemblies.get(MERGE)) is not None
            and not a.absorbed
            and self._assemblies.merge_ready(f, today)
        ]:
            assembly = mother.assemblies[MERGE]
            daughter = (
                self._fund_by_id(assembly.partner_fund_id)
                if assembly.partner_fund_id is not None
                else None
            )
            if daughter is None or MERGE not in daughter.assemblies:
                self._assemblies.close_merge(mother, today, approved=False)
                continue
            self._close_merge(mother, daughter, today)

    def _close_merge(self, mother: Fund, daughter: Fund, today: date) -> None:
        """A fusão passa quando as duas assembleias aprovam e os dois caixas cobrem a saída de quem votou contra; senão as gestoras seguem separadas."""
        # A taxa a pagar sai do caixa antes de a saída ser calculada sobre ele
        self.settle_payable(mother)
        self.settle_payable(daughter)
        won = (
            self._assemblies.score(mother, MERGE).wins
            and self._assemblies.score(daughter, MERGE).wins
        )
        # Com as duas assembleias a favor, o rendimento já apurado das duas é pago aos cotistas de
        # hoje antes de o plano medir caixa e PL por cota: a saída e a razão de troca partem do
        # patrimônio sem esse dinheiro, e as cotas convertidas nascem sem direito a ele
        if won:
            self._pay_distribution(daughter, today)
            self._pay_distribution(mother, today)
        plan = self._merge_plan(mother, daughter)
        voted = won and plan.ratio is not None
        approved = voted and plan.cash.shortfall == 0
        # A fusão que ganhou no voto e caiu por falta de caixa guarda o quanto faltou
        shortfall = plan.cash.shortfall if voted else Decimal(0)
        self._assemblies.close_merge(mother, today, approved, shortfall)
        self._assemblies.close_merge(daughter, today, approved, shortfall)
        if approved:
            self._merge(mother, daughter, plan, today)

    def _merge(
        self, mother: Fund, daughter: Fund, plan: MergePlan, today: date
    ) -> None:
        """A incorporadora fica com tudo da incorporada e os cotistas dela trocam as cotas; a incorporada deixa o mercado.

        A ordem é a do dinheiro: quem votou contra sai pelo caixa da incorporada, o caixa que
        sobra passa à incorporadora, que completa o que faltou do próprio, e só depois entram as
        posições, a renda fixa e as dívidas. As cotas que uma gestora tinha da outra são
        canceladas antes da troca: a incorporadora não recebe conversão por elas e o PL por cota
        do plano já as contou pelo valor patrimonial, o que deixa quem fica sem ganho nem perda.
        """
        if plan.ratio is None or plan.daughter_nav is None or plan.mother_nav is None:
            return
        engine = self._engine
        broker = engine.broker
        d_client = daughter.account.client_id
        m_client = mother.account.client_id
        engine.matching_engine.cancel_ticker(daughter.ticker)
        engine.matching_engine.cancel_all(d_client)
        # A estratégia automática da incorporada acaba com ela
        self._stop_automatic(daughter, "A gestora foi incorporada: o automático acabou")
        # Saída de quem votou contra: venda das cotas ao PL por cota, paga pelo caixa da incorporada
        price = exit_price(plan.daughter_nav)
        for leaving in plan.exits:
            broker.sell_to_fund(
                self._client_of_user(leaving.user_id),
                daughter.ticker,
                leaving.quotas,
                price,
            )
        if plan.cash.from_daughter > 0:
            engine.charge_fund_merge_exit(d_client, plan.cash.from_daughter)
        # O caixa que sobrou na incorporada passa à incorporadora, e ela completa a saída
        leftover = engine.get_cash(d_client)
        if leftover > 0:
            engine.merge_cash(d_client, m_client, leftover)
        elif leftover < 0:
            engine.merge_cash(m_client, d_client, -leftover)
        if plan.cash.from_mother > 0:
            engine.charge_fund_merge_exit(m_client, plan.cash.from_mother)

        # As cotas cruzadas deixam de existir, uma em cada lado
        daughter.account.burn(broker.cancel_position(m_client, daughter.ticker))
        mother.account.burn(broker.cancel_position(d_client, mother.ticker))

        # A carteira: ações, renda fixa e empréstimos
        for ticker, position in list(broker.get_positions(d_client).items()):
            if position.size > 0:
                broker.merge_position(d_client, m_client, ticker, position.size)
        engine.fixed_broker.transfer_all(d_client, m_client)
        engine.credit_book.transfer_loans(d_client, m_client)

        # Os cotistas da incorporada trocam as cotas; o que não fecha uma cota inteira vem em dinheiro
        issued = Decimal(0)
        for holder, quotas in self._holders(daughter):
            converted = converted_quotas(quotas, plan.ratio)
            remainder = conversion_remainder(
                quotas, plan.daughter_nav, converted, plan.mother_nav
            )
            broker.convert_position(holder, daughter.ticker, mother.ticker, converted)
            if remainder > 0:
                engine.merge_cash(m_client, holder, remainder)
            issued += converted
        maker_issued = converted_quotas(daughter.account.maker_quotas, plan.ratio)
        mother.account.quotas += issued + maker_issued
        mother.account.receive_maker(maker_issued)

        # A taxa que a incorporada ainda devia passa a dever à incorporadora
        mother.terms = mother.terms.model_copy(
            update={
                "management_fee_payable": mother.terms.management_fee_payable
                + daughter.terms.management_fee_payable,
                "performance_fee_payable": mother.terms.performance_fee_payable
                + daughter.terms.performance_fee_payable,
            }
        )
        daughter.terms = daughter.terms.model_copy(
            update={
                "management_fee_payable": Decimal(0),
                "performance_fee_payable": Decimal(0),
            }
        )
        self._publish_fee_payable(daughter)
        self._publish_fee_payable(mother)

        # Os convites de co-gestão sem resposta caem com a incorporada
        for invited in [
            c for c in daughter.comanagers if c.status is FundComanagerStatus.INVITED
        ]:
            self._comanagers.drop(daughter, invited.user_id)

        # A incorporada deixa o mercado: a gestora sai dos mapas vivos e guarda só o registro
        daughter.account.quotas = Decimal(0)
        daughter.account.maker_quotas = Decimal(0)
        daughter.terms = daughter.terms.model_copy(
            update={"merged_into_fund_id": mother.terms.id, "merged_on": today}
        )
        self._save(daughter)
        self._funds.pop(daughter.ticker, None)
        self._accounts.pop(daughter.ticker, None)
        engine.broker.maker_accounts.pop(daughter.ticker, None)
        engine.fund_references.pop(daughter.ticker, None)
        engine.ranking_prices.pop(daughter.ticker, None)
        self._takeover_orders.pop(daughter.ticker, None)
        self._merged[daughter.terms.id] = daughter.terms

        mother.nav = self._nav(mother)
        self._save(mother)
        self._announce(
            today,
            headlines.funds_merged(
                mother.ticker, daughter.ticker, plan.ratio, plan.exit_quotas
            ),
        )

    def _cancel_merge(self, fund: Fund) -> None:
        """A fusão é do gestor principal das duas: com a gestão mudando de mãos as duas votações encerram sem resultado."""
        assembly = fund.assemblies.get(MERGE)
        if assembly is None:
            return
        today = self._engine.current_date
        partner = (
            self._fund_by_id(assembly.partner_fund_id)
            if assembly.partner_fund_id is not None
            else None
        )
        self._assemblies.cancel_open(fund, MERGE, today)
        if partner is not None:
            self._assemblies.cancel_open(partner, MERGE, today)

    def cast_assembly_vote(
        self, ticker: str, agenda: FundAssemblyAgenda, user: UserDTO, in_favor: bool
    ) -> None:
        """O cotista vota na pauta aberta; mudar o voto vale até o fim."""
        self._assemblies.vote(
            self._funds[ticker], agenda, user, in_favor, self._engine.current_date
        )

    def open_votes_for(self, user: UserDTO) -> list[tuple[Fund, FundAssemblyDTO]]:
        """As votações abertas em que `user` pode votar e ainda não votou, com a gestora de cada uma."""
        return [
            (fund, assembly)
            for fund in self._funds.values()
            for assembly in self._assemblies.open_votes_for(fund, user)
        ]

    def assembly_panel(
        self,
        fund: Fund,
        viewer: UserDTO,
        nicknames: Mapping[int, str],
        colors: Mapping[int, str],
    ) -> FundAssemblyPanelDTO:
        """A seção Assembleia da gestora como `viewer` a vê."""
        partners = {
            other.terms.id: (other.ticker, other.terms.name)
            for other in self._funds.values()
        } | {terms.id: (terms.ticker, terms.name) for terms in self._merged.values()}
        panel = self._assemblies.panel(
            fund,
            viewer,
            self._engine.current_date,
            nicknames,
            colors,
            self._merge_view,
            partners,
            [
                self._merge_side(other, self._merge_valuation(fund, other).daughter_nav)
                for other in self.merge_partners(fund, viewer)
            ],
        )
        # A fusão depende da outra gestora: o bloqueio dela vem daqui
        block, next_allowed = self.merge_block(fund, viewer)
        options = [
            FundAssemblyOptionDTO(
                agenda=MERGE,
                can_convene=block is None,
                block=block,
                next_allowed_on=next_allowed,
            )
            if option.agenda is MERGE
            else option
            for option in panel.options
        ]
        return panel.model_copy(update={"options": options})

    def invites_for(self, user: UserDTO) -> list[tuple[Fund, FundAssemblyDTO, str]]:
        """Os convites de assembleia que esperam a resposta de `user`: a gestora, o convite e o apelido de quem convocou."""
        names = self._nicknames()
        return [
            (fund, invite, names.get(invite.convener_user_id, "?"))
            for fund in self._funds.values()
            if (invite := fund.assemblies.get(SWAP)) is not None
            and invite.status is FundAssemblyStatus.INVITED
            and invite.candidate_user_id == user.id
        ]

    # =========================
    # Co-gestores
    # =========================

    def invite_comanager(
        self, ticker: str, nickname: str, share: Decimal
    ) -> FundComanagerDTO:
        """O principal convida um jogador a co-gestor, reservando a parte dele nas taxas."""
        return self._comanagers.invite(
            self._funds[ticker], nickname, share, self._engine.current_date
        )

    def seat_comanager(self, ticker: str, user_id: int, share: Decimal) -> None:
        """O co-gestor combinado no lobby entra ativo na gestora recém-fundada."""
        self._comanagers.seat(
            self._funds[ticker], user_id, share, self._engine.current_date
        )

    def answer_comanager_invite(
        self, ticker: str, user: UserDTO, accept: bool
    ) -> FundComanagerDTO:
        """O convidado aceita (a parte vale nas taxas do mês seguinte) ou recusa.

        Com a gestora congelada pela presidência do principal, o co-gestor que aceita assume
        na hora, com o presidente em licença, e a carteira descongela.
        """
        fund = self._funds[ticker]
        answered = self._comanagers.answer(
            fund, user, accept, self._engine.current_date
        )
        president_id = fund.terms.manager_user_id
        if (
            accept
            and self.frozen_until(fund) is not None
            and self._manager_frozen_until(user.id) is None
        ):
            self._hand_over(fund, answered, answered.future_share, president_id)
        return answered

    def change_comanager_share(
        self, ticker: str, user_id: int, share: Decimal
    ) -> FundComanagerDTO:
        """Pede a parte nova do co-gestor, que vale nas taxas do mês seguinte."""
        return self._comanagers.change_share(
            self._funds[ticker], user_id, share, self._engine.current_date
        )

    def remove_comanager(self, ticker: str, user_id: int) -> FundComanagerDTO:
        """O principal tira o co-gestor ou retira o convite; o acesso acaba no mesmo pregão."""
        fund = self._funds[ticker]
        removed = self._comanagers.remove(fund, user_id, self._engine.current_date)
        self._directed.cancel_of(fund, user_id)
        return removed

    def leave_comanagement(self, ticker: str, user: UserDTO) -> None:
        """O co-gestor deixa a gestão; o acesso acaba no mesmo pregão."""
        fund = self._funds[ticker]
        self._comanagers.leave(fund, user, self._engine.current_date)
        self._directed.cancel_of(fund, user.id)

    def comanager_invites_for(
        self, user: UserDTO
    ) -> list[tuple[Fund, FundComanagerDTO, str, date]]:
        """Os convites de co-gestão que esperam `user`: a gestora, o convite, o apelido do principal e o último dia dele."""
        names = self._nicknames()
        return [
            (
                fund,
                comanager,
                names.get(fund.terms.manager_user_id, "?"),
                expires_on(comanager),
            )
            for fund in self._funds.values()
            for comanager in fund.comanagers
            if comanager.user_id == user.id
            and comanager.status is FundComanagerStatus.INVITED
        ]

    def founding_blocked_until(self, user_id: int) -> date | None:
        """Até quando o gestor afastado por assembleia não funda outra gestora."""
        return self._assemblies.founding_blocked_until(
            user_id, self._engine.current_date
        )

    def _announce_voting_opened(self, fund: Fund, today: date) -> None:
        """A manchete da convocação sai quando a votação abre."""
        assembly = fund.assemblies.get(SWAP)
        if (
            assembly is None
            or assembly.status is not FundAssemblyStatus.VOTING
            or assembly.candidate_user_id is None
        ):
            return
        names = self._nicknames()
        self._announce(
            today,
            headlines.assembly_called(
                fund.ticker,
                names.get(assembly.convener_user_id, "?"),
                names.get(assembly.candidate_user_id, "?"),
                assembly.ends_on,
            ),
        )

    def _advance_assembly(self, fund: Fund, today: date) -> None:
        """O fechamento do pregão da assembleia: o convite sem resposta cai e a votação do
        último pregão é apurada; se a troca vence, o candidato assume na hora, e o aumento de
        taxa aprovado vale no mês seguinte ao resultado."""
        self._assemblies.expire_invite(fund, today)
        for agenda in FundAssemblyAgenda:
            closed = self._assemblies.close_voting(fund, agenda, today)
            if closed is not None:
                self._apply_outcome(fund, closed[0], today)

    def _apply_outcome(
        self, fund: Fund, assembly: FundAssemblyDTO, today: date
    ) -> None:
        """Aplica o desfecho da pauta que acabou de fechar."""
        if assembly.agenda is FEE:
            self._apply_fee_outcome(fund, assembly, today)
            return
        candidate_id = assembly.candidate_user_id
        if candidate_id is None:
            return
        names = self._nicknames()
        if assembly.status is FundAssemblyStatus.REPLACED:
            self._replace_manager(fund, candidate_id)
            self._announce(
                today,
                headlines.assembly_replaced(
                    fund.ticker,
                    names.get(assembly.previous_manager_user_id, "?"),
                    names.get(candidate_id, "?"),
                ),
            )
            if (
                self._manager_cap is not None
                and assembly.previous_manager_user_id == fund.terms.founder_user_id
            ):
                self._eliminate(assembly.previous_manager_user_id, fund, today)
        else:
            self._announce(
                today,
                headlines.assembly_kept(
                    fund.ticker, names.get(assembly.previous_manager_user_id, "?")
                ),
            )

    def _apply_fee_outcome(
        self, fund: Fund, assembly: FundAssemblyDTO, today: date
    ) -> None:
        """A taxa aprovada fica pendente e vale no primeiro dia útil do mês seguinte ao resultado."""
        if (
            assembly.status is not FundAssemblyStatus.APPROVED
            or assembly.closed_on is None
            or assembly.proposed_management_fee is None
            or assembly.proposed_performance_fee is None
        ):
            return
        fund.terms = fund.terms.model_copy(
            update={
                "pending_management_fee": assembly.proposed_management_fee,
                "pending_performance_fee": assembly.proposed_performance_fee,
                "pending_from": next_month_turn(assembly.closed_on),
            }
        )
        self._save(fund)
        if assembly.proposed_management_fee != assembly.previous_management_fee:
            self._announce(
                today,
                headlines.management_fee_changed(
                    fund.ticker, assembly.proposed_management_fee
                ),
            )
        if assembly.proposed_performance_fee != assembly.previous_performance_fee:
            self._announce(
                today,
                headlines.performance_fee_changed(
                    fund.ticker, assembly.proposed_performance_fee
                ),
            )

    def _eliminate(self, user_id: int, lost: Fund, today: date) -> None:
        """Quem perde a assembleia da gestora que fundou sai da disputa: as ordens dele saem do
        livro e as outras gestoras que ele gere passam ao maior cotista ativo de cada uma."""
        self._eliminated.setdefault(user_id, today)
        self._engine.matching_engine.cancel_all(self._client_of_user(user_id))
        for fund in self._funds.values():
            if fund is lost or fund.terms.manager_user_id != user_id:
                continue
            holders = {
                holder: size
                for holder, size in self._assemblies.holdings(fund).items()
                if holder not in self._eliminated
            }
            if holders:
                self._replace_manager(fund, max(holders, key=lambda h: holders[h]))

    def _replace_manager(self, fund: Fund, manager_user_id: int) -> None:
        """O candidato assume: as ordens do gestor afastado saem do livro e a recompra dele cai.

        A proposta de aumento de taxa é do gestor que sai: a votação dela encerra sem resultado.
        """
        self._sync_buyback(fund)
        # A estratégia da carteira é do principal que sai: a gestora volta ao manual
        self._stop_automatic(fund, "A gestão mudou de mãos: a gestora voltou ao manual")
        self._assemblies.cancel_open(fund, FEE, self._engine.current_date)
        self._cancel_merge(fund)
        # A oferta de cotas é do principal que sai
        self._directed.cancel(fund)
        # O candidato que já era co-gestor passa a principal e deixa a lista deles
        if any(c.user_id == manager_user_id for c in fund.comanagers):
            self._comanagers.drop(fund, manager_user_id)
        # A gestão muda de mão no dia de hoje: o "desde" do novo gestor começa aqui. Quem
        # estava em licença só retoma por `on_leave_office`: qualquer outra troca encerra a licença
        fund.terms = fund.terms.model_copy(
            update={
                "manager_user_id": manager_user_id,
                "manager_since": self._engine.current_date,
                "leave_manager_user_id": None,
                "leave_heir_share": None,
            }
        )
        self._engine.matching_engine.cancel_all(fund.account.client_id)
        self._finish_buyback(fund, "canceled")

    def _nicknames(self) -> dict[int, str]:
        return {user.id: user.nickname for user in self.participants()}

    def on_office(self, manager_user_id: int) -> None:
        """O gestor assumiu a presidência: as ordens abertas das gestoras dele saem do livro.

        Com co-gestor ativo a gestora segue operando: o de maior parte vira o principal e o
        presidente sai da gestão em licença, com a parte do herdeiro guardada para `on_leave_office`.
        Sem co-gestor ela congela até o fim do mandato, salvo com a estratégia ligada, que mantém
        a carteira operando.
        """
        for fund in self._funds.values():
            if fund.terms.manager_user_id != manager_user_id:
                continue
            self._engine.matching_engine.cancel_all(fund.account.client_id)
            heir = heir_of(fund)
            if heir is None:
                continue
            self._hand_over(fund, heir, heir.share, manager_user_id)

    def _hand_over(
        self,
        fund: Fund,
        heir: FundComanagerDTO,
        heir_share: Decimal,
        president_id: int,
    ) -> None:
        """O herdeiro vira o principal e o presidente sai em licença, com a parte do herdeiro guardada para o retorno."""
        self._comanagers.succeed(fund, heir, self._engine.current_date)
        self._replace_manager(fund, heir.user_id)
        fund.terms = fund.terms.model_copy(
            update={
                "leave_manager_user_id": president_id,
                "leave_heir_share": heir_share,
            }
        )
        self._save(fund)

    def on_leave_office(self, president_id: int) -> None:
        """O presidente deixou a presidência sem reeleição (fim do mandato ou impeachment): a gestão volta a ele.

        Retoma a gestora que passou ao herdeiro, desde que o gestor de hoje ainda seja o herdeiro
        da posse (a troca por assembleia encerra a licença). O herdeiro volta a co-gestor com a
        parte de antes. A gestora que congelou sem herdeiro já volta a operar sozinha, porque o
        congelamento acaba junto com o mandato.
        """
        today = self._engine.current_date
        for fund in self._funds.values():
            # A gestora que seguiu no automático sob o presidente volta ao manual com o fim do mandato
            if fund.terms.manager_user_id == president_id:
                self._stop_automatic(
                    fund, "O mandato acabou: a gestora voltou ao manual"
                )
            if fund.terms.leave_manager_user_id != president_id:
                continue
            heir_id = fund.terms.manager_user_id
            heir_share = fund.terms.leave_heir_share
            self._replace_manager(fund, president_id)
            if heir_share is not None:
                self._comanagers.restore(fund, heir_id, heir_share, today)
            self._save(fund)

    def set_fees(
        self, ticker: str, management_fee: Decimal, performance_fee: Decimal
    ) -> None:
        """Pede as taxas novas, que valem no primeiro dia útil do mês seguinte.

        Pedir as taxas de hoje desfaz o pedido pendente. Cada taxa que muda vira manchete quando
        a gestora já é pública. Subir taxa de gestora com cotistas passa pela assembleia
        (`propose_fee_increase`); baixar vale sem votação.
        """
        fund = self._funds[ticker]
        if fund.listed and raises_fee(fund, management_fee, performance_fee):
            raise ConflictError(
                "Subir taxa de uma gestora com cotistas vai à assembleia: leve a proposta à votação"
            )
        terms = fund.terms
        today = self._engine.current_date
        management_changed = management_fee != terms.management_fee
        performance_changed = performance_fee != terms.performance_fee
        changed = management_changed or performance_changed
        # A data de vigência é uma só para tudo o que está pendente, o rendimento incluído
        rate_pending = terms.pending_distribution_rate is not None
        fund.terms = terms.model_copy(
            update={
                "pending_management_fee": management_fee if changed else None,
                "pending_performance_fee": performance_fee if changed else None,
                "pending_from": next_month_turn(today)
                if changed or rate_pending
                else None,
            }
        )
        self._save(fund)
        if not fund.listed:
            return
        if management_changed:
            self._announce(
                today, headlines.management_fee_changed(ticker, management_fee)
            )
        if performance_changed:
            self._announce(
                today, headlines.performance_fee_changed(ticker, performance_fee)
            )

    def set_distribution(self, ticker: str, rate: Decimal) -> None:
        """Pede a nova parte distribuída do lucro realizado, que vale no primeiro dia útil do mês seguinte.

        Pedir a parte de hoje desfaz o pedido pendente.
        """
        fund = self._funds[ticker]
        terms = fund.terms
        today = self._engine.current_date
        changed = rate != terms.distribution_rate
        fees_pending = terms.pending_management_fee is not None
        fund.terms = terms.model_copy(
            update={
                "pending_distribution_rate": rate if changed else None,
                "pending_from": next_month_turn(today)
                if changed or fees_pending
                else None,
            }
        )
        self._save(fund)

    # =========================
    # Dia
    # =========================

    def on_open(self, today: date) -> None:
        """O PL de cada gestora com cota e as ordens do formador e da oferta, refeitas em volta dele.

        O preço de ranking vale desde já na carteira de quem tem a cota.
        """
        for fund in self._funds.values():
            # A taxa a pagar é a primeira a sair do caixa; o rendimento apurado na data-com
            # paga só o que sobra, e os dois saem antes de o PL do dia ser calculado
            self.settle_payable(fund)
            self._pay_distribution(fund, today)
            nav = self._nav(fund)
            if nav is None:
                self._engine.fund_references.pop(fund.ticker, None)
                continue
            fund.nav = nav
            self._engine.ranking_prices[fund.ticker] = ranking_price(fund.days, nav)
            if fund.listed:
                self._sync_buyback(fund)
                self._advance_issuance(fund, today)
                self._refresh_orders(fund, today)
                self._engine.fund_references[fund.ticker] = self._reference(
                    fund, nav, today
                )
                self._seed_candle(fund, nav, today)
            else:
                self._engine.fund_references.pop(fund.ticker, None)
            self._advance_takeover(fund, today)

    def on_close(self, today: date) -> list[CandleDTO]:
        """Fecha o pregão das gestoras listadas: vela, fechamento do dia, preço de ranking e estado.

        Devolve as velas do dia, para o tempo real das cotas.
        """
        candles: list[CandleDTO] = []
        for fund in self._funds.values():
            # O convite de co-gestão vence também na gestora que ainda não abriu a oferta
            invites = self._comanagers.expire_invites(fund, today)
            if self._directed.expire(fund, today) or invites:
                self._save(fund)
            if fund.nav is None or not fund.listed:
                continue
            self._settle_takeover(fund, today)
            trades = fund.account.take_day()
            stock = self._engine.stocks[fund.ticker]
            candle = close_candle(stock, today, trades, fund.last_close, fund.nav)
            fund.last_close = candle.close
            if trades.open is not None:
                fund.last_trade_price = trades.close
            fund.days = [*fund.days, TradedDay(trades.quantity, trades.value)][
                -RANKING_WINDOW:
            ]
            fund.navs = cut_window([*fund.navs, NavPoint(today, fund.nav)])
            ranking = ranking_price(fund.days, fund.nav)
            self._engine.ranking_prices[fund.ticker] = ranking

            repository.fund.save_candle(self._simulation_id, candle)
            repository.fund.save_day(
                fund.terms.id,
                FundDayDTO(
                    day=today,
                    nav=fund.nav,
                    quotas=fund.account.quotas,
                    traded_quantity=trades.quantity,
                    traded_value=trades.value,
                    ranking_price=ranking,
                    fee_payable=fund.terms.fee_payable,
                    loan_debt=self._engine.credit_book.loan_debt(
                        fund.account.client_id, today
                    ),
                ),
            )
            self._engine.update_market_data([candle])
            # A oferta vale até o fim do último pregão dela; o que não vendeu não nasce
            listed_on = fund.terms.listed_on
            if (
                listed_on is not None
                and fund.issuance is None
                and fund.account.offer_remaining is not None
                and today >= offer_ends_on(listed_on)
            ):
                self._close_offer(fund, today)
            # A emissão vale até o fim do último pregão da sobra, ou até vender tudo
            issuance = fund.issuance
            if issuance is not None and (
                today >= issuance.ends_on or issuance.sold >= issuance.quotas
            ):
                self._close_issuance(fund, today)
            self._advance_assembly(fund, today)
            self._sync_buyback(fund)
            self._settle_distribution(fund, today)
            self._save(fund)
            candles.append(candle)
        self._advance_merges(today)
        return candles

    def on_month(self, today: date) -> None:
        """Vira as taxas pedidas e cobra as do mês: administração todo mês e performance a cada semestre."""
        for fund in self._funds.values():
            self._apply_pending(fund, today)
            self._comanagers.apply_pending(fund, today)
            if (
                not fund.listed
                or fund.nav is None
                or self.frozen_until(fund) is not None
            ):
                continue
            self._charge_management(fund)
            self._charge_performance(fund, today)
            self._save(fund)

    # =========================
    # Taxas
    # =========================

    def _apply_pending(self, fund: Fund, today: date) -> None:
        terms = fund.terms
        if terms.pending_from is None or terms.pending_from > today:
            return
        fund.terms = terms.model_copy(
            update={
                "distribution_rate": terms.pending_distribution_rate
                if terms.pending_distribution_rate is not None
                else terms.distribution_rate,
                "pending_distribution_rate": None,
                "management_fee": terms.pending_management_fee
                if terms.pending_management_fee is not None
                else terms.management_fee,
                "performance_fee": terms.pending_performance_fee
                if terms.pending_performance_fee is not None
                else terms.performance_fee,
                "pending_management_fee": None,
                "pending_performance_fee": None,
                "pending_from": None,
            }
        )
        self._save(fund)

    def _charge_management(self, fund: Fund) -> None:
        if fund.nav is None:
            return
        fee = management_fee(
            fund.nav, fund.account.outside_quotas, fund.terms.management_fee
        )
        self._pay(fund, fee, performance=False)

    def _charge_performance(self, fund: Fund, today: date) -> None:
        terms = fund.terms
        if (
            fund.nav is None
            or terms.listed_on is None
            or terms.high_water_mark is None
            or terms.high_water_mark_on is None
        ):
            return
        base = terms.last_performance_on or terms.listed_on
        if months_between(base, today) < PERFORMANCE_PERIOD_MONTHS:
            return
        charge = performance_charge(
            nav=fund.nav,
            quotas=fund.account.quotas,
            outside_quotas=fund.account.outside_quotas,
            rate=terms.performance_fee,
            high_water_mark=terms.high_water_mark,
            high_water_mark_on=terms.high_water_mark_on,
            today=today,
            cdi_growth=cdi_growth(terms.high_water_mark_on, today),
            drained_per_quota=drained_since(
                fund.distributions, terms.high_water_mark_on, fund.account.quotas
            ),
        )
        self._pay(fund, charge.fee, performance=True)
        fund.terms = fund.terms.model_copy(
            update={
                "high_water_mark": charge.high_water_mark,
                "high_water_mark_on": charge.high_water_mark_on,
                "last_performance_on": today,
            }
        )

    def _pay(self, fund: Fund, fee: Decimal, *, performance: bool) -> None:
        """A taxa sai do caixa da gestora até onde o caixa alcança; o resto vira taxa a pagar.

        A taxa inteira abate o lucro realizado do mês.
        """
        if fee <= 0:
            return
        paid, owed = split_payable(fee, self._engine.get_cash(fund.account.client_id))
        self._transfer_fee(fund, paid, performance=performance)
        update = {"month_fees": fund.terms.month_fees + fee}
        if owed > 0:
            column = _payable_column(performance)
            update[column] = getattr(fund.terms, column) + owed
        fund.terms = fund.terms.model_copy(update=update)

    def settle_payable(self, fund: Fund) -> None:
        """A taxa a pagar sai do caixa positivo antes de qualquer outro uso: administração primeiro, depois performance."""
        client_id = fund.account.client_id
        update: dict[str, Decimal] = {}
        for performance in (False, True):
            column = _payable_column(performance)
            paid, rest = split_payable(
                getattr(fund.terms, column), self._engine.get_cash(client_id)
            )
            if paid > 0:
                self._transfer_fee(fund, paid, performance=performance)
                update[column] = rest
        if update:
            fund.terms = fund.terms.model_copy(update=update)
            self._save(fund)

    def _transfer_fee(self, fund: Fund, amount: Decimal, *, performance: bool) -> None:
        """O valor sai do caixa da gestora e entra, dividido pelas partes, no caixa pessoal de quem a gere."""
        if amount <= 0:
            return
        self._engine.charge_fund_fee(fund.account.client_id, amount, performance)
        for user_id, share in split_fee(fund, amount):
            if share > 0:
                self._engine.receive_fund_fee(
                    self._client_of_user(user_id), share, performance
                )

    # =========================
    # Rendimentos mensais
    # =========================

    def _record_realized(
        self, client_id: UUID, kind: RealizedKind, amount: Decimal
    ) -> None:
        """Soma ao mês da gestora o lucro que a carteira dela acabou de realizar."""
        fund = self.of_client(client_id)
        if fund is None or not fund.listed:
            return
        column = _REALIZED_FIELDS[kind]
        fund.terms = fund.terms.model_copy(
            update={column: getattr(fund.terms, column) + amount}
        )

    def _settle_distribution(self, fund: Fund, today: date) -> None:
        """A data-com, no último pregão do mês: apura o rendimento por cota e zera o mês."""
        if not is_data_com(today):
            return
        terms = fund.terms
        settlement = settle_month(
            dividends=terms.month_dividends,
            interest=terms.month_interest,
            sales_gain=terms.month_sales_gain,
            fees=terms.month_fees,
            rate=terms.distribution_rate,
            outside_quotas=fund.account.outside_quotas,
        )
        distribution = FundDistributionDTO(
            data_com=today,
            realized_profit=settlement.realized_profit,
            rate=terms.distribution_rate,
            quotas=fund.account.outside_quotas,
            per_quota=settlement.per_quota,
            paid_per_quota=None,
            paid=None,
            paid_on=None,
        )
        repository.fund.save_distribution(terms.id, distribution)
        fund.distributions = [*fund.distributions, distribution]
        fund.terms = terms.model_copy(
            update={
                "month_dividends": Decimal(0),
                "month_interest": Decimal(0),
                "month_sales_gain": Decimal(0),
                "month_fees": Decimal(0),
            }
        )

    def _holders(self, fund: Fund) -> list[tuple[UUID, Decimal]]:
        """Quem tem cota fora do formador: jogadores, bots e outras gestoras, com a posição de cada um."""
        clients = [user.client_id for user in self.participants()]
        clients += [c for c in self.client_ids if c != fund.account.client_id]
        positions = self._engine.broker
        holders: list[tuple[UUID, Decimal]] = []
        for client_id in clients:
            position = positions.get_positions(client_id).get(fund.ticker)
            if position is not None and position.size > 0:
                holders.append((client_id, position.size))
        return holders

    def _pay_distribution(self, fund: Fund, today: date) -> None:
        """Paga o rendimento apurado na última data-com, no primeiro pregão depois dela.

        O valor por cota sai de `payout_per_quota`: o apurado, ou o caixa dividido pelas cotas
        quando o caixa não cobre. Cada cotista recebe como provento da cota.
        """
        pending = fund.distributions[-1] if fund.distributions else None
        if pending is None or pending.paid_on is not None or not fund.listed:
            return
        holders = self._holders(fund)
        outside = sum((quotas for _, quotas in holders), Decimal(0))
        cash = self._engine.get_cash(fund.account.client_id)
        paid_per_quota = payout_per_quota(pending.per_quota, outside, cash)
        payments = [
            (client_id, holder_payment(quotas, paid_per_quota))
            for client_id, quotas in holders
        ]
        total = sum((amount for _, amount in payments), Decimal(0))
        if total > 0:
            self._engine.charge_fund_distribution(fund.account.client_id, total)
            for client_id, amount in payments:
                if amount > 0:
                    self._engine.pay_dividend(client_id, fund.ticker, amount)
        paid = pending.model_copy(
            update={"paid_per_quota": paid_per_quota, "paid": total, "paid_on": today}
        )
        repository.fund.save_distribution(fund.terms.id, paid)
        fund.distributions = [*fund.distributions[:-1], paid]

    def short_cash_plans(
        self, user: UserDTO
    ) -> list[tuple[Fund, FundDistributionPlanDTO]]:
        """As gestoras do jogador cujo caixa não cobre o rendimento projetado do mês."""
        plans = [
            (fund, self.distribution_plan(fund)) for fund in self.managed_by(user.id)
        ]
        return [(f, p) for f, p in plans if p.projected > 0 and not p.cash_enough]

    def distribution_plan(self, fund: Fund) -> FundDistributionPlanDTO:
        """O rendimento do mês corrente: o realizado até hoje, o que ele distribuiria e se o caixa cobre."""
        terms = fund.terms
        today = self._engine.current_date
        outside = fund.account.outside_quotas
        settlement = settle_month(
            dividends=terms.month_dividends,
            interest=terms.month_interest,
            sales_gain=terms.month_sales_gain,
            fees=terms.month_fees,
            rate=terms.distribution_rate,
            outside_quotas=outside,
        )
        projected = settlement.per_quota * outside
        cash = self._engine.get_cash(fund.account.client_id)
        data_com_on = data_com_of_month(today)
        return FundDistributionPlanDTO(
            rate=terms.distribution_rate,
            pending_rate=terms.pending_distribution_rate,
            pending_from=terms.pending_from
            if terms.pending_distribution_rate is not None
            else None,
            dividends=terms.month_dividends,
            interest=terms.month_interest,
            sales_gain=terms.month_sales_gain,
            fees=-terms.month_fees,
            realized_profit=realized_profit(
                terms.month_dividends,
                terms.month_interest,
                terms.month_sales_gain,
                terms.month_fees,
            ),
            projected=projected,
            projected_per_quota=settlement.per_quota,
            cash=cash,
            cash_enough=cash - terms.fee_payable >= projected,
            data_com_on=data_com_on,
            pay_on=next_business_day(data_com_on),
        )

    # =========================
    # Apoio
    # =========================

    def _load(self, terms: FundDTO) -> Fund:
        """Põe a gestora no motor: conta, carteira, cota no catálogo e a janela do preço de ranking."""
        account = FundAccount(
            client_id=terms.client_id,
            quotas=terms.quotas,
            maker_quotas=terms.maker_quotas,
            maker_cash=terms.maker_cash,
            offer_remaining=terms.offer_remaining,
        )
        # Os dias depois do último processado são refeitos pelo tick
        after = self._engine.current_date + timedelta(days=1)
        repository.fund.drop_days_from(terms.id, after)
        repository.fund.drop_offer_sales_from(terms.id, after)
        repository.fund.drop_distributions_from(terms.id, after)
        days = repository.fund.days(
            terms.id, after, max(RANKING_WINDOW, PERFORMANCE_WINDOW)
        )
        # A retomada desfaz as ordens abertas: a recompra em aberto fica cancelada
        repository.fund.cancel_open_buybacks(terms.id)
        issuance = next(
            (i for i in repository.fund.issuances(terms.id) if i.closed_on is None),
            None,
        )
        assemblies, assembly_votes, assembly_history = self._assemblies.load(terms.id)
        fund = Fund(
            terms=terms,
            account=account,
            assemblies=assemblies,
            assembly_votes=assembly_votes,
            assembly_history=assembly_history,
            comanagers=self._comanagers.load(terms.id),
            directed=self._directed.load(terms.id),
            distributions=repository.fund.distributions(terms.id, after),
            days=[
                TradedDay(d.traded_quantity, d.traded_value)
                for d in days[-RANKING_WINDOW:]
            ],
            navs=cut_window([NavPoint(d.day, d.nav) for d in days]),
            last_close=repository.fund.last_close(
                self._simulation_id, terms.stock_id, self._engine.current_date
            ),
            last_trade_price=_decimal_or_none(
                repository.fund.last_traded_close(
                    self._simulation_id, terms.stock_id, self._engine.current_date
                )
            ),
            issuance=issuance,
            issuance_rights={
                right.user_id: right
                for right in (
                    repository.fund.issuance_rights(issuance.id) if issuance else []
                )
            },
        )
        self._funds[terms.ticker] = fund
        self._publish_fee_payable(fund)
        self._accounts[terms.ticker] = account
        self._engine.broker.maker_accounts[terms.ticker] = account
        SimulationManager.add_fund_portfolios({terms.client_id: terms.portfolio_id})
        SimulationManager.add_fund_names({terms.client_id: terms.name})
        self._engine.add_created_stock(
            StockDTO(
                id=terms.stock_id,
                ticker=terms.ticker,
                name=terms.name,
                asset_class=AssetClass.FUND,
            )
        )
        return fund

    def _announce(self, day: date, headline: Headline) -> None:
        if self._publish is not None:
            self._publish(day, headline)

    def nav_of(self, fund: Fund) -> Decimal | None:
        """O PL por cota de agora, com a reserva da recompra contada."""
        return self._nav(fund)

    def quotas_of(self, fund: Fund, user: UserDTO) -> Decimal:
        """As cotas da gestora que `user` tem na carteira pessoal."""
        position = self._engine.broker.get_positions(user.client_id).get(fund.ticker)
        return position.size if position else Decimal(0)

    def _nav(self, fund: Fund) -> Decimal | None:
        """O PL por cota pelo balanço da carteira da gestora."""
        balance = self._engine.balance_sheet(fund.account.client_id)
        return nav_per_quota(
            balance.total_cash + self._reserved_for_buyback(fund),
            balance.total_equity,
            balance.total_fixed,
            balance.total_debt,
            fund.account.quotas,
        )

    def _reserved_for_buyback(self, fund: Fund) -> Decimal:
        """O caixa que a ordem de recompra aberta guarda: ele ainda é patrimônio da gestora."""
        order = fund.buyback_order
        if (
            fund.buyback is None
            or order is None
            or order.status not in (OrderStatus.PENDING, OrderStatus.PARTIAL)
        ):
            return Decimal(0)
        return to_money(order.price) * order.remaining

    def listed_candles(self, today: date) -> list[CandleDTO]:
        """A última vela de cada cota listada, da memória do motor.

        A cota que ainda não fechou pregão desde a estreia ou desde a retomada ganha a vela
        plana do dia: ao último fechamento, ou ao PL na estreia.
        """
        candles = []
        for fund in self._funds.values():
            if not fund.listed or fund.nav is None:
                continue
            stock = self._engine.stocks[fund.ticker]
            last = self._engine.matching_engine.market_data.get_last(fund.ticker)
            if last is None:
                candles.append(self._flat_candle(fund, fund.nav, today))
                continue
            change = last.close - last.open
            candles.append(
                CandleDTO(
                    **stock.model_dump(),
                    open=last.open,
                    high=last.high,
                    low=last.low,
                    close=last.close,
                    volume=last.volume,
                    price_date=last.price_date,
                    change=round(change, 2),
                    change_pct=change / last.open if last.open else 0,
                )
            )
        return candles

    def _flat_candle(self, fund: Fund, nav: Decimal, today: date) -> CandleDTO:
        """A vela sem negócio do dia: o último fechamento, ou o PL na estreia."""
        stock = self._engine.stocks[fund.ticker]
        return close_candle(stock, today, DayTrades(), fund.last_close, nav)

    def _seed_candle(self, fund: Fund, nav: Decimal, today: date) -> None:
        """A vela plana da cota sem vela na memória do motor, para os bots do pregão a verem.

        A vela de verdade do pregão a substitui no fechamento.
        """
        if self._engine.matching_engine.market_data.get_last(fund.ticker) is None:
            self._engine.update_market_data([self._flat_candle(fund, nav, today)])

    def _reference(self, fund: Fund, nav: Decimal, today: date) -> FundReference:
        """A referência de negociação da cota no pregão de hoje.

        O preço fixo é o da ordem do emissor no livro: o PL na oferta de abertura e o preço
        anunciado na sobra da emissão. O último pregão da janela é o fim dela.
        """
        issuance = fund.issuance
        selling = bool(fund.account.offer_remaining)
        fixed_price: float | None = None
        last_session = False
        if selling:
            fixed_price = round(float(issuance.price if issuance else nav), 2)
            listed_on = fund.terms.listed_on
            if issuance is not None:
                last_session = today >= issuance.ends_on
            elif listed_on is not None:
                last_session = today >= offer_ends_on(listed_on)
        performance = excess_return(
            fund.navs, nav, today, fund.distributions, cdi_growth
        )
        return FundReference(
            nav=float(nav),
            performance=float(performance),
            fixed_price=fixed_price,
            fixed_price_last_session=last_session,
        )

    def _refresh_orders(self, fund: Fund, today: date) -> None:
        """A escada do formador e a ordem de venda do emissor: ao PL do dia na oferta de abertura,
        ao preço fixo do anúncio na sobra da emissão."""
        if fund.nav is None:
            return
        issuance = fund.issuance
        fair_value = float(issuance.price) if issuance else float(fund.nav)
        selling = fund.account.offer_remaining is not None
        self._maker.refresh(
            fund.ticker,
            float(fund.nav),
            fund.account.quotas,
            today,
            bid_ceiling=fair_value if selling else None,
        )
        self._offer.refresh(fund.ticker, fair_value, today)

    def _close_offer(self, fund: Fund, day: date) -> None:
        """Fecha a oferta e grava o dia em que fechou."""
        self._offer.close(fund.ticker)
        fund.terms = fund.terms.model_copy(update={"offer_closed_on": day})
        self._save(fund)

    def _record_offer_sale(
        self,
        ticker: str,
        buyer_user_id: int | None,
        quotas: Decimal,
        price: Decimal,
    ) -> None:
        """Grava a venda da oferta no dia dela, junto das cotas emitidas; a que zera o saldo
        fecha a oferta nesse mesmo dia."""
        fund = self._funds[ticker]
        today = self._engine.current_date
        issuance = fund.issuance
        repository.fund.record_offer_sale(
            fund.terms.id,
            FundOfferSaleDTO(
                day=today,
                buyer_user_id=buyer_user_id,
                quotas=quotas,
                price=price,
                issuance_id=issuance.id if issuance else None,
            ),
        )
        if issuance is not None:
            # A venda da sobra soma na emissão; quem a encerra é o fim do pregão
            self._add_issuance_sold(fund, quotas)
        elif fund.account.offer_remaining is None:
            fund.terms = fund.terms.model_copy(update={"offer_closed_on": today})
        self._save(fund)

    def _publish_fee_payable(self, fund: Fund) -> None:
        """A taxa a pagar é dívida da conta da gestora no motor, e o balanço da carteira a soma."""
        self._engine.fund_fee_payable[fund.account.client_id] = fund.terms.fee_payable

    def _save(self, fund: Fund) -> None:
        account = fund.account
        fund.terms = fund.terms.model_copy(
            update={
                "quotas": account.quotas,
                "maker_quotas": account.maker_quotas,
                "maker_cash": account.maker_cash,
                "offer_remaining": account.offer_remaining,
            }
        )
        self._publish_fee_payable(fund)
        repository.fund.save(fund.terms)
