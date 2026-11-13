"""
Receitas de estado: cada uma leva o app até uma tela ou estado que o canvas desenha.

O palco da skill de canvas carrega este arquivo: `app()` sobe o app e devolve a URL, e
`STATES` liga o nome do estado à função que leva a página até ele. A mesma receita serve
para trazer a tela ao canvas e para conferir a tela implementada contra o board.

O app é o da demonstração (`scripts/demo/`): o front buildado do código atual, sobre uma
cópia descartável do banco-base, semeado com as cotações fixas da demo. Toda rodada
parte do mesmo dado.
"""

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from playwright.sync_api import Page, Playwright, sync_playwright

from backend.core.utils import PROJECT_ROOT
from scripts.demo.__main__ import import_stocks, missing_indicators
from scripts.demo.script import sidebar
from scripts.demo.server import (
    base_database_url,
    build_frontend,
    demo_server,
    demo_settings,
    recording_database,
)

WORK_DIR = PROJECT_ROOT / "build" / "canvas"
# O conteúdo da página, dentro da casca (menu e topbar): é o que o port copia para o canvas
CONTENT = "main main"


@contextmanager
def app() -> Iterator[str]:
    build_frontend()
    # O banco-base recebe as cotações antes da cópia: o backend o cria na primeira subida
    with (
        demo_server(WORK_DIR, base_database_url()) as app_url,
        sync_playwright() as playwright,
    ):
        seed_base(playwright, app_url)
    with (
        recording_database() as database_url,
        demo_server(WORK_DIR, database_url) as app_url,
    ):
        yield app_url


def seed_base(playwright: Playwright, base_url: str) -> None:
    """
    As cotações vêm dos CSVs da demo. Cada indicador que falta é pedido à fonte uma vez
    por rodada; o que a fonte não entrega sai nomeado, e o estado que depende dele mostra
    a falta na tela.
    """
    api = playwright.request.new_context(base_url=base_url)
    import_stocks(api)
    for series in missing_indicators(api):
        response = api.post(f"/api/import-assets/indicators/{series}", timeout=180_000)
        if not response.ok:
            print(f"aviso: o indicador {series} não veio da fonte; o banco segue sem ele")
    api.dispose()


def start_match(page: Page) -> None:
    """Entra com o nickname do host até a Carteira da simulação: a nova, ou a que já está aberta."""
    page.goto("/login")
    page.get_by_label("Seu nickname").fill(demo_settings()["host"]["nickname"])
    page.get_by_role("button", name="Entrar").click()
    # Com o app mantido de pé entre rodadas, a conta do host já existe: o login pede a
    # confirmação e leva direto à simulação aberta
    returning = page.get_by_role("button", name="Sou eu, entrar")
    new_match = page.get_by_role("button", name="Iniciar nova simulação")
    portfolio = page.get_by_role("heading", name="Carteira")
    returning.or_(new_match).first.wait_for()
    if returning.is_visible():
        returning.click()
    new_match.or_(portfolio).first.wait_for()
    if new_match.is_visible():
        new_match.click()
    portfolio.wait_for()


def dismiss_topic(page: Page) -> None:
    """O cartão "Tópico sobre esta tela" abre na primeira visita e flutua sobre o conteúdo: a tela é retratada sem ele."""
    later = page.get_by_role("button", name="Agora não")
    if later.is_visible():
        later.click()
        later.wait_for(state="hidden")


def stocks_list(page: Page) -> None:
    """Renda variável: a lista de ações da simulação."""
    start_match(page)
    sidebar(page, "Renda variável").click()
    page.get_by_role("row", name=re.compile(r"^PETR4")).wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def portfolio_empty(page: Page) -> None:
    """Carteira sem posição nenhuma: tudo em caixa."""
    start_match(page)
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def stock_detail(page: Page) -> None:
    """Detalhe de uma ação (PETR4), com o gráfico de preço."""
    stocks_list(page)
    page.get_by_role("row", name=re.compile(r"^PETR4")).click()
    page.get_by_role("heading", name=re.compile("PETR4")).first.wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


STATES: dict[str, Callable[[Page], None]] = {
    "carteira/vazia": portfolio_empty,
    "renda-variavel/detalhe": stock_detail,
    "renda-variavel/lista": stocks_list,
}
