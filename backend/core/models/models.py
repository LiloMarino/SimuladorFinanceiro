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
            "IVG_R",
            "IGP_M",
            "TR",
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
            "IVG_R",
            "IGP_M",
            "TR",
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
        Enum("STOCK", "FII", "ETF", "BDR", "CRYPTO", "FUND", name="asset_class"),
        nullable=False,
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
    portfolios: Mapped[list["Portfolios"]] = relationship(
        "Portfolios", back_populates="simulation"
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

    portfolios: Mapped[list["Portfolios"]] = relationship(
        "Portfolios", back_populates="user"
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
    # Nome da profissão no viver de renda com profissões; nulo vale CLT
    profession: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Sigla do partido que o Comissionado escolheu; nulo nas demais profissões
    party: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="simulation_players")
    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="simulation_players"
    )


class Portfolios(Base):
    """A carteira de um jogador numa partida: dona dos eventos e dos snapshots dela."""

    __tablename__ = "portfolios"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="portfolios_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="portfolios_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="portfolios_pkey"),
        UniqueConstraint(
            "simulation_id", "user_id", name="portfolios_simulation_id_user_id_key"
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
    # O dono da carteira; nulo na carteira de uma gestora
    user_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
    # O capital com que o jogador entrou na partida: a base do capital colocado dele
    starting_cash: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )

    simulation: Mapped["Simulations"] = relationship(
        "Simulations", back_populates="portfolios"
    )
    user: Mapped["Users | None"] = relationship("Users", back_populates="portfolios")
    event_cashflow: Mapped[list["EventCashflow"]] = relationship(
        "EventCashflow", back_populates="portfolio"
    )
    event_equity: Mapped[list["EventEquity"]] = relationship(
        "EventEquity", back_populates="portfolio"
    )
    event_fixed_income: Mapped[list["EventFixedIncome"]] = relationship(
        "EventFixedIncome", back_populates="portfolio"
    )
    snapshots: Mapped[list["Snapshots"]] = relationship(
        "Snapshots", back_populates="portfolio"
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
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_cashflow_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_cashflow_pkey"),
        Index(
            "event_cashflow_simulation_portfolio_idx",
            "simulation_id",
            "portfolio_id",
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
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
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

    portfolio: Mapped["Portfolios"] = relationship(
        "Portfolios", back_populates="event_cashflow"
    )
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
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_equity_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_equity_pkey"),
        Index(
            "event_equity_simulation_portfolio_idx",
            "simulation_id",
            "portfolio_id",
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
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
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
    portfolio: Mapped["Portfolios"] = relationship(
        "Portfolios", back_populates="event_equity"
    )
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
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_fixed_income_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_fixed_income_pkey"),
        Index(
            "event_fixed_income_simulation_portfolio_idx",
            "simulation_id",
            "portfolio_id",
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
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
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
    portfolio: Mapped["Portfolios"] = relationship(
        "Portfolios", back_populates="event_fixed_income"
    )
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
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="event_credit_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="event_credit_pkey"),
        Index(
            "event_credit_simulation_portfolio_idx",
            "simulation_id",
            "portfolio_id",
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
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
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
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="strategy_log_fund_id_fkey",
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
    # A gestora dona da linha; ausente, a linha é da conta pessoal do jogador
    fund_id: Mapped[int | None] = mapped_column(BigInteger)
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
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="snapshots_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint(
            "simulation_id", "portfolio_id", "snapshot_date", name="snapshots_pkey"
        ),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
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

    portfolio: Mapped["Portfolios"] = relationship(
        "Portfolios", back_populates="snapshots"
    )
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
    # As siglas dos partidos que a manchete cita, na ordem do texto
    party_abbrs: Mapped[list[str]] = mapped_column(
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
    # Ações em circulação que o yfinance informa; base do número de ações de uma estatal
    shares_outstanding: Mapped[int | None] = mapped_column(BigInteger)
    fetched_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=text("now()")
    )


class Funds(Base):
    """Uma gestora numa partida: a cota é uma linha de `stock` e o caixa e as posições moram na carteira dela."""

    __tablename__ = "funds"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="funds_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="funds_stock_id_fkey",
        ),
        ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="funds_portfolio_id_fkey",
        ),
        ForeignKeyConstraint(
            ["founder_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="funds_founder_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["manager_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="funds_manager_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["merged_into_fund_id"],
            ["funds.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="funds_merged_into_fund_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="funds_pkey"),
        UniqueConstraint("portfolio_id", name="funds_portfolio_id_key"),
        UniqueConstraint(
            "simulation_id", "stock_id", name="funds_simulation_stock_key"
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
    # A cota da gestora
    stock_id: Mapped[int] = mapped_column(Integer, nullable=False)
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # A conta da gestora no motor
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    founder_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    manager_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # Cotas em circulação, com as do formador de mercado
    quotas: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    maker_quotas: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # Caixa sintético do formador: fica só nesta linha, para auditoria
    maker_cash: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # Cotas da oferta pública ainda à venda; nulo sem oferta aberta
    offer_remaining: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    # Dia da oferta pública; nulo antes dela
    listed_on: Mapped[datetime.date | None] = mapped_column(Date)
    # Cotas postas à venda na oferta e o preço delas, fixados na abertura; nulos sem oferta
    offer_quotas: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    offer_price: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    # Dia em que a oferta fechou; nulo com a oferta aberta ou sem oferta
    offer_closed_on: Mapped[datetime.date | None] = mapped_column(Date)
    # Dia em que a oferta automática do modo aquisição hostil abriu; nulo sem ela
    takeover_offer_on: Mapped[datetime.date | None] = mapped_column(Date)
    management_fee: Mapped[decimal.Decimal] = mapped_column(
        Numeric(8, 6), nullable=False
    )
    performance_fee: Mapped[decimal.Decimal] = mapped_column(
        Numeric(8, 6), nullable=False
    )
    # Troca de taxa pedida: vale a partir de `pending_from`
    pending_management_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    pending_performance_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    pending_from: Mapped[datetime.date | None] = mapped_column(Date)
    # PL por cota que a performance precisa superar, corrigido pelo CDI desde `high_water_mark_on`
    high_water_mark: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    high_water_mark_on: Mapped[datetime.date | None] = mapped_column(Date)
    last_performance_on: Mapped[datetime.date | None] = mapped_column(Date)
    # Parte do lucro realizado do mês que vira rendimento aos cotistas (0,95 é 95%); a troca
    # pedida vale a partir de `pending_from`, junto das taxas
    distribution_rate: Mapped[decimal.Decimal] = mapped_column(
        Numeric(8, 6), nullable=False, server_default=text("0.95")
    )
    pending_distribution_rate: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    # Dia em que o gestor de hoje assumiu a gestora
    manager_since: Mapped[datetime.date | None] = mapped_column(Date)
    # O gestor que passou a gestão ao herdeiro na posse da presidência e a parte que o herdeiro
    # tinha nas taxas antes de virar principal; nulos sem gestor em licença
    leave_manager_user_id: Mapped[int | None] = mapped_column(Integer)
    leave_heir_share: Mapped[decimal.Decimal | None] = mapped_column(Numeric(8, 6))
    # O lucro realizado desde a última data-com, por origem: dividendos, juros e cupons da
    # renda fixa, ganho nas vendas e taxas pagas
    month_dividends: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    month_interest: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    month_sales_gain: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    month_fees: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # A taxa que o caixa não cobriu, por tipo: dívida da gestora com o gestor, quitada pelo
    # próximo dinheiro que entra
    management_fee_payable: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    performance_fee_payable: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # A gestora que incorporou esta e o dia da fusão; nulos enquanto ela existe por si
    merged_into_fund_id: Mapped[int | None] = mapped_column(BigInteger)
    merged_on: Mapped[datetime.date | None] = mapped_column(Date)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )


class FundDistributions(Base):
    """O rendimento de um mês da gestora: o que a data-com apurou e, depois, o que foi pago."""

    __tablename__ = "fund_distributions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_distributions_fund_id_fkey",
        ),
        PrimaryKeyConstraint("fund_id", "data_com", name="fund_distributions_pkey"),
    )

    fund_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # O último pregão do mês, em que o lucro realizado fecha
    data_com: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    realized_profit: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # A parte distribuída em vigor na data-com
    rate: Mapped[decimal.Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    # As cotas fora do formador que dividem o rendimento e o valor por cota apurado
    quotas: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    per_quota: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # O que foi pago de fato e quando; nulos até o primeiro pregão do mês seguinte
    paid_per_quota: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    paid: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    paid_on: Mapped[datetime.date | None] = mapped_column(Date)


class FundDays(Base):
    """O fechamento de uma gestora num pregão: o PL por cota, o giro e o preço de ranking."""

    __tablename__ = "fund_days"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_days_fund_id_fkey",
        ),
        PrimaryKeyConstraint("fund_id", "day", name="fund_days_pkey"),
    )

    fund_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    day: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    # PL por cota
    nav: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    quotas: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    traded_quantity: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # Soma de preço vezes quantidade dos negócios do dia
    traded_value: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    ranking_price: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )
    # A taxa a pagar da gestora no fim do pregão
    fee_payable: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # O saldo devedor dos empréstimos da gestora no fim do pregão
    loan_debt: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )


class FundOfferSales(Base):
    """Uma venda da oferta pública: as cotas que o comprador levou da gestora, ao preço da oferta."""

    __tablename__ = "fund_offer_sales"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_offer_sales_fund_id_fkey",
        ),
        ForeignKeyConstraint(
            ["buyer_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_offer_sales_buyer_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["issuance_id"],
            ["fund_issuances.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_offer_sales_issuance_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_offer_sales_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    day: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # Nulo quando o comprador é o formador de mercado da própria gestora
    buyer_user_id: Mapped[int | None] = mapped_column(Integer)
    quotas: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # A emissão a que a venda pertence; nulo na oferta pública de abertura
    issuance_id: Mapped[int | None] = mapped_column(BigInteger)


class FundIssuances(Base):
    """Uma emissão de cotas novas: preço fixado no anúncio, preferência dos cotistas e depois a sobra aberta."""

    __tablename__ = "fund_issuances"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_issuances_fund_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_issuances_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    announced_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # As cotas postas à venda e o preço (o PL por cota do dia do anúncio), fixos até o fim
    quotas: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # Último dia da preferência e último dia da sobra aberta
    preference_ends_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # Cotas que nasceram até agora (preferência e sobra)
    sold: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # O dia em que a emissão fechou; nulo com ela aberta
    closed_on: Mapped[datetime.date | None] = mapped_column(Date)
    # O preço de fechamento da cota na sessão anterior ao anúncio, fixo até o fim da emissão; nulo = sem ágio
    book_price: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))


class FundIssuanceRights(Base):
    """O direito de preferência de um jogador numa emissão, pela proporção que ele tinha no anúncio."""

    __tablename__ = "fund_issuance_rights"
    __table_args__ = (
        ForeignKeyConstraint(
            ["issuance_id"],
            ["fund_issuances.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_issuance_rights_issuance_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_issuance_rights_user_id_fkey",
        ),
        PrimaryKeyConstraint(
            "issuance_id", "user_id", name="fund_issuance_rights_pkey"
        ),
    )

    issuance_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Cotas que o jogador pode comprar na preferência e quantas já comprou
    rights: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    bought: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)


class FundBuybacks(Base):
    """Uma recompra: a ordem de compra da gestora no livro, cujas cotas compradas deixam de existir."""

    __tablename__ = "fund_buybacks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_buybacks_fund_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_buybacks_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    announced_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    quantity: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    max_price: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # Cotas já recompradas e o total pago por elas
    bought: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    paid: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # Um valor de `FundBuybackState`
    state: Mapped[str] = mapped_column(Text, nullable=False)


class FundAssemblies(Base):
    """Uma assembleia de cotistas: a pauta, o convite ao aliado (troca de gestor), a votação e o resultado."""

    __tablename__ = "fund_assemblies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assemblies_fund_id_fkey",
        ),
        ForeignKeyConstraint(
            ["convener_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assemblies_convener_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["candidate_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assemblies_candidate_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["previous_manager_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assemblies_previous_manager_user_id_fkey",
        ),
        ForeignKeyConstraint(
            ["partner_fund_id"],
            ["funds.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
            name="fund_assemblies_partner_fund_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_assemblies_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    convener_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # O indicado a gestor; nulo nas pautas que não trocam o gestor
    candidate_user_id: Mapped[int | None] = mapped_column(Integer)
    # O gestor de quando a assembleia foi convocada
    previous_manager_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Um valor de `FundAssemblyAgenda`
    agenda: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'REPLACE_MANAGER'")
    )
    # Um valor de `FundAssemblyStatus`
    status: Mapped[str] = mapped_column(Text, nullable=False)
    called_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # O dia em que a votação abriu; nulo enquanto o convite espera o aliado
    started_on: Mapped[datetime.date | None] = mapped_column(Date)
    # O último pregão da fase de agora: o do convite ou o da votação
    ends_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    closed_on: Mapped[datetime.date | None] = mapped_column(Date)
    # O placar do fechamento, em cotas; nulo até a votação fechar
    in_favor_quotas: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    against_quotas: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    abstention_quotas: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    # As taxas da pauta de aumento: as de quando foi proposto e as propostas; nulas nas outras pautas
    previous_management_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    previous_performance_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    proposed_management_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    proposed_performance_fee: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(8, 6)
    )
    # Na pauta de fusão: a outra gestora e se esta é a incorporada; nulos nas outras pautas
    partner_fund_id: Mapped[int | None] = mapped_column(BigInteger)
    absorbed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    # O que faltou nos caixas para pagar a saída de quem votou contra, quando isso rejeitou a fusão no fechamento
    merge_shortfall: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))


