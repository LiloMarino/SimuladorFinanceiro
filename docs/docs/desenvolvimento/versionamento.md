---
sidebar_position: 8
---

# Versionamento

O projeto segue o [SemVer](https://semver.org/lang/pt-BR/): `MAIOR.MENOR.CORREÇÃO`, como em `2.1.3`. O número responde a uma pergunta sobre quem já tem o app instalado: **atualizar vai quebrar alguma coisa?**

O número diz compatibilidade, não maturidade: nada na release diz que o jogo está em fase de testes.

## Quando sobe cada número

| Sobe | Quando | Exemplo |
| --- | --- | --- |
| **Correção** (2.0.1) | corrige bug, sem feature nova | uma tela que errava um número |
| **Menor** (2.1.0) | feature nova e nada quebra: as partidas salvas abrem e o `config.toml` antigo funciona | bots, modo Especialista, indicadores técnicos |
| **Maior** (3.0.0) | algo deixa de funcionar para quem atualiza: partida salva que não abre, chave do `config.toml` removida ou renomeada, troca de banco sem migrar os dados | trocar o Postgres pelo SQLite sem importar os dados |

Migration que acrescenta tabela ou coluna não é maior, porque a aplicação das migrations a faz sozinha nas partidas salvas. Ritmo: um marco concluído vira uma versão menor, correção solta vira correção, e a maior só com quebra de compatibilidade.

## O número sai dos commits

Os commits seguem o [Conventional Commits](https://www.conventionalcommits.org/pt-br/): `tipo: Descrição`, sem escopo. O [git-cliff](https://git-cliff.org/) lê os commits desde a última tag e calcula a próxima versão:

| Commit | Pede |
| --- | --- |
| `fix:`, `docs:`, `refactor:`, `build:`, `test:`, `chore:`, `ci:`, `perf:`, `style:` | correção |
| `feat:` | menor |
| `feat!:`, `fix!:` (um `!` depois do tipo) | maior |
| sem tipo | nada: não move o número |

O `!` é a única marca de quebra de compatibilidade, e quem faz o commit que quebra é quem o coloca. Vale para qualquer tipo, até `fix!:`.

## Changelog

O `CHANGELOG.md` da raiz é gerado pelo mesmo `git-cliff`, sem edição manual: `feat:` vira "Novidades", `fix:` vira "Correções", e os outros tipos ficam de fora. Cada seção diz se as partidas salvas e o `config.toml` continuam valendo. A seção da versão vira a descrição da release no GitHub e a página [Novidades](../como-usar/novidades.md) destes docs.

## Publicando uma versão

1. `pnpm release` calcula a versão pelos commits, grava no `pyproject.toml` (a fonte única do número) e no `uv.lock`, regenera o `docs/openapi.json` e acrescenta a seção ao `CHANGELOG.md`. Se o `pyproject.toml` já estiver acima do calculado, o número fica como está.
2. Revise o diff e commite como `chore: Versão X.Y.Z`.
3. Dispare o workflow **Release Multi-Plataforma** no GitHub. Ele lê a versão do `pyproject.toml`, confere que não está abaixo da pedida pelos commits, gera os executáveis e cria a tag e a release.
