"""strip sa suffix from tickers

Revision ID: 3b7e41c9d0a6
Revises: 9707da5dfa82
Create Date: 2026-10-21 15:02:41.719563
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "3b7e41c9d0a6"
down_revision: str | Sequence[str] | None = "9707da5dfa82"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# A base guarda o código da B3 sem o `.SA`; só `stock` e `ticker_profile` o guardam
# como texto, e os eventos e a carteira apontam para `stock.id`
_TICKER_TABLES = ("stock", "ticker_profile")


def upgrade() -> None:
    connection = op.get_bind()
    for table in _TICKER_TABLES:
        # Código que já existe sem o sufixo (vindo de CSV) não é mesclado em silêncio
        clashes = (
            connection.execute(
                text(
                    f"SELECT old.ticker FROM {table} old "
                    f"JOIN {table} bare ON bare.ticker = left(old.ticker, -3) "
                    "WHERE old.ticker LIKE '%.SA'"
                )
            )
            .scalars()
            .all()
        )
        if clashes:
            raise RuntimeError(
                f"Em {table}, o código já existe com e sem o .SA: "
                f"{', '.join(clashes)}. Apague uma das linhas de cada par e rode de novo."
            )
        connection.execute(
            text(
                f"UPDATE {table} SET ticker = left(ticker, -3) WHERE ticker LIKE '%.SA'"
            )
        )


def downgrade() -> None:
    # O código sem o sufixo é o formato da base: não há o que desfazer
    pass
