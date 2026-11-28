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
- Aviso do websocket carrega o dado novo, e o front o aplica no cache com `setQueryData` (moldes: `frontend/features/variable-income/hooks/queries/useVariableIncomeStock.ts` e `frontend/shared/hooks/queries/usePortfolio.ts`). O servidor sabe quem assina cada aviso e entrega pronto o que a tela mostra, inclusive o que ele calcula a partir de outro dado (prévia da ordem, indicadores, padrões de vela). A query HTTP busca na abertura da tela e quando a conexão volta; entre uma e outra, a tela vive do que os avisos entregam. Isso vale para o dado em tempo real: o que muda a cada pregão ou pela ação de outro jogador com a tela aberta. O resto é HTTP: a tela busca ao abrir, o botão relê o que ele mesmo mudou, e um aviso raro (mensal, de conquista, da sala e do lobby) pode pedir a releitura.
- Texto de tela fala do que o jogador decide e do que acontece com ele: o resultado, o custo, o prazo e a ação. Como o motor chega ao resultado (fórmula, quem decide em que pregão, prêmio, faixa interna, curva de parâmetro) mora no Como jogar e, quando ajuda na decisão, numa dica ⓘ. A pergunta "por que não aconteceu?" se responde com a causa numa frase ("a gestora rendeu igual ao CDI e a cota não tem ágio"), não com o regulamento.
- Componente montado em toda página (topo, barra lateral, faixa, diálogo global) assina só um resumo leve feito para ele; o painel inteiro fica com a tela que o mostra.

## Antes de commitar

- Rode `pnpm format` e `pnpm lint:fix`, e depois `pnpm run check` na raiz (ruff, deptry, pyright, pytest, oxlint, oxfmt, tsc, knip e vitest).
- O check roda três trilhas em paralelo e fecha com o tempo de cada uma: `check:back` (lints e pyright), `test` (pytest) e `check:front` (lints, tsc, knip e vitest). Depois de uma falha, a correção roda de novo só a trilha que falhou; as que passaram continuam valendo, a menos que a correção mexa no código delas.
- Mudou rota ou DTO do backend: rode `pnpm openapi` (regenera `docs/openapi.json` e os tipos do front); o `tests/test_openapi.py` falha se estiver defasado.
- Mudou os models: `pnpm db:revision` (veja `docs/docs/desenvolvimento/ciclo-banco-dados.md`).

## Roadmap

- `ROADMAP.md` e `DECISIONS_ARCHIVE.md` são gerados: nunca edite à mão. Use o `roadmap.py` da skill `feature-roadmap` (`complete`, `insert`, `archive`, `check`). `DECISIONS.md` é prosa livre.
- Concluir uma feature: commit `feat:` com o código e, separado, `docs: Concluído <o que foi feito> no roadmap`, pelo nome da feature e sem o ID.

## Ambiente de teste

- Os testes com banco precisam de `POSTGRES_DATABASE_URL`; sem ela são pulados. O cluster precisa ser UTF-8 (`initdb -E UTF8`), senão o psycopg devolve `bytes`.
