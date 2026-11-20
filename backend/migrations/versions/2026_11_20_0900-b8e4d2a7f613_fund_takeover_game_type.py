"""fund takeover game type

Revision ID: b8e4d2a7f613
Revises: d7b3f4a6c819
Create Date: 2026-11-20 09:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "b8e4d2a7f613"
down_revision: str | Sequence[str] | None = "d7b3f4a6c819"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Onde as regras moram como JSON: (tabela, coluna)
_RULE_COLUMNS = (
    ("simulations", "rules"),
    ("preset", "config"),
    ("last_simulation_settings", "settings"),
)


def _becomes_takeover(column: str) -> str:
    """Só a Clássica individual com a expansão Gestoras e o modo hostil ligado vira o tipo novo."""
    return (
        f"coalesce(({column}->>'fund_takeover_enabled')::boolean, false)"
        f" AND coalesce({column}->>'game_type', 'CLASSIC') = 'CLASSIC'"
        f" AND coalesce({column}->>'player_grouping', 'INDIVIDUAL') = 'INDIVIDUAL'"
        f" AND coalesce(({column}->>'funds_enabled')::boolean, false)"
    )


def upgrade() -> None:
    # O ranking guardado das salvas convertidas é recalculado pela regra nova
    op.execute(
        f"UPDATE simulations SET result = NULL, result_as_of = NULL "
        f"WHERE {_becomes_takeover('rules')}"
    )
    for table, column in _RULE_COLUMNS:
        # O modo hostil ligado em qualquer outro tipo se apaga; o tipo que a partida tinha fica
        op.execute(
            f"UPDATE {table} SET {column} = CASE WHEN {_becomes_takeover(column)} "
            f"THEN jsonb_set({column} - 'fund_takeover_enabled', '{{game_type}}', "
            f"'\"FUND_TAKEOVER\"') "
            f"ELSE {column} - 'fund_takeover_enabled' END "
            f"WHERE jsonb_exists({column}, 'fund_takeover_enabled')"
        )


def downgrade() -> None:
    for table, column in _RULE_COLUMNS:
        op.execute(
            f"UPDATE {table} SET {column} = jsonb_set({column}, '{{game_type}}', "
            f"'\"CLASSIC\"') || '{{\"fund_takeover_enabled\": true}}'::jsonb "
            f"WHERE {column}->>'game_type' = 'FUND_TAKEOVER'"
        )
    op.execute(
        "UPDATE simulations SET result = NULL, result_as_of = NULL "
        "WHERE rules->>'fund_takeover_enabled' = 'true'"
    )
