import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.candle import CandleDTO
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import (
    DEFAULT_DISTRIBUTION_RATE,
    FundAssemblyDTO,
    FundAssemblyVoteDTO,
    FundBuybackDTO,
    FundBuybackState,
    FundDayDTO,
    FundDistributionDTO,
    FundDTO,
    FundIssuanceDTO,
    FundIssuanceRightDTO,
    FundOfferSaleDTO,
)
from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.stock import StockDTO
from backend.core.enum import (
    AssetClass,
    DataOrigin,
    EquityEventType,
    FundAssemblyStatus,
)
from backend.core.models.models import (
    EventEquity,
    FundAssemblies,
    FundAssemblyVotes,
    FundBuybacks,
    FundDays,
    FundDistributions,
    FundIssuanceRights,
    FundIssuances,
    FundOfferSales,
    Funds,
    Portfolios,
    Stock,
    StockPriceHistory,
    Users,
)
from backend.core.repository.ticker_claim import claim_stock, letters_taken

# Colunas da linha de `funds` que mudam depois de a gestora nascer
_MUTABLE = (
    "manager_user_id",
    "quotas",
    "maker_quotas",
    "maker_cash",
    "offer_remaining",
    "listed_on",
    "offer_quotas",
    "offer_price",
    "offer_closed_on",
    "takeover_offer_on",
    "management_fee",
    "performance_fee",
    "pending_management_fee",
    "pending_performance_fee",
    "pending_from",
    "high_water_mark",
    "high_water_mark_on",
    "last_performance_on",
    "distribution_rate",
    "pending_distribution_rate",
    "month_dividends",
    "month_interest",
    "month_sales_gain",
    "month_fees",
    "management_fee_payable",
    "performance_fee_payable",
)


def _to_dto(fund: Funds, ticker: str) -> FundDTO:
    return FundDTO(ticker=ticker, **{k: getattr(fund, k) for k in _columns()})


def _assembly_dto(row: FundAssemblies) -> FundAssemblyDTO:
    return FundAssemblyDTO(
        id=row.id,
        convener_user_id=row.convener_user_id,
        candidate_user_id=row.candidate_user_id,
        previous_manager_user_id=row.previous_manager_user_id,
        status=FundAssemblyStatus(row.status),
        called_on=row.called_on,
        started_on=row.started_on,
        ends_on=row.ends_on,
        closed_on=row.closed_on,
        in_favor_quotas=row.in_favor_quotas,
        against_quotas=row.against_quotas,
        abstention_quotas=row.abstention_quotas,
    )


def _columns() -> list[str]:
    return [
        "id",
        "stock_id",
        "portfolio_id",
        "client_id",
        "founder_user_id",
        "name",
        *_MUTABLE,
    ]


def _equity_event(event: EventEquity, ticker: str) -> EquityEventDTO:
    return EquityEventDTO(
        simulation_id=event.simulation_id,
        portfolio_id=event.portfolio_id,
        event_type=EquityEventType(event.event_type),
        ticker=ticker,
        quantity=event.quantity,
        price=event.price,
        event_date=event.event_date,
        created_at=event.created_at,
    )


class FundRepository:
    @transactional
    def claim_stock(self, session: Session, ticker: str, name: str) -> StockDTO | None:
        """A linha de `stock` da cota de uma gestora; None quando as letras são de um ativo importado."""
        return claim_stock(session, ticker, name, AssetClass.FUND)

    @transactional
    def letters_taken_by_asset(self, session: Session, ticker: str) -> bool:
        """A conferência de `claim_stock` sem gravar: as quatro letras já são de um ativo importado."""
        return letters_taken(session, ticker, AssetClass.FUND)

    @transactional
    def create(
        self,
        session: Session,
        *,
        simulation_id: int,
        stock_id: int,
        ticker: str,
        client_id: uuid.UUID,
        founder_user_id: int,
        manager_user_id: int,
        name: str,
        management_fee: Decimal,
        performance_fee: Decimal,
    ) -> FundDTO:
        """Abre a carteira da gestora (sem jogador dono) e grava a gestora com zero cota."""
        now = datetime.now(UTC)
        portfolio = Portfolios(
            simulation_id=simulation_id,
            user_id=None,
            created_at=now,
            starting_cash=Decimal(0),
        )
        session.add(portfolio)
        session.flush()
        fund = Funds(
            simulation_id=simulation_id,
            stock_id=stock_id,
            portfolio_id=portfolio.id,
            client_id=client_id,
            founder_user_id=founder_user_id,
            manager_user_id=manager_user_id,
            name=name,
            management_fee=management_fee,
            performance_fee=performance_fee,
            distribution_rate=DEFAULT_DISTRIBUTION_RATE,
            month_dividends=Decimal(0),
            month_interest=Decimal(0),
            month_sales_gain=Decimal(0),
            month_fees=Decimal(0),
            management_fee_payable=Decimal(0),
            performance_fee_payable=Decimal(0),
            created_at=now,
        )
        session.add(fund)
        session.flush()
        return _to_dto(fund, ticker)

    @transactional
    def of_simulation(self, session: Session, simulation_id: int) -> list[FundDTO]:
        """As gestoras da partida, em ordem de criação."""
        rows = session.execute(
            select(Funds, Stock.ticker)
            .join(Stock, Stock.id == Funds.stock_id)
            .where(Funds.simulation_id == simulation_id)
            .order_by(Funds.id)
        ).all()
        return [_to_dto(fund, ticker) for fund, ticker in rows]

    @transactional
    def save(self, session: Session, fund: FundDTO) -> None:
        """Grava as colunas que mudam: cotas, formador, oferta, taxas, rendimento e marca d'água."""
        session.execute(
            update(Funds)
            .where(Funds.id == fund.id)
            .values({column: getattr(fund, column) for column in _MUTABLE})
        )

    @transactional
    def save_day(self, session: Session, fund_id: int, day: FundDayDTO) -> None:
        """Grava o fechamento do pregão; refazer o dia troca a linha."""
        values = {"fund_id": fund_id, **day.model_dump()}
        session.execute(
            insert(FundDays)
            .values(values)
            .on_conflict_do_update(
                index_elements=["fund_id", "day"],
                set_={k: v for k, v in values.items() if k not in ("fund_id", "day")},
            )
        )

    @transactional
    def days(
        self, session: Session, fund_id: int, before: date, limit: int
    ) -> list[FundDayDTO]:
        """Os últimos `limit` fechamentos antes de `before`, do mais antigo ao mais recente."""
        rows = session.execute(
            select(FundDays)
            .where(FundDays.fund_id == fund_id, FundDays.day < before)
            .order_by(FundDays.day.desc())
            .limit(limit)
        ).scalars()
        return [FundDayDTO.model_validate(row) for row in reversed(list(rows))]

    @transactional
    def credit_history(
        self,
        session: Session,
        portfolio_id: int,
        before: date | None = None,
        last: int | None = None,
    ) -> list[PatrimonialHistoryDTO]:
        """O histórico patrimonial da gestora, lido dos fechamentos dela, em ordem de data.

        O patrimônio é o PL por cota vezes as cotas; o aporte acumulado soma a variação de cotas
        vezes o PL por cota do dia; a dívida é o empréstimo mais a taxa a pagar. Com `last`, só os
        `last` mais recentes antes de `before`.
        """
        stmt = (
            select(FundDays)
            .join(Funds, Funds.id == FundDays.fund_id)
            .where(Funds.portfolio_id == portfolio_id)
        )
        if before is not None:
            stmt = stmt.where(FundDays.day < before)
        if last is None:
            rows = list(session.scalars(stmt.order_by(FundDays.day)).all())
        else:
            recent = stmt.order_by(FundDays.day.desc()).limit(last)
            rows = list(reversed(session.scalars(recent).all()))

        history: list[PatrimonialHistoryDTO] = []
        contribution = Decimal(0)
        previous_quotas: Decimal | None = None
        for row in rows:
            networth = row.nav * row.quotas
            if previous_quotas is None:
                contribution = networth
            else:
                contribution += (row.quotas - previous_quotas) * row.nav
            previous_quotas = row.quotas
            history.append(
                PatrimonialHistoryDTO(
                    snapshot_date=row.day,
                    total_networth=networth,
                    total_equity=Decimal(0),
                    total_fixed=Decimal(0),
                    total_cash=Decimal(0),
                    total_contribution=contribution,
                    total_debt=row.loan_debt + row.fee_payable,
                )
            )
        return history

    @transactional
    def drop_days_from(self, session: Session, fund_id: int, day: date) -> None:
        """Apaga os fechamentos de `day` em diante: o dia refeito pela retomada recomeça limpo."""
        session.execute(
            delete(FundDays).where(FundDays.fund_id == fund_id, FundDays.day >= day)
        )

    @transactional
    def save_distribution(
        self, session: Session, fund_id: int, distribution: FundDistributionDTO
    ) -> None:
        """Grava o rendimento do mês: a data-com cria a linha e o pagamento completa os campos pagos."""
        values = {"fund_id": fund_id, **distribution.model_dump()}
        session.execute(
            insert(FundDistributions)
            .values(values)
            .on_conflict_do_update(
                index_elements=["fund_id", "data_com"],
                set_={
                    k: v for k, v in values.items() if k not in ("fund_id", "data_com")
                },
            )
        )

    @transactional
    def distributions(
        self, session: Session, fund_id: int, before: date
    ) -> list[FundDistributionDTO]:
        """Os rendimentos apurados antes de `before`, do mais antigo ao mais novo."""
        rows = session.execute(
            select(FundDistributions)
            .where(
                FundDistributions.fund_id == fund_id,
                FundDistributions.data_com < before,
            )
            .order_by(FundDistributions.data_com)
        ).scalars()
        return [FundDistributionDTO.model_validate(row) for row in rows]

    @transactional
    def drop_distributions_from(
        self, session: Session, fund_id: int, day: date
    ) -> None:
        """Apaga as datas-com de `day` em diante e desfaz os pagamentos dali: o dia refeito pela retomada recomeça limpo."""
        session.execute(
            delete(FundDistributions).where(
                FundDistributions.fund_id == fund_id,
                FundDistributions.data_com >= day,
            )
        )
        session.execute(
            update(FundDistributions)
            .where(
                FundDistributions.fund_id == fund_id,
                FundDistributions.paid_on >= day,
            )
            .values(paid_per_quota=None, paid=None, paid_on=None)
        )

    @transactional
    def record_offer_sale(
        self, session: Session, fund_id: int, sale: FundOfferSaleDTO
    ) -> None:
        """Grava uma venda da oferta pública no momento em que acontece."""
        session.add(FundOfferSales(fund_id=fund_id, **sale.model_dump()))

    @transactional
    def offer_sales(self, session: Session, fund_id: int) -> list[FundOfferSaleDTO]:
        """As vendas da oferta pública de abertura, na ordem em que aconteceram."""
        rows = session.execute(
            select(FundOfferSales)
            .where(
                FundOfferSales.fund_id == fund_id,
                FundOfferSales.issuance_id.is_(None),
            )
            .order_by(FundOfferSales.id)
        ).scalars()
        return [FundOfferSaleDTO.model_validate(row) for row in rows]

    @transactional
    def issuance_sales(
        self, session: Session, issuance_id: int
    ) -> list[FundOfferSaleDTO]:
        """As vendas de uma emissão (preferência e sobra), na ordem em que aconteceram."""
        rows = session.execute(
            select(FundOfferSales)
            .where(FundOfferSales.issuance_id == issuance_id)
            .order_by(FundOfferSales.id)
        ).scalars()
        return [FundOfferSaleDTO.model_validate(row) for row in rows]

    @transactional
    def create_issuance(
        self,
        session: Session,
        fund_id: int,
        issuance: FundIssuanceDTO,
        rights: list[FundIssuanceRightDTO],
    ) -> FundIssuanceDTO:
        """Grava o anúncio de uma emissão com o retrato dos direitos; devolve com o id."""
        values = issuance.model_dump(exclude={"id"})
        row = FundIssuances(fund_id=fund_id, **values)
        session.add(row)
        session.flush()
        session.add_all(
            FundIssuanceRights(issuance_id=row.id, **right.model_dump())
            for right in rights
        )
        return FundIssuanceDTO.model_validate(row)

    @transactional
    def save_issuance(
        self,
        session: Session,
        issuance: FundIssuanceDTO,
        rights: list[FundIssuanceRightDTO],
    ) -> None:
        """Grava o que muda na emissão: as cotas vendidas, o fechamento e o que cada jogador já comprou."""
        session.execute(
            update(FundIssuances)
            .where(FundIssuances.id == issuance.id)
            .values(sold=issuance.sold, closed_on=issuance.closed_on)
        )
        for right in rights:
            session.execute(
                update(FundIssuanceRights)
                .where(
                    FundIssuanceRights.issuance_id == issuance.id,
                    FundIssuanceRights.user_id == right.user_id,
                )
                .values(bought=right.bought)
            )

    @transactional
    def issuances(self, session: Session, fund_id: int) -> list[FundIssuanceDTO]:
        """As emissões da gestora, da mais antiga à mais nova."""
        rows = session.execute(
            select(FundIssuances)
            .where(FundIssuances.fund_id == fund_id)
            .order_by(FundIssuances.id)
        ).scalars()
        return [FundIssuanceDTO.model_validate(row) for row in rows]

    @transactional
    def issuance_rights(
        self, session: Session, issuance_id: int
    ) -> list[FundIssuanceRightDTO]:
        """Os direitos de preferência de uma emissão, um por jogador."""
        rows = session.execute(
            select(FundIssuanceRights)
            .where(FundIssuanceRights.issuance_id == issuance_id)
            .order_by(FundIssuanceRights.user_id)
        ).scalars()
        return [FundIssuanceRightDTO.model_validate(row) for row in rows]

    @transactional
    def create_buyback(
        self, session: Session, fund_id: int, buyback: FundBuybackDTO
    ) -> FundBuybackDTO:
        """Grava a recompra aberta; devolve com o id."""
        row = FundBuybacks(fund_id=fund_id, **buyback.model_dump(exclude={"id"}))
        session.add(row)
        session.flush()
        return FundBuybackDTO.model_validate(row)

    @transactional
    def save_buyback(self, session: Session, buyback: FundBuybackDTO) -> None:
        """Grava o andamento da recompra: cotas compradas, valor pago e estado."""
        session.execute(
            update(FundBuybacks)
            .where(FundBuybacks.id == buyback.id)
            .values(
                bought=buyback.bought,
                paid=buyback.paid,
                state=buyback.state,
            )
        )

    @transactional
    def buybacks(self, session: Session, fund_id: int) -> list[FundBuybackDTO]:
        """As recompras da gestora, da mais antiga à mais nova."""
        rows = session.execute(
            select(FundBuybacks)
            .where(FundBuybacks.fund_id == fund_id)
            .order_by(FundBuybacks.id)
        ).scalars()
        return [FundBuybackDTO.model_validate(row) for row in rows]

    @transactional
    def cancel_open_buybacks(self, session: Session, fund_id: int) -> None:
        """A retomada da partida desfaz as ordens abertas: a recompra em aberto fica cancelada."""
        canceled: FundBuybackState = "canceled"
        session.execute(
            update(FundBuybacks)
            .where(FundBuybacks.fund_id == fund_id, FundBuybacks.state == "open")
            .values(state=canceled)
        )

    @transactional
    def create_assembly(
        self, session: Session, fund_id: int, assembly: FundAssemblyDTO
    ) -> FundAssemblyDTO:
        """Grava a assembleia recém-convocada; devolve com o id."""
        values = assembly.model_dump(exclude={"id"})
        values["status"] = assembly.status.value
        row = FundAssemblies(fund_id=fund_id, **values)
        session.add(row)
        session.flush()
        return _assembly_dto(row)

    @transactional
    def save_assembly(self, session: Session, assembly: FundAssemblyDTO) -> None:
        """Grava o que muda na assembleia: estado, datas e o placar do fechamento."""
        session.execute(
            update(FundAssemblies)
            .where(FundAssemblies.id == assembly.id)
            .values(
                status=assembly.status.value,
                started_on=assembly.started_on,
                ends_on=assembly.ends_on,
                closed_on=assembly.closed_on,
                in_favor_quotas=assembly.in_favor_quotas,
                against_quotas=assembly.against_quotas,
                abstention_quotas=assembly.abstention_quotas,
            )
        )

    @transactional
    def assemblies(self, session: Session, fund_id: int) -> list[FundAssemblyDTO]:
        """As assembleias da gestora, da mais antiga à mais nova."""
        rows = session.execute(
            select(FundAssemblies)
            .where(FundAssemblies.fund_id == fund_id)
            .order_by(FundAssemblies.id)
        ).scalars()
        return [_assembly_dto(row) for row in rows]

    @transactional
    def save_assembly_vote(
        self, session: Session, assembly_id: int, vote: FundAssemblyVoteDTO
    ) -> None:
        """Grava o voto do cotista; votar de novo troca o voto."""
        values = {"assembly_id": assembly_id, **vote.model_dump()}
        session.execute(
            insert(FundAssemblyVotes)
            .values(values)
            .on_conflict_do_update(
                index_elements=["assembly_id", "user_id"],
                set_={"in_favor": vote.in_favor, "voted_on": vote.voted_on},
            )
        )

    @transactional
    def assembly_votes(
        self, session: Session, assembly_id: int
    ) -> list[FundAssemblyVoteDTO]:
        """Os votos de uma assembleia, um por cotista."""
        rows = session.execute(
            select(FundAssemblyVotes)
            .where(FundAssemblyVotes.assembly_id == assembly_id)
            .order_by(FundAssemblyVotes.user_id)
        ).scalars()
        return [FundAssemblyVoteDTO.model_validate(row) for row in rows]

    @transactional
    def last_removal(
        self, session: Session, simulation_id: int, user_id: int
    ) -> date | None:
        """O dia em que `user_id` foi afastado da gestão de uma gestora da partida, o mais recente."""
        return session.execute(
            select(FundAssemblies.closed_on)
            .join(Funds, Funds.id == FundAssemblies.fund_id)
            .where(
                Funds.simulation_id == simulation_id,
                FundAssemblies.previous_manager_user_id == user_id,
                FundAssemblies.status == FundAssemblyStatus.REPLACED.value,
            )
            .order_by(FundAssemblies.closed_on.desc())
            .limit(1)
        ).scalar_one_or_none()

    @transactional
    def founder_removals(
        self, session: Session, simulation_ids: list[int]
    ) -> list[tuple[int, int, str, date]]:
        """Os fundadores afastados da própria gestora por assembleia: simulação, id, apelido e
        o dia do primeiro afastamento."""
        rows = session.execute(
            select(
                Funds.simulation_id,
                Users.id,
                Users.nickname,
                func.min(FundAssemblies.closed_on),
            )
            .select_from(FundAssemblies)
            .join(Funds, Funds.id == FundAssemblies.fund_id)
            .join(Users, Users.id == Funds.founder_user_id)
            .where(
                Funds.simulation_id.in_(simulation_ids),
                FundAssemblies.previous_manager_user_id == Funds.founder_user_id,
                FundAssemblies.status == FundAssemblyStatus.REPLACED.value,
            )
            .group_by(Funds.simulation_id, Users.id, Users.nickname)
        ).all()
        return [
            (sim, user, name, day) for sim, user, name, day in rows if day is not None
        ]

    @transactional
    def drop_offer_sales_from(self, session: Session, fund_id: int, day: date) -> None:
        """Apaga as vendas de `day` em diante: o dia refeito pela retomada recomeça limpo."""
        session.execute(
            delete(FundOfferSales).where(
                FundOfferSales.fund_id == fund_id, FundOfferSales.day >= day
            )
        )

    @transactional
    def save_candle(
        self, session: Session, simulation_id: int, candle: CandleDTO
    ) -> None:
        """A vela da cota na série da própria partida: só ela enxerga esse preço."""
        values = {
            "stock_id": candle.id,
            "price_date": candle.price_date,
            "version": simulation_id,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
            "origin": DataOrigin.GENERATED.value,
        }
        session.execute(
            insert(StockPriceHistory)
            .values(values)
            .on_conflict_do_update(
                index_elements=["stock_id", "price_date", "version"],
                set_={
                    k: v
                    for k, v in values.items()
                    if k not in ("stock_id", "price_date", "version")
                },
            )
        )

    @transactional
    def last_close(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        """O último fechamento da cota na série da partida até `until`, ou None sem vela."""
        return session.execute(
            select(StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock_id,
                StockPriceHistory.version == simulation_id,
                StockPriceHistory.price_date <= until,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
        ).scalar_one_or_none()

    @transactional
    def month_end_closes(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> dict[date, float]:
        """O último fechamento de cada mês da série da partida até `until`, pelo primeiro dia do mês."""
        rows = session.execute(
            select(StockPriceHistory.price_date, StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock_id,
                StockPriceHistory.version == simulation_id,
                StockPriceHistory.price_date <= until,
            )
            .order_by(StockPriceHistory.price_date)
        ).all()
        return {day.replace(day=1): close for day, close in rows}

    @transactional
    def last_traded_close(
        self, session: Session, simulation_id: int, stock_id: int, until: date
    ) -> float | None:
        """O fechamento do último pregão em que a cota negociou até `until`, ou None se nunca negociou."""
        return session.execute(
            select(StockPriceHistory.close)
            .where(
                StockPriceHistory.stock_id == stock_id,
                StockPriceHistory.version == simulation_id,
                StockPriceHistory.price_date <= until,
                StockPriceHistory.volume > 0,
            )
            .order_by(StockPriceHistory.price_date.desc())
            .limit(1)
        ).scalar_one_or_none()

    @transactional
    def quota_trades(
        self, session: Session, simulation_id: int, stock_id: int
    ) -> list[EquityEventDTO]:
        """As compras e vendas da cota em todas as carteiras da partida, na ordem em que aconteceram."""
        rows = session.execute(
            select(EventEquity, Stock.ticker)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.stock_id == stock_id,
                EventEquity.event_type.in_(
                    [EquityEventType.BUY.value, EquityEventType.SELL.value]
                ),
            )
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()
        return [_equity_event(event, ticker) for event, ticker in rows]

    @transactional
    def portfolio_equity_events(
        self, session: Session, simulation_id: int, portfolio_id: int
    ) -> list[EquityEventDTO]:
        """Os eventos de renda variável da carteira na partida, na ordem em que aconteceram."""
        rows = session.execute(
            select(EventEquity, Stock.ticker)
            .join(Stock, Stock.id == EventEquity.stock_id)
            .where(
                EventEquity.simulation_id == simulation_id,
                EventEquity.portfolio_id == portfolio_id,
            )
            .order_by(EventEquity.event_date, EventEquity.id)
        ).all()
        return [_equity_event(event, ticker) for event, ticker in rows]
