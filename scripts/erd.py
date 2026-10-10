"""Gera a página de docs com o diagrama do banco a partir dos models.

Uso: `pnpm db:erd`. O `tests/test_erd.py` compara a página com o que este
script geraria, então ela acompanha cada mudança de model.
"""

from pathlib import Path

from sqlalchemy import (
    Column,
    Enum,
    ForeignKeyConstraint,
    MetaData,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql

from backend.core.models.models import Base

PAGE_PATH = Path("docs/docs/desenvolvimento/diagrama-banco-dados.md")

HEADER = """---
sidebar_position: 5
---

# Diagrama do Banco de Dados

O schema atual do banco, com cada tabela, suas colunas e as relações entre elas. Para a forma de alterar o schema, veja o [Ciclo de Desenvolvimento com Banco de Dados](./ciclo-banco-dados.md).

:::info Página gerada
Esta página é gerada a partir de `backend/core/models/models.py` por `pnpm db:erd`. O `tests/test_erd.py` falha enquanto ela estiver diferente dos models.
:::

**Como ler:** `PK` é chave primária, `FK` é chave estrangeira e `UK` é valor único. Uma linha liga a tabela referenciada (lado `||`, exatamente um) à que guarda a chave estrangeira (lado `o{`, zero ou mais), e o rótulo é a coluna da chave. Uma coluna marcada `nullable` aceita nulo. Coluna de `ENUM` tem como tipo o nome do `ENUM`, e os valores aceitos estão em [Valores dos ENUM](#valores-dos-enum). Uma tabela que aparece só com o nome está detalhada na outra seção.

"""

# Uma seção por domínio mantém cada diagrama estreito o bastante para ser lido.
# Tabela fora destas listas cai em "Outras tabelas" até ganhar uma seção.
SECTIONS: list[tuple[str, str, set[str]]] = [
    (
        "Partidas e jogadores",
        "Cada partida, quem joga nela, e os eventos e snapshots que reconstroem "
        "a carteira de cada jogador.",
        {
            "simulations",
            "users",
            "event_cashflow",
            "event_equity",
            "event_fixed_income",
            "snapshots",
        },
    ),
    (
        "Ativos e indicadores",
        "Os ativos negociáveis, o histórico de preços e os indicadores econômicos.",
        {
            "stock",
            "stock_price_history",
            "fixed_income_asset",
            "ipca_history",
            "selic_history",
        },
    ),
]


# Nomes do Postgres com espaço viram um token só, que é o que o Mermaid aceita
SHORT_TYPES = {
    "timestamp with time zone": "timestamptz",
    "double precision": "double",
}


def _column_type(column: Column) -> str:
    if isinstance(column.type, Enum) and column.type.name:
        return column.type.name
    compiled = column.type.compile(dialect=postgresql.dialect())
    name = compiled.split("(")[0].strip().lower()
    return SHORT_TYPES.get(name, name)


def _column_keys(table: Table, column: Column) -> str:
    keys: list[str] = []
    if column.primary_key:
        keys.append("PK")
    if column.foreign_keys:
        keys.append("FK")
    unique = any(
        constraint.columns.keys() == [column.name]
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    )
    if unique:
        keys.append("UK")
    return ", ".join(keys)


def _column_comment(column: Column) -> str:
    return "nullable" if column.nullable and not column.primary_key else ""


def _render_table(table: Table) -> list[str]:
    lines = [f"    {table.name} {{"]
    for column in table.columns:
        parts = [_column_type(column), column.name]
        keys = _column_keys(table, column)
        if keys:
            parts.append(keys)
        comment = _column_comment(column)
        if comment:
            parts.append(f'"{comment}"')
        lines.append("        " + " ".join(parts))
    lines.append("    }")
    return lines


def _render_relationship(table: Table, constraint: ForeignKeyConstraint) -> str:
    parent = constraint.referred_table.name
    optional = any(column.nullable for column in constraint.columns)
    parent_side = "|o" if optional else "||"
    label = ", ".join(column.name for column in constraint.columns)
    return f"    {parent} {parent_side}--o{{ {table.name} : {label}"


def render_diagram(tables: list[Table]) -> str:
    tables = sorted(tables, key=lambda table: table.name)
    # Da esquerda para a direita, as tabelas que guardam a chave estrangeira se
    # empilham em vez de se enfileirar, e o diagrama cabe na largura da página
    lines = ["erDiagram", "    direction LR"]
    for table in tables:
        lines.extend(_render_table(table))
    for table in tables:
        constraints = sorted(
            (c for c in table.constraints if isinstance(c, ForeignKeyConstraint)),
            key=lambda c: c.referred_table.name,
        )
        lines.extend(_render_relationship(table, c) for c in constraints)
    return "\n".join(lines)


def _sections(metadata: MetaData) -> list[tuple[str, str, list[Table]]]:
    tables = list(metadata.tables.values())
    sections = [
        (title, description, [table for table in tables if table.name in names])
        for title, description, names in SECTIONS
    ]
    listed = set().union(*(names for _, _, names in SECTIONS))
    others = [table for table in tables if table.name not in listed]
    if others:
        sections.append(("Outras tabelas", "Tabelas ainda sem seção.", others))
    return sections


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
    header = [
        "## Valores dos ENUM",
        "",
        "| ENUM | Valores | Colunas |",
        "| --- | --- | --- |",
    ]
    return "\n".join([*header, *rows, ""])


def render_page() -> str:
    blocks = [
        f"## {title}\n\n{description}\n\n```mermaid\n{render_diagram(tables)}\n```\n"
        for title, description, tables in _sections(Base.metadata)
    ]
    return HEADER + "\n".join([*blocks, render_enums(Base.metadata)])


def main() -> None:
    PAGE_PATH.write_text(render_page(), encoding="utf-8", newline="\n")
    print(f"Diagrama gerado em {PAGE_PATH}")


if __name__ == "__main__":
    main()
