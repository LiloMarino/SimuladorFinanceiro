import datetime
import decimal
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Double,
    Enum,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FixedIncomeAsset(Base):
    """O título que um jogador comprou, da vitrine da partida."""

    __tablename__ = "fixed_income_asset"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fixed_income_asset_simulation_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fixed_income_asset_pkey"),
        UniqueConstraint(
            "simulation_id", "asset_uuid", name="fixed_income_asset_simulation_uuid_key"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    asset_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    issuer: Mapped[str] = mapped_column(Text, nullable=False)
    investment_type: Mapped[str] = mapped_column(
        Enum(
            "CDB",
            "LCI",
            "LCA",
            "TESOURO_DIRETO",
            "DOLLAR_ACCOUNT",
            name="investment_type",
        ),
        nullable=False,
    )
    rate_type: Mapped[str] = mapped_column(
        Enum("SELIC", "IPCA", "CDI", "PREFIXADO", "FED_FUNDS", name="rate_type"),
        nullable=False,
    )
    maturity_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    interest_rate: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    daily_liquidity: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    player_cap: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 2))
    offered_until: Mapped[datetime.date | None] = mapped_column(Date)
    risk_premium: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))

    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="asset"
    )


class EconomicIndicatorHistory(Base):
    __tablename__ = "economic_indicator_history"
    __table_args__ = (
        PrimaryKeyConstraint(
            "series", "ref_date", "version", name="economic_indicator_history_pkey"
        ),
    )

    series: Mapped[str] = mapped_column(
        Enum(
            "CDI",
            "SELIC",
            "IPCA",
            "IBOV",
            "GDP_GROWTH",
            "UNEMPLOYMENT",
            "PTAX",
            "FOCUS_SELIC",
            "FOCUS_IPCA",
            "FOCUS_GDP",
            "FOCUS_FX",
            "FED_FUNDS",
            name="indicator_series",
        ),
        primary_key=True,
    )
    ref_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    value: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    origin: Mapped[str] = mapped_column(
        Enum("REAL", "GENERATED", name="data_origin"), nullable=False
    )
    # 0 é a série comum; N é a cópia congelada da partida simulations.id = N
    version: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, server_default=text("0")
    )


class FetchLog(Base):
    __tablename__ = "fetch_log"
    __table_args__ = (PrimaryKeyConstraint("series", name="fetch_log_pkey"),)

    series: Mapped[str] = mapped_column(
        Enum(
            "CDI",
            "SELIC",
            "IPCA",
            "IBOV",
            "GDP_GROWTH",
            "UNEMPLOYMENT",
            "PTAX",
            "FOCUS_SELIC",
            "FOCUS_IPCA",
            "FOCUS_GDP",
            "FOCUS_FX",
            "FED_FUNDS",
            name="indicator_series",
        ),
        primary_key=True,
    )
    attempted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    succeeded_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))


class GeneratedFuture(Base):
    """Os controles do futuro gravado: há no máximo um, e gerar de novo o troca."""

    __tablename__ = "generated_future"
    __table_args__ = (
        CheckConstraint("id = 1", name="generated_future_single_row"),
        PrimaryKeyConstraint("id", name="generated_future_pkey"),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    temperature: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    inflation_level: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    surge_frequency: Mapped[decimal.Decimal] = mapped_column(
        Numeric(4, 2), nullable=False
    )
    surge_intensity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    until: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    # Até onde o real ocupou o lugar do gerado depois da gravação; nulo enquanto
    # o futuro parte do último dia real de cada série
    real_advanced_until: Mapped[datetime.date | None] = mapped_column(Date)


class LastSimulationSettings(Base):
    """As regras da próxima partida, compartilhadas pelo servidor do host."""

    __tablename__ = "last_simulation_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="last_simulation_settings_single_row"),
        PrimaryKeyConstraint("id", name="last_simulation_settings_pkey"),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ImportSettings(Base):
    """As escolhas do host sobre como a base é importada; sem linha valem os padrões."""

    __tablename__ = "import_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="import_settings_single_row"),
        PrimaryKeyConstraint("id", name="import_settings_pkey"),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    correct_price_errors: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class Preset(Base):
    """Regras de partida com nome: os prontos do app e os que o host salvou."""

    __tablename__ = "preset"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="preset_pkey"),
        Index("preset_name_lower_key", text("lower(name)"), unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    built_in: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    # Regras sem o nome da partida; o que faltar vem do padrão ao carregar
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )


