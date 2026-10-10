"""Gera o `docs/openapi.json` a partir das rotas, sem subir o servidor.

Uso: `pnpm openapi`, que também regenera as páginas de API dos docs e os tipos
do frontend (`frontend/types/openapi.generated.ts`), ambos lidos deste arquivo. O
`tests/test_openapi.py` compara o arquivo com o que este script geraria, então
ele acompanha cada mudança de rota.
"""

import json
from pathlib import Path

from main import create_api

SPEC_PATH = Path("docs/openapi.json")


def render_spec() -> str:
    # Mesmo formato que o FastAPI serve em /openapi.json
    return json.dumps(create_api().openapi(), ensure_ascii=False, separators=(",", ":"))


def main() -> None:
    SPEC_PATH.write_text(render_spec(), encoding="utf-8", newline="\n")
    print(f"OpenAPI gerado em {SPEC_PATH}")


if __name__ == "__main__":
    main()
