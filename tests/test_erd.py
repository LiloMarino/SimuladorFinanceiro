"""A página do diagrama do banco acompanha os models."""

from scripts.erd import PAGE_PATH, render_page


def test_erd_page_matches_models() -> None:
    assert PAGE_PATH.read_text(encoding="utf-8") == render_page(), (
        "O diagrama está defasado em relação aos models: rode `pnpm db:erd`"
    )