class Sectors(Base):
    __tablename__ = "sectors"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="sectors_pkey"),
        UniqueConstraint("name", name="sectors_name_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    segments: Mapped[list["Segments"]] = relationship(
        "Segments", back_populates="sector"
    )


class Segments(Base):
    __tablename__ = "segments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sector_id"],
            ["sectors.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="segments_sector_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="segments_pkey"),
        UniqueConstraint("sector_id", "name", name="segments_sector_id_name_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    sector_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    sector: Mapped["Sectors"] = relationship("Sectors", back_populates="segments")
    stock: Mapped[list["Stock"]] = relationship("Stock", back_populates="segment")


class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = (
        ForeignKeyConstraint(
            ["segment_id"],
            ["segments.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="stock_segment_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="stock_pkey"),
        UniqueConstraint("ticker", name="stock_ticker_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    ticker: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    asset_class: Mapped[str] = mapped_column(
        Enum("STOCK", "FII", "ETF", "BDR", "CRYPTO", name="asset_class"), nullable=False
    )
    # Moeda em que a fonte cota o ativo; o preço guardado é sempre em real
    currency: Mapped[str] = mapped_column(
        Enum("BRL", "USD", name="currency"),
        nullable=False,
        server_default=text("'BRL'"),
    )
    # Nacional ou internacional: nasce pela moeda e pela classe, e a Central de dados troca
    origin: Mapped[str] = mapped_column(
        Enum("DOMESTIC", "FOREIGN", name="asset_origin"),
        nullable=False,
        server_default=text("'DOMESTIC'"),
    )
    segment_id: Mapped[int | None] = mapped_column(Integer)

    segment: Mapped["Segments | None"] = relationship(
        "Segments", back_populates="stock"
    )
    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="stock"
    )
    stock_price_history: Mapped[list["StockPriceHistory"]] = relationship(
        "StockPriceHistory", back_populates="stock"
    )
    stock_corporate_event: Mapped[list["StockCorporateEvent"]] = relationship(
        "StockCorporateEvent", back_populates="stock"
    )


class Simulations(Base):
    __tablename__ = "simulations"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="simulations_pkey"),
        UniqueConstraint("name", name="simulations_name_key"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # Os imprevistos saem dela: fica no servidor, fora das regras
    random_seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Partida só de estratégias, rodada pelo host sem espera entre os pregões
    is_backtest: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    # As regras da partida: `SimulationSettingsDTO.model_dump(mode="json")` sem o
    # nome, o mesmo formato de `Preset.config`. A leitura valida o JSON inteiro
    # contra o DTO e recusa chave desconhecida: regra nova é um campo do DTO com
    # valor padrão; regra removida pede uma migration `rules - 'chave'`.
    rules: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Ranking calculado até o último dia gravado (`result_as_of`); serve a lista de
    # salvas enquanto a simulação não avança
    result: Mapped[dict | None] = mapped_column(JSONB)
    result_as_of: Mapped[datetime.date | None] = mapped_column(Date)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    last_simulated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    event_cashflow: Mapped[list["EventCashflow"]] = relationship(
        "EventCashflow", back_populates="simulation"
    )
    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="simulation"
    )
    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="simulation"
    )
    snapshots: Mapped[list["Snapshots"]] = relationship(
        "Snapshots", back_populates="simulation"
    )
    simulation_players: Mapped[list["SimulationPlayers"]] = relationship(
        "SimulationPlayers", back_populates="simulation"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("client_id", name="users_client_id_key"),
        # O apelido é único entre as pessoas; bot repete nome de uma partida para outra
        Index(
            "users_nickname_key",
            "nickname",
            unique=True,
            postgresql_where=text("NOT is_bot"),
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    nickname: Mapped[str] = mapped_column(Text, nullable=False)
    # Jogador sem pessoa por trás: o motor roda a estratégia dele a cada tick
    is_bot: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    settings: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    event_cashflow: Mapped[list["EventCashflow"]] = relationship(
        "EventCashflow", back_populates="user"
    )
    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="user"
    )
    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="user"
    )
    snapshots: Mapped[list["Snapshots"]] = relationship(
        "Snapshots", back_populates="user"
    )
    simulation_players: Mapped[list["SimulationPlayers"]] = relationship(
        "SimulationPlayers", back_populates="user"
    )