class FundAssemblyVotes(Base):
    """O voto de um cotista numa assembleia; ele muda até o fim da votação."""

    __tablename__ = "fund_assembly_votes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["assembly_id"],
            ["fund_assemblies.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assembly_votes_assembly_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_assembly_votes_user_id_fkey",
        ),
        PrimaryKeyConstraint("assembly_id", "user_id", name="fund_assembly_votes_pkey"),
    )

    assembly_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    in_favor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    voted_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)


class FundComanagers(Base):
    """Um co-gestor da gestora: o convite pendente ou o gestor ativo, com a parte das taxas dele."""

    __tablename__ = "fund_comanagers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_comanagers_fund_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_comanagers_user_id_fkey",
        ),
        PrimaryKeyConstraint("fund_id", "user_id", name="fund_comanagers_pkey"),
    )

    fund_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Um valor de `FundComanagerStatus`
    status: Mapped[str] = mapped_column(Text, nullable=False)
    # A parte das taxas em vigor, como fração: 0,30 é 30%; zero enquanto o convite espera
    share: Mapped[decimal.Decimal] = mapped_column(Numeric(7, 6), nullable=False)
    # A parte agendada e o dia em que passa a valer
    pending_share: Mapped[decimal.Decimal | None] = mapped_column(Numeric(7, 6))
    pending_from: Mapped[datetime.date | None] = mapped_column(Date)
    invited_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # O dia em que aceitou; nulo enquanto o convite espera
    since: Mapped[datetime.date | None] = mapped_column(Date)


