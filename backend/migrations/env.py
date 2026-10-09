from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from backend import config as app_config
from backend.core.models.models import Base

# A URL vem do `migration.py`; pela CLI (`pnpm db:revision`) vale a do .env
alembic_config = context.config
url = (
    alembic_config.get_section(alembic_config.config_ini_section, {}).get(
        "sqlalchemy.url"
    )
    or app_config.env.postgres_url
)


def run_migrations() -> None:
    # O DDL do Postgres é transacional: uma migration que falha é desfeita inteira
    engine = create_engine(url, poolclass=NullPool)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=Base.metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


run_migrations()
