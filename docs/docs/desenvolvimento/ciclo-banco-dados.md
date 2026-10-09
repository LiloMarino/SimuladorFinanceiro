---
sidebar_position: 4
---

# Ciclo de Desenvolvimento com Banco de Dados


O ciclo de desenvolvimento do projeto é feito **exclusivamente com PostgreSQL**.

Durante o desenvolvimento, **o PostgreSQL é tratado como o banco canônico**.

---

## Configuração do Banco de Dados (PostgreSQL)

1. **Instalar PostgreSQL:**

   * Windows: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
   * Linux: `sudo apt install postgresql`
   * macOS: `brew install postgresql`

2. **Configurar `.env`:**

   ```env
   POSTGRES_DATABASE_URL=postgresql+psycopg://postgres:sua_senha@localhost:5432/simulador_financeiro
   ```

3. **Iniciar a aplicação:**

   ```bash
   pnpm backend
   ```

Na inicialização, antes de o servidor subir, o banco é criado se não existir e levado à última migration.

---

## Ciclo de Desenvolvimento

O schema nasce dos models em `backend/core/models/models.py`, e cada mudança vira uma migration do [Alembic](https://alembic.sqlalchemy.org/), guardada em `backend/migrations/versions/`:

1. ✏️ **Alterar o model** em `backend/core/models/models.py`
2. 🧬 **Gerar a migration:**

   ```bash
   pnpm db:revision "add price impact to simulations"
   ```

   O autogenerate compara os models com o banco do `.env` e escreve a revisão. A descrição é em inglês e vira o nome do arquivo.
3. 🔍 **Revisar o arquivo gerado** — ele é um ponto de partida, não o resultado final
4. ✅ **Rodar `pnpm test`** — o `tests/test_migrations.py` confere que as migrations chegam exatamente no schema dos models e que toda revisão desce e sobe de volta

O banco do `.env` precisa estar no head antes de gerar uma revisão nova: subir o app uma vez já garante isso.

### O que o autogenerate não cobre

* **Valor novo num `ENUM` nativo do Postgres** (`cashflow_event_type`, `equity_event_type` etc.) entra à mão na migration:

  ```python
  op.execute("ALTER TYPE cashflow_event_type ADD VALUE 'TAX'")
  ```

* **`ENUM` removido no `downgrade`** sobrevive ao `drop_table` e é dropado explicitamente: `sa.Enum(name="...").drop(op.get_bind())`.
* **Coluna `NOT NULL` nova em tabela com dado** precisa de valor para as linhas existentes: `server_default` na coluna ou um `UPDATE` na própria migration, antes de tornar a coluna obrigatória.
* **Renomear tabela ou coluna** aparece como remoção + criação; troque por `op.rename_table` / `op.alter_column(..., new_column_name=...)` para não perder o dado.

---

## Como a Migration Roda na Inicialização

`backend/core/migration.py` decide pelo estado do banco:

| Estado do banco | O que acontece |
| --- | --- |
| Vazio | Recebe todas as migrations até o head |
| Já no head | Nada |
| Com tabelas, sem `alembic_version`, igual aos models | É marcado no head (`stamp`) |
| Com tabelas, sem `alembic_version`, diferente dos models | A inicialização é recusada: o banco é anterior às migrations e precisa ser trocado por um novo |
| Numa revisão anterior | Ensaio numa cópia, backup, e então upgrade |

**Ensaio:** as migrations rodam primeiro numa cópia (`<banco>_dryrun`), e o upgrade só é aplicado no banco real se nenhuma tabela perder linha nem célula preenchida. A cópia é apagada no fim.

**Backup:** antes do upgrade, o banco como estava é copiado para `<banco>_bkp_AAAAMMDD_HHMMSS`; ficam os 3 mais recentes.

As duas cópias usam `CREATE DATABASE ... TEMPLATE`, que exige o banco sem outras conexões abertas: com pgAdmin ou DBeaver conectados, a migration é recusada até que eles sejam fechados. O DDL do Postgres é transacional, então uma migration que falha no meio é desfeita inteira.

---

## Dicas e Boas Práticas

### Evite SQL Raw

Sempre que possível, use o ORM do SQLAlchemy.

**Evite:**

```python
session.execute("SELECT * FROM users WHERE id = 1")
```

**Prefira:**

```python
session.get(User, 1)
```

ou, em consultas mais complexas:

```python
stmt = select(User).where(User.id == 1)
session.execute(stmt).scalar_one_or_none()
```

---

## Próximos Passos

* [Diretrizes Async vs Sync](./async-vs-sync.md)
* [Estrutura de Pastas](./estrutura-pastas.md)