class FundComanagerEvents(Base):
    """A entrada ou a saída de um co-gestor, para os movimentos da página da gestora."""

    __tablename__ = "fund_comanager_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_comanager_events_fund_id_fkey",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_comanager_events_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_comanager_events_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # `joined` (aceitou o convite) ou `left` (saiu, foi removido ou deixou a gestão)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    day: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # A parte das taxas de quem entrou; nula na saída
    share: Mapped[decimal.Decimal | None] = mapped_column(Numeric(7, 6))


class FundDirectedIssuances(Base):
    """A emissão dirigida: cotas novas que o gestor principal vende a si ou a um co-gestor."""

    __tablename__ = "fund_directed_issuances"
    __table_args__ = (
        ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_directed_issuances_fund_id_fkey",
        ),
        ForeignKeyConstraint(
            ["buyer_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="fund_directed_issuances_buyer_user_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="fund_directed_issuances_pkey"),
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
    fund_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buyer_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quotas: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    offered_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    # Um valor de `FundDirectedIssuanceStatus`
    status: Mapped[str] = mapped_column(Text, nullable=False)
    # O preço e o dia da liquidação; nulos enquanto a oferta espera ou se ela não liquidou
    price: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))
    settled_on: Mapped[datetime.date | None] = mapped_column(Date)


