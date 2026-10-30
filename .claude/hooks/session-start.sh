#!/bin/bash
# Prepara a sessão na nuvem: dependências, Postgres UTF-8 local e banco migrado.
# Sem isso os testes com banco são pulados e o app não sobe.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

PG_PORT=5433
PG_DATA=/var/lib/simfin-pg
PG_LOG=/var/log/simfin-pg.log
DB_NAME=simulador_financeiro
DB_URL="postgresql+psycopg://postgres@127.0.0.1:${PG_PORT}/${DB_NAME}"

# O Postgres recusa rodar como root: usa o usuário `postgres` do pacote
as_postgres() {
  if [ "$(id -u)" -eq 0 ]; then
    runuser -u postgres -- "$@"
  else
    "$@"
  fi
}

pg_bin() {
  ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -n 1
}

if [ -z "$(pg_bin)" ]; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql
  # O pacote cria e sobe um cluster próprio na 5432; o desta sessão é outro
  systemctl stop postgresql 2>/dev/null || true
fi
PG_BIN="$(pg_bin)"

if [ ! -f "$PG_DATA/PG_VERSION" ]; then
  install -d -o postgres -g postgres "$PG_DATA"
  as_postgres "$PG_BIN/initdb" -D "$PG_DATA" -E UTF8 --locale=C.UTF-8 \
    --username=postgres --auth=trust >/dev/null
fi

if ! as_postgres "$PG_BIN/pg_ctl" -D "$PG_DATA" status >/dev/null 2>&1; then
  touch "$PG_LOG"
  chown postgres:postgres "$PG_LOG"
  as_postgres "$PG_BIN/pg_ctl" -D "$PG_DATA" -l "$PG_LOG" -w \
    -o "-p $PG_PORT -c listen_addresses=127.0.0.1" start >/dev/null
fi

uv sync --dev
pnpm install
(cd frontend && pnpm install)

# Cria o banco vazio e leva ao head das migrations
POSTGRES_DATABASE_URL="$DB_URL" uv run python -c \
  "from backend.core.migration import migrate; migrate('$DB_URL')"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export POSTGRES_DATABASE_URL='$DB_URL'" >> "$CLAUDE_ENV_FILE"
fi
