"""Gera, a partir dos models, os arquivos que a página do diagrama do banco consome.

Roda dentro do `pnpm start` e do `pnpm build` dos docs (`pnpm db:erd`): os dois
arquivos gerados não são versionados e acompanham sempre o `Base.metadata`.
"""

import json
from pathlib import Path

from sqlalchemy import Enum, MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from backend.core.models.models import Base

DDL_PATH = Path("docs/src/generated/schema.json")
ENUMS_PATH = Path("docs/docs/desenvolvimento/_enums.md")


def render_ddl(metadata: MetaData) -> str:
    # sorted_tables põe cada tabela depois das que ela referencia
    statements = (
        str(CreateTable(table).compile(dialect=postgresql.dialect())).strip() + ";"
        for table in metadata.sorted_tables
    )
    return "\n".join(statements)


def render_enums(metadata: MetaData) -> str:
    enums: dict[str, tuple[list[str], list[str]]] = {}
    for table in metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, Enum) and column.type.name:
                _, columns = enums.setdefault(
                    column.type.name, (list(column.type.enums), [])
                )
                columns.append(f"`{table.name}.{column.name}`")
    rows = [
        f"| `{name}` | {', '.join(f'`{v}`' for v in values)} | {', '.join(columns)} |"
        for name, (values, columns) in sorted(enums.items())
    ]
    header = ["| ENUM | Valores | Colunas |", "| --- | --- | --- |"]
    return "\n".join([*header, *rows, ""])


def main() -> None:
    DDL_PATH.parent.mkdir(parents=True, exist_ok=True)
    DDL_PATH.write_text(
        json.dumps({"ddl": render_ddl(Base.metadata)}, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    ENUMS_PATH.write_text(render_enums(Base.metadata), encoding="utf-8", newline="\n")
    print(f"Schema gerado em {DDL_PATH} e {ENUMS_PATH}")


if __name__ == "__main__":
    main()
