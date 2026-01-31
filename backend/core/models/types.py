from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# JSON type that uses JSONB on PostgreSQL and JSON on SQLite
JSONType = JSON().with_variant(JSONB(), "postgresql")
