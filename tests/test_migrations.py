"""As migrations chegam exatamente no schema dos models, e o `migrate` guarda só os
backups mais recentes."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from backend.core.migration import (
    backups_to_drop,
    current_revision,
    head_revision,
    schema_diff,
)


def test_schema_matches_models(migrated_template: URL) -> None:
    """O banco modelo da sessão subiu até o head, e o `compare_metadata` não acha diferença."""
    # Sem pool: o modelo só aceita ser copiado sem nenhuma conexão aberta nele.
    engine = create_engine(migrated_template, poolclass=NullPool)
    try:
        assert schema_diff(engine) == []
        assert current_revision(engine) == head_revision()
    finally:
        engine.dispose()


def test_only_the_latest_backups_are_kept() -> None:
    backups = [
        "db_bkp_20261003_101500",
        "db_bkp_20261001_090000",
        "db_bkp_20261009_120000",
        "db_bkp_20261005_080000",
    ]

    assert backups_to_drop(backups, keep=3) == ["db_bkp_20261001_090000"]
    assert backups_to_drop(backups[:2], keep=3) == []
