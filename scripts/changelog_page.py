"""Gera a página "Novidades" dos docs a partir do `CHANGELOG.md` da raiz.

Roda dentro do `pnpm start` e do `pnpm build` dos docs (`pnpm db:changelog`);
o arquivo gerado não é versionado.
"""

import re
from pathlib import Path

CHANGELOG_PATH = Path("CHANGELOG.md")
PAGE_PATH = Path("docs/docs/como-usar/novidades.md")

PAGE_HEADER = """---
sidebar_position: 10
---

# Novidades

O que mudou em cada versão do Simulador Financeiro, da mais nova para a mais antiga. Cada versão diz se as partidas salvas e o `config.toml` continuam valendo. Como o número é escolhido: [Versionamento](../desenvolvimento/versionamento.md).

"""

CODE_SPAN = re.compile(r"(`[^`]*`)")


def escape_mdx(line: str) -> str:
    """O MDX lê `<` e `{` fora de código como JSX; a mensagem de um commit pode trazê-los."""
    parts = CODE_SPAN.split(line)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(r"([<{])", r"\\\1", parts[index])
    return "".join(parts)


def main() -> None:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    # O cabeçalho do arquivo (título e introdução) dá lugar ao da página
    body = text[text.index("\n## ") + 1 :]
    escaped = "\n".join(escape_mdx(line) for line in body.splitlines())
    PAGE_PATH.write_text(PAGE_HEADER + escaped + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
