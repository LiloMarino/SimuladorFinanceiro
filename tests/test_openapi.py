"""O OpenAPI dos docs acompanha as rotas."""

from scripts.openapi import SPEC_PATH, render_spec


def test_openapi_spec_matches_routes() -> None:
    assert SPEC_PATH.read_text(encoding="utf-8") == render_spec(), (
        "O docs/openapi.json está defasado em relação às rotas: rode `pnpm docs:api`"
    )