class SimulationPlayers(Base):
    __tablename__ = "simulation_players"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="simulation_players_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="simulation_players_user_id_fkey",
        ),
        PrimaryKeyConstraint(
            "simulation_id", "user_id", name="simulation_players_pkey"
        ),
        UniqueConstraint(
            "simulation_id", "color", name="simulation_players_simulation_id_color_key"
        ),
        CheckConstraint("team BETWEEN 1 AND 10", name="simulation_players_team_check"),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    color: Mapped[str] = mapped_column(Text, nullable=False)
    # Índice da equipe (1 a 10); nulo fora do modo em equipes
    team: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="simulation_players")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="simulation_players"
    )


class EventCashflow(Base):
    __tablename__ = "event_cashflow"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_cashflow_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="event_cashflow_stock_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_cashflow_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_cashflow_pkey"),
        Index(
            "event_cashflow_simulation_user_idx",
            "simulation_id",
            "user_id",
            "event_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Um valor de `CashflowEventType`
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # Qual imprevisto foi, para o histórico; nulo nos outros eventos
    life_event_key: Mapped[str | None] = mapped_column(Text)
    # O ativo de que veio o dividendo; nulo nos eventos que não vêm de um ativo
    stock_id: Mapped[int | None] = mapped_column(Integer)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    user: Mapped["Users"] = relationship("Users", back_populates="event_cashflow")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="event_cashflow"
    )


class EventEquity(Base):
    __tablename__ = "event_equity"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_equity_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="event_equity_stock_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_equity_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_equity_pkey"),
        Index(
            "event_equity_simulation_user_idx", "simulation_id", "user_id", "event_date"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Um valor de `EquityEventType`
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="event_equity")
    user: Mapped["Users"] = relationship("Users", back_populates="event_equity")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="event_equity"
    )


class EventFixedIncome(Base):
    __tablename__ = "event_fixed_income"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_fixed_income_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["asset_id"],
            ["fixed_income_asset.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_fixed_income_asset_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_fixed_income_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_fixed_income_pkey"),
        Index(
            "event_fixed_income_simulation_user_idx",
            "simulation_id",
            "user_id",
            "event_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Um valor de `FixedIncomeEventType`
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # IR e IOF retidos no resgate (bruto - líquido); zero na aplicação
    tax_withheld: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # Dólar do dia em reais; só a conta em dólar guarda
    fx_rate: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 8))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    asset: Mapped["FixedIncomeAsset"] = relationship(
        "FixedIncomeAsset", back_populates="event_fixed_income"
    )
    user: Mapped["Users"] = relationship("Users", back_populates="event_fixed_income")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="event_fixed_income"
    )