class StateOwnedStocks(Base):
    """A marcação da base: o ativo importado que o governo controla em toda partida nova."""

    __tablename__ = "state_owned_stocks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_owned_stocks_stock_id_fkey",
        ),
        PrimaryKeyConstraint("stock_id", name="state_owned_stocks_pkey"),
        CheckConstraint(
            "government_share > 0 AND government_share <= 1",
            name="state_owned_stocks_share_check",
        ),
        CheckConstraint("shares > 0", name="state_owned_stocks_shares_check"),
    )

    stock_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Fatia do governo em fração: 0,5 é metade das ações
    government_share: Mapped[decimal.Decimal] = mapped_column(
        Numeric(6, 5), nullable=False
    )
    # Ações em circulação da empresa
    shares: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Um valor de `StateLever`; nulo quando a empresa não tem preço a segurar
    lever: Mapped[str | None] = mapped_column(Text)


class StateCompanies(Base):
    """Uma estatal numa partida: importada da marcação da base ou fundada pelo governo."""

    __tablename__ = "state_companies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_companies_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["stock_id"],
            ["stock.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_companies_stock_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="state_companies_pkey"),
        UniqueConstraint(
            "simulation_id", "stock_id", name="state_companies_simulation_stock_key"
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
    stock_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Um valor de `StateCompanyOrigin`
    origin: Mapped[str] = mapped_column(Text, nullable=False)
    government_share: Mapped[decimal.Decimal] = mapped_column(
        Numeric(6, 5), nullable=False
    )
    shares: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Um valor de `StateLever`; nulo sem preço a segurar
    lever: Mapped[str | None] = mapped_column(Text)
    # Um valor de `StateCompanySize`; só a fundada tem porte
    size: Mapped[str | None] = mapped_column(Text)
    # Capital que o governo pôs na fundação; zero na importada
    invested: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, server_default=text("0")
    )
    # Retorno anual médio e semente do sorteio do valor justo; nulos na importada, que segue a história
    mean_return: Mapped[decimal.Decimal | None] = mapped_column(Numeric(8, 6))
    seed: Mapped[int | None] = mapped_column(BigInteger)
    # Um valor de `StateCompanyStatus`
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'ACTIVE'")
    )
    founded_on: Mapped[datetime.date | None] = mapped_column(Date)
    # Dia em que a oferta de privatização abriu
    offer_opened_on: Mapped[datetime.date | None] = mapped_column(Date)
    privatized_on: Mapped[datetime.date | None] = mapped_column(Date)
    # O que o governo recebeu pela fatia na privatização
    proceeds: Mapped[decimal.Decimal | None] = mapped_column(Numeric(20, 6))


