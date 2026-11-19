from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, insert, literal, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.state_company import (
    StateCompanyDTO,
    StateCompanyMonthDTO,
    StateOwnedStockDTO,
    StateOwnedStockRequest,
)
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    EquityEventType,
    StateCompanyOrigin,
    StateCompanySize,
    StateCompanyStatus,
    StateLever,
)
from backend.core.models.models import (
    EventEquity,
    Portfolios,
    StateCompanies,
    StateCompanyMonths,
    StateOfferReservations,
    StateOwnedStocks,
    Stock,
    Users,
)
from backend.core.repository.ticker_claim import claim_stock, letters_taken


def _mark_dto(mark: StateOwnedStocks, ticker: str) -> StateOwnedStockDTO:
    return StateOwnedStockDTO(
        ticker=ticker,
        government_share=mark.government_share,
        shares=mark.shares,
        lever=StateLever(mark.lever) if mark.lever else None,
    )


def _company_dto(company: StateCompanies, ticker: str) -> StateCompanyDTO:
    return StateCompanyDTO(
        id=company.id,
        stock_id=company.stock_id,
        ticker=ticker,
        origin=StateCompanyOrigin(company.origin),
        government_share=company.government_share,
        shares=company.shares,
        lever=StateLever(company.lever) if company.lever else None,
        size=StateCompanySize(company.size) if company.size else None,
        invested=company.invested,
        mean_return=company.mean_return,
        seed=company.seed,
        status=StateCompanyStatus(company.status),
        founded_on=company.founded_on,
        offer_opened_on=company.offer_opened_on,
        privatized_on=company.privatized_on,
        proceeds=company.proceeds,
    )