class EventCredit(Base):
    __tablename__ = "event_credit"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_credit_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_credit_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_credit_pkey"),
        Index(
            "event_credit_simulation_user_idx", "simulation_id", "user_id", "event_date"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    loan_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    # Um valor de `CreditEventType`
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # Número da parcela, nos eventos de parcela
    installment_number: Mapped[int | None] = mapped_column(Integer)
    # Só no contrato: juro anual travado, prazo e a nota da assinatura
    annual_rate: Mapped[decimal.Decimal | None] = mapped_column(Numeric(10, 6))
    term_months: Mapped[int | None] = mapped_column(Integer)
    grade: Mapped[str | None] = mapped_column(
        Enum("AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D", name="credit_grade")
    )
    # Só na amortização
    prepayment_mode: Mapped[str | None] = mapped_column(
        Enum("SHORTEN_TERM", "REDUCE_INSTALLMENT", name="credit_prepayment_mode")
    )
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class GovernmentEvent(Base):
    """Fonte da verdade da expansão Governo & Política: o estado político é o replay desta tabela."""

    __tablename__ = "government_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="government_event_simulation_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="government_event_pkey"),
        Index("government_event_simulation_id_idx", "simulation_id", "id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Um valor de `GovernmentEventType`
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    # Os dados do evento; o formato de cada tipo mora no DTO de `GovernmentEventDTO`
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class StrategyLog(Base):
    __tablename__ = "strategy_log"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="strategy_log_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="strategy_log_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="strategy_log_pkey"),
        Index("strategy_log_user_idx", "simulation_id", "user_id", "event_date"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    # order, enabled, switched, params, disabled, error, error_seen ou resumed
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    strategy_key: Mapped[str | None] = mapped_column(Text)
    params: Mapped[dict | None] = mapped_column(JSONB)
    # buy, sell, cancel ou invest
    action: Mapped[str | None] = mapped_column(Text)
    ticker: Mapped[str | None] = mapped_column(Text)
    asset_uuid: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    asset_name: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 8))
    price: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    order_type: Mapped[str | None] = mapped_column(Text)
    order_id: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    # executed, partial, open, canceled ou refused; só a linha de ordem muda depois de gravada
    status: Mapped[str | None] = mapped_column(Text)
    detail: Mapped[str | None] = mapped_column(Text)


class CandleChallengeStats(Base):
    """Os acertos do jogador no desafio da vela do lobby e a maior sequência dele."""

    __tablename__ = "candle_challenge_stats"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="candle_challenge_stats_user_id_fkey",
        ),
        PrimaryKeyConstraint("user_id", name="candle_challenge_stats_pkey"),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Total de acertos, somando todas as rodadas
    hits: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    # A maior sequência de acertos seguidos numa rodada e o dia em que ela saiu
    best_streak: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    best_streak_on: Mapped[datetime.date | None] = mapped_column(Date)


class Snapshots(Base):
    __tablename__ = "snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="snapshots_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="snapshots_user_id_fkey",
        ),
        PrimaryKeyConstraint(
            "simulation_id", "user_id", "snapshot_date", name="snapshots_pkey"
        ),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    total_equity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    total_fixed: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    total_cash: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    total_contribution: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # O patrimônio já desconta a dívida; ela fica à parte para o histórico e a nota de risco
    total_debt: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    total_networth: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # {tipo: valor} da renda variável
    equity_by_class: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )

    user: Mapped["Users"] = relationship("Users", back_populates="snapshots")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="snapshots"
    )


class Achievements(Base):
    __tablename__ = "achievements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="achievements_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="achievements_user_id_fkey",
        ),
        PrimaryKeyConstraint("user_id", "code", name="achievements_pkey"),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Código estável do catálogo; o texto e o ícone vivem no código
    code: Mapped[str] = mapped_column(Text, primary_key=True)
    # Nulo quando a partida em que saiu foi excluída: a conquista é do jogador
    simulation_id: Mapped[int | None] = mapped_column(BigInteger)
    unlocked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    # Dia da partida em que saiu
    game_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # Nulo até o jogador abrir a tela de conquistas
    seen_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(True))


