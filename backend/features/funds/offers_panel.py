from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.fund import (
    FundClosedOfferDTO,
    FundOffersDTO,
    FundOpenOfferDTO,
    FundPreferenceOfferDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.utils import next_business_day
from backend.features.funds import fund_ledger
from backend.features.funds.fund_book import (
    LEFTOVER_SESSIONS,
    OFFER_SESSIONS,
    PREFERENCE_SESSIONS,
    Fund,
    FundBook,
    offer_ends_on,
    offer_session,
)
from backend.features.market_maker.sessions import window_session


class FundOffersBuilder:
    """A página Ofertas públicas: a preferência de quem consulta, a venda aberta a qualquer
    investidor e o histórico do que já encerrou.

    A oferta de abertura segue na lista de abertas até o último pregão dela, mesmo esgotada:
    o que o pregão não vendeu é o que encerra por prazo e vai ao histórico.
    """

    def __init__(self, book: FundBook, today: date) -> None:
        self._book = book
        self._today = today

    def build(self, viewer: UserDTO) -> FundOffersDTO:
        nicknames = {user.id: user.nickname for user in self._book.participants()}
        preference: list[FundPreferenceOfferDTO] = []
        opened: list[FundOpenOfferDTO] = []
        closed: list[FundClosedOfferDTO] = []
        # Cada gestora contribui com o que tem de aberto e com o histórico das vendas que encerrou
        for fund in self._book.funds():
            preference.extend(self._preference(fund, viewer))
            opened.extend(self._open(fund, nicknames))
            closed.extend(
                self._closed(
                    fund, hide_initial=self._open_initial_terms(fund) is not None
                )
            )
        preference.sort(key=lambda item: (item.preference_ends_on, item.ticker))
        opened.sort(key=lambda item: (item.ends_on, item.name))
        closed.sort(key=lambda item: (item.closed_on, item.ticker), reverse=True)
        return FundOffersDTO(preference=preference, open=opened, closed=closed)

    def _preference(self, fund: Fund, viewer: UserDTO) -> list[FundPreferenceOfferDTO]:
        """A preferência de `viewer` na emissão em andamento, enquanto ainda tem direito a usar."""
        issuance = fund.issuance
        if issuance is None or fund.issuance_phase(self._today) != "preference":
            return []
        right = fund.issuance_rights.get(viewer.id)
        if right is None or right.rights - right.bought <= 0:
            return []
        session = window_session(
            issuance.announced_on, self._today, PREFERENCE_SESSIONS
        )
        return [
            FundPreferenceOfferDTO(
                fund_id=fund.terms.id,
                ticker=fund.ticker,
                name=fund.terms.name,
                issuance_quotas=issuance.quotas,
                price=issuance.price,
                my_rights=right.rights,
                my_left=right.rights - right.bought,
                holders_bought=issuance.sold,
                preference_ends_on=issuance.preference_ends_on,
                sessions_left=PREFERENCE_SESSIONS - session + 1,
                leftover_sessions=LEFTOVER_SESSIONS,
            )
        ]

    def _initial_sold(self, fund: Fund) -> Decimal:
        """As cotas vendidas na oferta de abertura, somadas das vendas gravadas."""
        sales = repository.fund.offer_sales(fund.terms.id)
        return fund_ledger.offer_totals(sales).sold

    def _open_initial_terms(self, fund: Fund) -> tuple[date, Decimal, Decimal] | None:
        """O dia de abertura, as cotas e o preço da oferta de abertura que aparece entre as
        abertas: em venda, ou esgotada dentro do prazo dela; nulo fora disso."""
        terms = fund.terms
        listed_on, quotas, price = (
            terms.listed_on,
            terms.offer_quotas,
            terms.offer_price,
        )
        if (
            fund.issuance is not None
            or listed_on is None
            or quotas is None
            or price is None
            or self._today > offer_ends_on(listed_on)
        ):
            return None
        selling = fund.account.offer_remaining is not None
        sold_out = (
            not selling
            and terms.offer_closed_on is not None
            and self._initial_sold(fund) >= quotas
        )
        return (listed_on, quotas, price) if selling or sold_out else None

    def _open(self, fund: Fund, nicknames: dict[int, str]) -> list[FundOpenOfferDTO]:
        """A venda aberta a todos: a oferta de abertura ou a sobra da emissão."""
        terms = fund.terms
        manager = nicknames.get(terms.manager_user_id)
        issuance = fund.issuance
        if issuance is not None:
            if fund.issuance_phase(self._today) != "leftover":
                return []
            start = next_business_day(issuance.preference_ends_on)
            session = window_session(start, self._today, LEFTOVER_SESSIONS)
            sales = repository.fund.issuance_sales(issuance.id)
            bought = sum(
                (
                    sale.quotas
                    for sale in sales
                    if sale.day <= issuance.preference_ends_on
                ),
                Decimal(0),
            )
            return [
                FundOpenOfferDTO(
                    fund_id=terms.id,
                    ticker=fund.ticker,
                    name=terms.name,
                    manager_nickname=manager,
                    kind="leftover",
                    price=issuance.price,
                    quotas=issuance.quotas,
                    remaining=issuance.quotas - issuance.sold,
                    session=None,
                    ends_on=issuance.ends_on,
                    sessions_left=LEFTOVER_SESSIONS - session,
                    management_fee=terms.management_fee,
                    performance_fee=terms.performance_fee,
                    preference_ends_on=issuance.preference_ends_on,
                    preference_bought=bought,
                )
            ]
        initial = self._open_initial_terms(fund)
        if initial is None:
            return []
        listed_on, quotas, price = initial
        session = offer_session(listed_on, self._today)
        remaining = fund.account.offer_remaining or Decimal(0)
        return [
            FundOpenOfferDTO(
                fund_id=terms.id,
                ticker=fund.ticker,
                name=terms.name,
                manager_nickname=manager,
                kind="initial",
                price=price,
                quotas=quotas,
                remaining=remaining,
                session=session,
                ends_on=offer_ends_on(listed_on),
                sessions_left=OFFER_SESSIONS - session,
                management_fee=terms.management_fee,
                performance_fee=terms.performance_fee,
                preference_ends_on=None,
                preference_bought=None,
            )
        ]

    def _closed(self, fund: Fund, hide_initial: bool) -> list[FundClosedOfferDTO]:
        """O histórico da gestora: a oferta de abertura e cada emissão encerradas."""
        terms = fund.terms
        market_price = self._book.price(fund)
        found: list[FundClosedOfferDTO] = []
        if (
            not hide_initial
            and terms.offer_closed_on is not None
            and terms.offer_quotas is not None
            and terms.offer_price is not None
        ):
            found.append(
                FundClosedOfferDTO(
                    fund_id=terms.id,
                    ticker=fund.ticker,
                    name=terms.name,
                    kind="initial",
                    price=terms.offer_price,
                    quotas=terms.offer_quotas,
                    sold=self._initial_sold(fund),
                    closed_on=terms.offer_closed_on,
                    market_price=market_price,
                )
            )
        for issuance in repository.fund.issuances(terms.id):
            if issuance.closed_on is None:
                continue
            found.append(
                FundClosedOfferDTO(
                    fund_id=terms.id,
                    ticker=fund.ticker,
                    name=terms.name,
                    kind="issuance",
                    price=issuance.price,
                    quotas=issuance.quotas,
                    sold=issuance.sold,
                    closed_on=issuance.closed_on,
                    market_price=market_price,
                )
            )
        return found