class StateCompanyMonths(Base):
    """O mês de uma estatal: o valor justo, o lucro e o dividendo que foi ao Tesouro."""

    __tablename__ = "state_company_months"
    __table_args__ = (
        ForeignKeyConstraint(
            ["state_company_id"],
            ["state_companies.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_company_months_state_company_id_fkey",
        ),
        PrimaryKeyConstraint(
            "state_company_id", "month", name="state_company_months_pkey"
        ),
    )

    state_company_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Primeiro dia do mês
    month: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    fair_value: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    profit: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    treasury_dividend: Mapped[decimal.Decimal] = mapped_column(
        Numeric(20, 6), nullable=False
    )


class StateOfferReservations(Base):
    """A reserva de uma conta na oferta de privatização: quantas ações ela pede, sem gastar caixa."""

    __tablename__ = "state_offer_reservations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["state_company_id"],
            ["state_companies.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_offer_reservations_state_company_id_fkey",
        ),
        ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="state_offer_reservations_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint(
            "state_company_id", "portfolio_id", name="state_offer_reservations_pkey"
        ),
        CheckConstraint("quantity > 0", name="state_offer_reservations_quantity_check"),
    )

    state_company_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # A conta que reserva: a carteira do jogador ou a da gestora que ele comanda
    portfolio_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    quantity: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    reserved_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)


class SovereignFunds(Base):
    """O Fundo Soberano de uma partida: o caixa e as posições moram na carteira dele, que não tem dono jogador."""

    __tablename__ = "sovereign_funds"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="sovereign_funds_simulation_id_fkey",
        ),
        ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="sovereign_funds_portfolio_id_fkey",
        ),
        PrimaryKeyConstraint("simulation_id", name="sovereign_funds_pkey"),
        UniqueConstraint("portfolio_id", name="sovereign_funds_portfolio_id_key"),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # A conta do fundo no motor
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)


class SovereignFundFlows(Base):
    """Cada movimento entre o fundo e o Tesouro: aporte, venda e dividendo, com o dia em que aconteceu."""

    __tablename__ = "sovereign_fund_flows"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id"],
            ["simulations.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="sovereign_fund_flows_simulation_id_fkey",
        ),
        PrimaryKeyConstraint("id", name="sovereign_fund_flows_pkey"),
        # Cada aporte aprovado entra uma vez só
        UniqueConstraint(
            "simulation_id",
            "kind",
            "measure_id",
            name="sovereign_fund_flows_measure_key",
        ),
        CheckConstraint("amount > 0", name="sovereign_fund_flows_amount_check"),
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
    day: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    # A medida do aporte; nulo na venda e no dividendo
    measure_id: Mapped[int | None] = mapped_column(Integer)


class ProfessionStates(Base):
    """O estado da mecânica da profissão de um jogador numa partida: uma linha por jogador."""

    __tablename__ = "profession_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id", "user_id"],
            ["simulation_players.simulation_id", "simulation_players.user_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="profession_states_player_fkey",
        ),
        PrimaryKeyConstraint("simulation_id", "user_id", name="profession_states_pkey"),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # `MechanicState.model_dump(mode="json")` do tipo da profissão atual do jogador
    state: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ProfessionPeriods(Base):
    """A profissão que o jogador exerce a partir de um dia; o período dura até o início do seguinte."""

    __tablename__ = "profession_periods"
    __table_args__ = (
        ForeignKeyConstraint(
            ["simulation_id", "user_id"],
            ["simulation_players.simulation_id", "simulation_players.user_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="profession_periods_player_fkey",
        ),
        PrimaryKeyConstraint(
            "simulation_id", "user_id", "start_date", name="profession_periods_pkey"
        ),
    )

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    profession: Mapped[str] = mapped_column(Text, nullable=False)
