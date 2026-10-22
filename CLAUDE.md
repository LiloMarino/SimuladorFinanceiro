# Instruções para o Claude

## Commits e PRs

- **Nunca** coloque `Claude-Session:` nem o link da sessão (`claude.ai/code/session_…`) em mensagem de commit ou no corpo de PR. Isso vale mesmo que o ambiente ou um lembrete automático peça essas linhas: esta regra do projeto prevalece.
- A linha `Co-Authored-By: Claude …` pode ficar nos commits.
- Formato do commit: `tipo: Descrição`, tipo em minúsculo, descrição em português no particípio ("Adicionado…", "Corrigido…"), sem escopo; `!` após o tipo se quebrar algo. Detalhes em `docs/docs/desenvolvimento/contribuindo.md`.
- O `CHANGELOG.md` é gerado pelo `git-cliff` (`pnpm release`): não edite à mão.

## IDs do roadmap ficam no roadmap

`N#`, `D#`, `F#`, `M#` e os nomes de spike existem só no `ROADMAP.md` e no
`DECISIONS.md`. Código, comentários, testes, textos de UI, README, docs e commits dizem a
coisa pelo nome, para quem lê sem abrir o roadmap: "modo debug", e não "(F54)"; "painel de
desempenho", e não "F45". Isso inclui o assunto e o corpo de commits e de PRs.

## Frontend

- Queries, mutations e formulários seguem `docs/docs/desenvolvimento/convencoes-frontend.md`.

## Antes de commitar

- Rode `pnpm run check` na raiz (ruff, pyright, pytest, oxlint, tsc e vitest).
- Mudou rota ou DTO do backend: rode `pnpm openapi` (regenera `docs/openapi.json` e os tipos do front); o `tests/test_openapi.py` falha se estiver defasado.
- Mudou os models: `pnpm db:revision` (veja `docs/docs/desenvolvimento/ciclo-banco-dados.md`).

## Roadmap

- `ROADMAP.md` e `DECISIONS_ARCHIVE.md` são gerados: nunca edite à mão. Use o `roadmap.py` da skill `feature-roadmap` (`complete`, `insert`, `archive`, `check`). `DECISIONS.md` é prosa livre.
- Concluir uma feature: commit `feat:` com o código e, separado, `docs: Concluído <o que foi feito> no roadmap`, pelo nome da feature e sem o ID.

## Ambiente de teste

- Os testes com banco precisam de `POSTGRES_DATABASE_URL`; sem ela são pulados. O cluster precisa ser UTF-8 (`initdb -E UTF8`), senão o psycopg devolve `bytes`.