class AchievementProgress(Base):
    """O melhor valor já alcançado numa conquista com meta, em qualquer partida."""

    __tablename__ = "achievement_progress"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="achievement_progress_user_id_fkey",
        ),
        PrimaryKeyConstraint("user_id", "code", name="achievement_progress_pkey"),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(Text, primary_key=True)
    best: Mapped[decimal.Decimal] = mapped_column(Numeric(30, 6), nullable=False)


class Summaries(Base):
    """A retrospectiva do ano de cada jogador, criada pelo motor na virada do ano."""

    __tablename__ = "summaries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="summaries_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="summaries_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="summaries_pkey"),
        Index("summaries_simulation_user_idx", "simulation_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer)
    game_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    kind: Mapped[str] = mapped_column(
        Enum("YEAR_REVIEW", name="summary_kind"),
        nullable=False,
    )
    # O formato do conteúdo mora em `YearReviewDTO`
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class News(Base):
    """As manchetes do jornal da partida, da sala inteira; o histórico é salvo com a partida."""

    __tablename__ = "news"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="news_simulation_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="news_pkey"),
        Index("news_simulation_date_idx", "simulation_id", "news_date"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(
            always=True,
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=9223372036854775807,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    news_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # Um valor de `NewsType`
    news_type: Mapped[str] = mapped_column(Text, nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    dek: Mapped[str | None] = mapped_column(Text)
    # Os ativos de que a manchete fala, para o filtro "só minha carteira"
    tickers: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    # Variação do dia do ativo da manchete, em pontos percentuais com sinal; vazia nas demais
    change_pct: Mapped[decimal.Decimal | None] = mapped_column(Numeric(8, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="stock_price_history_stock_id_fkey",
        ),
        PrimaryKeyConstraint(
            "stock_id", "price_date", "version", name="stock_price_history_pkey"
        ),
    )

    stock_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    open: Mapped[float] = mapped_column(Double(53), nullable=False)
    high: Mapped[float] = mapped_column(Double(53), nullable=False)
    low: Mapped[float] = mapped_column(Double(53), nullable=False)
    close: Mapped[float] = mapped_column(Double(53), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    origin: Mapped[str] = mapped_column(
        Enum("REAL", "GENERATED", name="data_origin"),
        nullable=False,
        server_default=text("'REAL'"),
    )
    # Dia em que a fonte errou o preço e o fechamento é a interpolação dos vizinhos
    price_corrected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    # 0 é a série comum; N é a cópia congelada da partida simulations.id = N
    version: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, server_default=text("0")
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="stock_price_history")


class StockCorporateEvent(Base):
    """Desdobramento ou dividendo de um ativo, no formato de `StockPriceHistory`."""

    __tablename__ = "stock_corporate_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="stock_corporate_event_stock_id_fkey",
        ),
        PrimaryKeyConstraint(
            "stock_id",
            "ex_date",
            "kind",
            "version",
            name="stock_corporate_event_pkey",
        ),
    )

    stock_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ex_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    kind: Mapped[str] = mapped_column(
        Enum("SPLIT", "DIVIDEND", name="corporate_event_kind"), primary_key=True
    )
    # Razão do desdobramento (2 é 2:1; 0,1 é grupamento 10:1) ou dividendo por cota, bruto
    value: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    origin: Mapped[str] = mapped_column(
        Enum("REAL", "GENERATED", name="data_origin"),
        nullable=False,
        server_default=text("'REAL'"),
    )
    # 0 é a série comum; N é a cópia congelada da partida simulations.id = N
    version: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, server_default=text("0")
    )

    stock: Mapped["Stock"] = relationship(
        "Stock", back_populates="stock_corporate_event"
    )


class TickerProfile(Base):
    __tablename__ = "ticker_profile"
    __table_args__ = (PrimaryKeyConstraint("ticker", name="ticker_profile_pkey"),)

    ticker: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    quote_type: Mapped[str | None] = mapped_column(Text)
    sector: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )
