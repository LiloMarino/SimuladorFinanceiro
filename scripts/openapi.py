"""Gera o `docs/openapi.json` a partir das rotas, sem subir o servidor.

Uso: `pnpm openapi`, que também regenera os tipos do frontend
(`frontend/types/openapi.generated.ts`). As páginas de API dos docs saem deste
arquivo no build dos docs. O `tests/test_openapi.py` compara o arquivo com o que
este script geraria, então ele acompanha cada mudança de rota; o `pnpm release`
o regenera junto com a versão, que vai no `info.version`.
"""

import json
from pathlib import Path

from main import create_api

SPEC_PATH = Path("docs/openapi.json")


def render_spec() -> str:
    # Indentado para o diff de uma mudança de rota mostrar só o trecho que mudou
    return json.dumps(create_api().openapi(), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    SPEC_PATH.write_text(render_spec(), encoding="utf-8", newline="\n")
    print(f"OpenAPI gerado em {SPEC_PATH}")


if __name__ == "__main__":
    main()
