"""tighten schema 4.0

Revision ID: f3a8c5d1b764
Revises: e9c4a6b2d813
Create Date: 2026-11-07 22:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3a8c5d1b764"
down_revision: str | Sequence[str] | None = "e9c4a6b2d813"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Coluna de tipo de evento e o ENUM nativo que ela usava
EVENT_TYPE_COLUMNS: list[tuple[str, str, str]] = [
    ("event_cashflow", "event_type", "cashflow_event_type"),
    ("event_equity", "event_type", "equity_event_type"),
    ("event_fixed_income", "event_type", "fixed_income_event_type"),
    ("event_credit", "event_type", "credit_event_type"),
    ("government_event", "event_type", "government_event_type"),
    ("news", "news_type", "news_type"),
]

# Os valores de cada ENUM, na ordem em que o tipo nasceu
ENUM_VALUES: dict[str, list[str]] = {
    "cashflow_event_type": [
        "DEPOSIT",
        "WITHDRAW",
        "DIVIDEND",
        "CONTRIBUTION",
        "TAX",
        "SALARY",
        "EXPENSE",
        "UNEXPECTED_EXPENSE",
        "OVERDRAFT_INTEREST",
        "LOAN_PROCEEDS",
        "LOAN_PAYMENT",
        "CAMPAIGN_CONTRIBUTION",
        "CAMPAIGN_DONATION",
        "CAMPAIGN_ACTION",
    ],
    "equity_event_type": [
        "BUY",
        "SELL",
        "SPLIT",
        "FRACTION_SELL",
    ],
    "fixed_income_event_type": [
        "BUY",
        "REDEEM",
    ],
    "credit_event_type": [
        "CONTRACT",
        "INSTALLMENT_PAID",
        "INSTALLMENT_LATE",
        "OVERDUE_PAID",
        "PREPAYMENT",
        "PAYOFF",
    ],
    "government_event_type": [
        "PARTY_FOUNDED",
        "COMPUTER_PARTY_ADDED",
        "COMPUTER_PARTY_REMOVED",
        "PARTY_JOINED",
        "PARTY_LEFT",
        "MEMBER_EXPELLED",
        "CONTRIBUTION_SET",
        "TICKET_SET",
        "VICE_ANSWERED",
        "CAMPAIGN_SPENT",
        "DONATION_MADE",
        "ELECTION_ROUND",
        "TERM_STARTED",
        "MEASURE_PROPOSED",
        "MEASURE_WITHDRAWN",
        "MEASURE_VOTED",
        "APPROVAL_MEASURED",
        "IMPEACHED",
        "PARTY_VALUES_SET",
        "CAMPAIGN_ACTION",
        "PROMISES_SET",
        "PROMISES_WEIGHED",
        "PROMISES_SETTLED",
        "HOUSE_ELECTED",
        "BLOC_GUIDED",
        "GUIDANCE_RULE_SET",
        "IMPEACHMENT_REQUESTED",
        "IMPEACHMENT_VOTED",
        "DEAL_PROPOSED",
        "DEAL_ANSWERED",
        "DEAL_WITHDRAWN",
        "DEAL_BROKEN",
        "RUNOFF_ENDORSED",
        "RUNOFF_CONTRIBUTION",
        "RUNOFF_POLL",
        "PARTIES_PREPARED",
        "SELIC_SET",
        "SELIC_DECIDED",
        "FEDERATION_PROPOSED",
        "FEDERATION_WITHDRAWN",
        "FEDERATION_ANSWERED",
        "FEDERATION_LEFT",
        "FEDERATION_ENDED",
    ],
    "news_type": [
        "ELECTION_CALENDAR",
        "ELECTION_RESULT",
        "TERM_STARTED",
        "MEASURE_PROPOSED",
        "MEASURE_VOTED",
        "PARTY_LIFE",
        "CAMPAIGN",
        "COPOM_DECISION",
        "MONTHLY_INFLATION",
        "IBOVESPA_EXTREME",
        "STRONG_MOVE",
        "WEEK_HIGH",
        "HISTORICAL_MILESTONE",
    ],
}

EVENT_TABLES = ["event_cashflow", "event_equity", "event_fixed_income", "event_credit"]


def upgrade() -> None:
    for table, column, enum_name in EVENT_TYPE_COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.Text(),
            postgresql_using=f"{column}::text",
            existing_nullable=False,
        )
        op.execute(f"DROP TYPE {enum_name}")

    for table in EVENT_TABLES:
        op.create_index(
            f"{table}_simulation_user_idx",
            table,
            ["simulation_id", "user_id", "event_date"],
        )

    # O título pertence à partida que o emitiu; o UUID dele já leva o id dela
    op.add_column(
        "fixed_income_asset", sa.Column("simulation_id", sa.BigInteger(), nullable=True)
    )
    op.execute(
        "UPDATE fixed_income_asset a SET simulation_id = ("
        "SELECT min(e.simulation_id) FROM event_fixed_income e WHERE e.asset_id = a.id)"
    )
    op.execute("DELETE FROM fixed_income_asset WHERE simulation_id IS NULL")
    op.alter_column("fixed_income_asset", "simulation_id", nullable=False)
    op.drop_constraint("fixed_income_asset_uuid_key", "fixed_income_asset")
    op.create_unique_constraint(
        "fixed_income_asset_simulation_uuid_key",
        "fixed_income_asset",
        ["simulation_id", "asset_uuid"],
    )
    op.create_foreign_key(
        "fixed_income_asset_simulation_id_fkey",
        "fixed_income_asset",
        "simulations",
        ["simulation_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )
    op.drop_constraint("event_fixed_income_asset_id_fkey", "event_fixed_income")
    op.create_foreign_key(
        "event_fixed_income_asset_id_fkey",
        "event_fixed_income",
        "fixed_income_asset",
        ["asset_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    op.execute(
        "UPDATE snapshots SET equity_by_class = '{}' WHERE equity_by_class IS NULL"
    )
    op.alter_column("snapshots", "equity_by_class", nullable=False)
    op.alter_column("snapshots", "total_debt", server_default=None)
    op.alter_column("generated_future", "surge_frequency", server_default=None)
    op.alter_column("generated_future", "surge_intensity", server_default=None)
    op.alter_column("event_fixed_income", "tax_withheld", server_default=None)


def downgrade() -> None:
    op.alter_column("event_fixed_income", "tax_withheld", server_default=sa.text("0"))
    op.alter_column("generated_future", "surge_intensity", server_default="6")
    op.alter_column("generated_future", "surge_frequency", server_default="0")
    op.alter_column("snapshots", "total_debt", server_default=sa.text("0"))
    op.alter_column("snapshots", "equity_by_class", nullable=True)

    op.drop_constraint("event_fixed_income_asset_id_fkey", "event_fixed_income")
    op.create_foreign_key(
        "event_fixed_income_asset_id_fkey",
        "event_fixed_income",
        "fixed_income_asset",
        ["asset_id"],
        ["id"],
        ondelete="RESTRICT",
        onupdate="CASCADE",
    )
    op.drop_constraint("fixed_income_asset_simulation_id_fkey", "fixed_income_asset")
    op.drop_constraint("fixed_income_asset_simulation_uuid_key", "fixed_income_asset")
    op.create_unique_constraint(
        "fixed_income_asset_uuid_key", "fixed_income_asset", ["asset_uuid"]
    )
    op.drop_column("fixed_income_asset", "simulation_id")

    for table in EVENT_TABLES:
        op.drop_index(f"{table}_simulation_user_idx", table)

    bind = op.get_bind()
    for table, column, enum_name in EVENT_TYPE_COLUMNS:
        sa.Enum(*ENUM_VALUES[enum_name], name=enum_name).create(bind)
        op.alter_column(
            table,
            column,
            type_=sa.Enum(name=enum_name),
            postgresql_using=f"{column}::{enum_name}",
            existing_nullable=False,
        )