class StateCompanyRepository:
    @transactional
    def mark(
        self, session: Session, ticker: str, request: StateOwnedStockRequest
    ) -> StateOwnedStockDTO | None:
        """Marca (ou remarca) o ativo da base como estatal; None quando o código não existe."""
        stock_id = session.execute(
            select(Stock.id).where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        if stock_id is None:
            return None
        values = {
            "government_share": request.government_share,
            "shares": request.shares,
            "lever": request.lever.value if request.lever else None,
        }
        session.execute(
            pg_insert(StateOwnedStocks)
            .values(stock_id=stock_id, **values)
            .on_conflict_do_update(index_elements=["stock_id"], set_=values)
        )
        return StateOwnedStockDTO(ticker=ticker, **request.model_dump())

    @transactional
    def unmark(self, session: Session, ticker: str) -> bool:
        """Tira a marcação; False quando o código não existe ou não estava marcado."""
        removed = session.execute(
            delete(StateOwnedStocks)
            .where(
                StateOwnedStocks.stock_id.in_(
                    select(Stock.id).where(Stock.ticker == ticker)
                )
            )
            .returning(StateOwnedStocks.stock_id)
        ).all()
        return len(removed) > 0

    @transactional
    def get_mark(self, session: Session, ticker: str) -> StateOwnedStockDTO | None:
        """A marcação do código, ou None quando ele não é estatal na base."""
        mark = session.execute(
            select(StateOwnedStocks)
            .join(Stock, Stock.id == StateOwnedStocks.stock_id)
            .where(Stock.ticker == ticker)
        ).scalar_one_or_none()
        return _mark_dto(mark, ticker) if mark else None

    @transactional
    def marks(self, session: Session) -> list[StateOwnedStockDTO]:
        """Todas as marcações da base, em ordem de ticker."""
        rows = session.execute(
            select(StateOwnedStocks, Stock.ticker)
            .join(Stock, Stock.id == StateOwnedStocks.stock_id)
            .order_by(Stock.ticker)
        ).all()
        return [_mark_dto(mark, ticker) for mark, ticker in rows]

    @transactional
    def copy_marks(self, session: Session, simulation_id: int) -> int:
        """Abre as estatais importadas da partida a partir das marcações da base; devolve quantas."""
        marks = select(
            literal(simulation_id),
            StateOwnedStocks.stock_id,
            literal(StateCompanyOrigin.IMPORTED.value),
            StateOwnedStocks.government_share,
            StateOwnedStocks.shares,
            StateOwnedStocks.lever,
        )
        opened = session.execute(
            insert(StateCompanies)
            .from_select(
                [
                    "simulation_id",
                    "stock_id",
                    "origin",
                    "government_share",
                    "shares",
                    "lever",
                ],
                marks,
            )
            .returning(StateCompanies.id)
        ).all()
        return len(opened)

    @transactional
    def of_simulation(
        self, session: Session, simulation_id: int
    ) -> list[StateCompanyDTO]:
        """As estatais da partida, em ordem de criação."""
        rows = session.execute(
            select(StateCompanies, Stock.ticker)
            .join(Stock, Stock.id == StateCompanies.stock_id)
            .where(StateCompanies.simulation_id == simulation_id)
            .order_by(StateCompanies.id)
        ).all()
        return [_company_dto(company, ticker) for company, ticker in rows]

    @transactional
    def claim_stock(self, session: Session, ticker: str, name: str) -> StockDTO | None:
        """A linha de `stock` da ação de uma estatal fundada; None quando as letras são de outro ativo."""
        return claim_stock(session, ticker, name, AssetClass.STOCK)

    @transactional
    def letters_taken(self, session: Session, ticker: str) -> bool:
        """A conferência de `claim_stock` sem gravar."""
        return letters_taken(session, ticker, AssetClass.STOCK)

    @transactional
    def insert_founded(
        self,
        session: Session,
        *,
        simulation_id: int,
        stock_id: int,
        ticker: str,
        government_share: Decimal,
        shares: int,
        lever: StateLever | None,
        size: StateCompanySize,
        invested: Decimal,
        mean_return: Decimal,
        seed: int,
        founded_on: date,
    ) -> StateCompanyDTO:
        """Abre a estatal fundada da partida, ativa."""
        company = StateCompanies(
            simulation_id=simulation_id,
            stock_id=stock_id,
            origin=StateCompanyOrigin.FOUNDED.value,
            government_share=government_share,
            shares=shares,
            lever=lever.value if lever else None,
            size=size.value,
            invested=invested,
            mean_return=mean_return,
            seed=seed,
            status=StateCompanyStatus.ACTIVE.value,
            founded_on=founded_on,
        )
        session.add(company)
        session.flush()
        return _company_dto(company, ticker)

    @transactional
    def open_offer(self, session: Session, company_id: int, day: date) -> None:
        """A estatal passa a oferta de privatização, aberta no dia."""
        session.execute(
            update(StateCompanies)
            .where(StateCompanies.id == company_id)
            .values(status=StateCompanyStatus.PRIVATIZING.value, offer_opened_on=day)
        )

    @transactional
    def mark_privatized(
        self,
        session: Session,
        company_id: int,
        day: date,
        proceeds: Decimal,
    ) -> None:
        """A oferta fechou: a estatal passa a privatizada no dia, com o que o governo recebeu."""
        session.execute(
            update(StateCompanies)
            .where(StateCompanies.id == company_id)
            .values(
                status=StateCompanyStatus.PRIVATIZED.value,
                privatized_on=day,
                proceeds=proceeds,
            )
        )

    @transactional
    def save_reservation(
        self,
        session: Session,
        company_id: int,
        portfolio_id: int,
        quantity: Decimal,
        day: date,
    ) -> None:
        """Grava (ou troca) o pedido da conta na oferta; a conta tem um pedido só por oferta."""
        values = {"quantity": quantity, "reserved_on": day}
        session.execute(
            pg_insert(StateOfferReservations)
            .values(state_company_id=company_id, portfolio_id=portfolio_id, **values)
            .on_conflict_do_update(
                index_elements=["state_company_id", "portfolio_id"], set_=values
            )
        )

    @transactional
    def reservations_of(self, session: Session, company_id: int) -> dict[int, Decimal]:
        """Os pedidos da oferta, por carteira, em ordem de carteira."""
        rows = session.execute(
            select(StateOfferReservations.portfolio_id, StateOfferReservations.quantity)
            .where(StateOfferReservations.state_company_id == company_id)
            .order_by(StateOfferReservations.portfolio_id)
        ).all()
        return {portfolio_id: quantity for portfolio_id, quantity in rows}

    @transactional
    def shares_held(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> Decimal:
        """As ações da empresa que as carteiras da partida têm até o dia: compras menos vendas."""
        rows = session.execute(
            select(EventEquity.event_type, func.sum(EventEquity.quantity))
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.stock_id == stock_id,
                EventEquity.event_date <= until,
            )
            .group_by(EventEquity.event_type)
        ).all()
        return sum(
            (EquityEventType(kind).quantity_sign * total for kind, total in rows),
            Decimal(0),
        )

    @transactional
    def shares_by_portfolio(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> list[tuple[int, bool | None, Decimal]]:
        """
        As ações da empresa em cada carteira da partida até o dia: (carteira, se o dono é um
        bot, saldo). O dono é None na carteira de gestora, que não tem usuário.
        """
        rows = session.execute(
            select(
                EventEquity.portfolio_id,
                Users.is_bot,
                EventEquity.event_type,
                func.sum(EventEquity.quantity),
            )
            .join(Portfolios, Portfolios.id == EventEquity.portfolio_id)
            .outerjoin(Users, Users.id == Portfolios.user_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.stock_id == stock_id,
                EventEquity.event_date <= until,
            )
            .group_by(EventEquity.portfolio_id, Users.is_bot, EventEquity.event_type)
            .order_by(EventEquity.portfolio_id)
        ).all()
        held: dict[int, tuple[bool | None, Decimal]] = {}
        for portfolio_id, is_bot, kind, total in rows:
            _, balance = held.get(portfolio_id, (is_bot, Decimal(0)))
            held[portfolio_id] = (
                is_bot,
                balance + EquityEventType(kind).quantity_sign * total,
            )
        return [(pid, is_bot, balance) for pid, (is_bot, balance) in held.items()]

    @transactional
    def save_month(self, session: Session, month: StateCompanyMonthDTO) -> None:
        """Grava (ou regrava) o mês da estatal."""
        values = {
            "fair_value": month.fair_value,
            "profit": month.profit,
            "treasury_dividend": month.treasury_dividend,
        }
        session.execute(
            pg_insert(StateCompanyMonths)
            .values(
                state_company_id=month.state_company_id, month=month.month, **values
            )
            .on_conflict_do_update(
                index_elements=["state_company_id", "month"], set_=values
            )
        )

    @transactional
    def months_of(
        self, session: Session, company_id: int
    ) -> list[StateCompanyMonthDTO]:
        """Os meses gravados da estatal, do mais antigo ao mais novo."""
        rows = session.execute(
            select(StateCompanyMonths)
            .where(StateCompanyMonths.state_company_id == company_id)
            .order_by(StateCompanyMonths.month)
        ).scalars()
        return [
            StateCompanyMonthDTO(
                state_company_id=row.state_company_id,
                month=row.month,
                fair_value=row.fair_value,
                profit=row.profit,
                treasury_dividend=row.treasury_dividend,
            )
            for row in rows
        ]
