"""
Receitas de estado: cada uma leva o app até uma tela ou estado que o canvas desenha.

O palco da skill de canvas carrega este arquivo: `app()` sobe o app e devolve a URL, e
`STATES` liga o nome do estado à função que leva a página até ele. A mesma receita serve
para trazer a tela ao canvas e para conferir a tela implementada contra o board.

O app é o da demonstração (`scripts/demo/`): o front buildado do código atual, sobre uma
cópia descartável do banco-base, semeado com as cotações fixas da demo. Toda rodada
parte do mesmo dado.
"""

import os
import re
from collections.abc import Callable, Generator
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page, Playwright, expect, sync_playwright

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
def app() -> Generator[str]:
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
            print(
                f"aviso: o indicador {series} não veio da fonte; o banco segue sem ele"
            )
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


def saved_match() -> tuple[str, str]:
    """
    O nickname e o nome da simulação salva que as receitas do Mapa abrem, lidos de
    `CANVAS_NICKNAME` e `CANVAS_SAVE_NAME`. A salva vive num banco de teste (app de pé com
    `--base-url`) com o governo ligado e eleições passadas.
    """
    nickname = os.environ.get("CANVAS_NICKNAME")
    save_name = os.environ.get("CANVAS_SAVE_NAME")
    if not nickname or not save_name:
        raise RuntimeError(
            "As receitas do Mapa pedem CANVAS_NICKNAME e CANVAS_SAVE_NAME: o nickname com conta "
            "e a simulação salva (governo ligado, eleições passadas) do banco de teste."
        )
    return nickname, save_name


def open_saved_match(page: Page, nickname: str, simulation_name: str) -> None:
    """
    Entra com um nickname que já tem conta e continua a simulação salva pelo nome: se ela já
    é a selecionada, o lobby oferece "Continuar" com o nome dela; senão ela é escolhida na
    lista de simulações salvas.
    """
    page.goto("/login")
    page.get_by_label("Seu nickname").fill(nickname)
    page.get_by_role("button", name="Entrar").click()
    # Nickname com conta pede a confirmação; o login leva ao lobby, ou à partida se já há uma ativa
    returning = page.get_by_role("button", name="Sou eu, entrar")
    lobby = page.get_by_role(
        "button", name=re.compile(r"^(Continuar|Escolher partida salva|Trocar partida)")
    )
    returning.or_(lobby).first.wait_for()
    if returning.is_visible():
        returning.click()
    page.wait_for_url(re.compile(r"/(lobby)?$"))
    # Com partida ativa o lobby fica fechado: a partida ativa é encerrada pela API ("Parar simulação"),
    # a não ser que seja esta mesma, que já está aberta
    if urlparse(page.url).path != "/lobby":
        status = page.request.get(urljoin(page.url, "/api/simulation/status")).json()
        active_name = (status.get("simulation") or {}).get("name")
        if active_name == simulation_name:
            page.get_by_role("heading", name="Carteira").wait_for()
            return
        stopped = page.request.post(urljoin(page.url, "/api/simulation/stop"))
        if not stopped.ok:
            raise RuntimeError(f"A partida ativa não parou: HTTP {stopped.status}")
        page.goto("/lobby")
    lobby.first.wait_for()
    continue_button = page.get_by_role(
        "button", name=f"Continuar {simulation_name}", exact=True
    )
    if not continue_button.is_visible():
        page.get_by_role(
            "button", name=re.compile(r"^(Escolher partida salva|Trocar partida)")
        ).first.click()
        dialog = page.get_by_role("dialog")
        # A linha da salva é o elemento mais fundo que contém o nome e o botão "Selecionar".
        # Dentro de `has=` o localizador é relativo à linha: parte de `page`, não do diálogo.
        row = (
            dialog.locator("div")
            .filter(has=page.get_by_text(simulation_name, exact=True))
            .filter(has=page.get_by_role("button", name="Selecionar", exact=True))
            .last
        )
        row.get_by_role("button", name="Selecionar", exact=True).click()
        continue_button.wait_for()
    continue_button.click()
    page.get_by_role("heading", name="Carteira").wait_for()


def map_default(page: Page) -> None:
    """Mapa do Brasil, divisão por estado e tabela recolhida, na salva de `saved_match()`."""
    open_saved_match(page, *saved_match())
    sidebar(page, "Mapa").click()
    page.get_by_role("heading", name="Mapa do Brasil").wait_for()
    page.get_by_text("Estados, do maior para o menor").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def map_states_expanded(page: Page) -> None:
    """Mapa com a tabela "Estados, do maior para o menor" expandida ("Ver os 27" aberto), na salva de `saved_match()`."""
    map_default(page)
    page.get_by_role("button", name="Ver os 27", exact=True).click()
    page.get_by_role("button", name="Ver menos", exact=True).wait_for()


def map_first_poll(page: Page) -> None:
    """Mapa na primeira pesquisa da campanha: a lente de variação fica indisponível e o aviso das lentes diz o motivo."""
    map_default(page)
    page.get_by_role("button", name=re.compile(r"^Pesquisa de ")).first.click()
    page.get_by_text("Indisponíveis agora").wait_for()


def map_by_region(page: Page) -> None:
    """Mapa dividido por região: a tabela lista as 5 regiões, sem a coluna Região e sem o botão de expandir."""
    map_default(page)
    page.get_by_role("button", name="Região", exact=True).click()
    page.get_by_text("Regiões, do maior para o menor").wait_for()
    page.wait_for_load_state("networkidle")


def map_error(page: Page) -> None:
    """Mapa quando a consulta `/api/government/map` falha: dado forjado, a API responde 500."""
    open_saved_match(page, *saved_match())
    page.route(
        "**/api/government/map", lambda route: route.fulfill(status=500, body="{}")
    )
    sidebar(page, "Mapa").click()
    page.get_by_text("Não foi possível carregar o mapa").wait_for(timeout=60_000)
    dismiss_topic(page)


PROFESSION_NAMES = re.compile(
    r"^(CLT|Servidor|Empreendedor|Aposentado|Auxílio|Locador)\b"
)


def lobby_with_professions(page: Page) -> None:
    """
    Lobby sem partida ativa, com as profissões ligadas: viver de renda, modo de profissões e
    salário de 5000 do host. As regras vão pela API das settings, a mesma que o formulário chama.
    """
    page.goto("/login")
    page.get_by_label("Seu nickname").fill(demo_settings()["host"]["nickname"])
    page.get_by_role("button", name="Entrar").click()
    # Conta do host já existente pede a confirmação; se há partida ativa, o login leva à Carteira
    returning = page.get_by_role("button", name="Sou eu, entrar")
    lobby = page.get_by_role(
        "button",
        name=re.compile(
            r"^(Iniciar nova simulação|Continuar|Escolher partida salva|Trocar partida)"
        ),
    )
    portfolio = page.get_by_role("heading", name="Carteira")
    returning.or_(lobby).or_(portfolio).first.wait_for()
    if returning.is_visible():
        returning.click()
    page.wait_for_url(re.compile(r"/(lobby)?$"))
    # Partida ativa tiraria o lobby: ela é encerrada pela API, como em open_saved_match
    status = page.request.get(urljoin(page.url, "/api/simulation/status")).json()
    if status.get("simulation"):
        stopped = page.request.post(urljoin(page.url, "/api/simulation/stop"))
        if not stopped.ok:
            raise RuntimeError(f"A partida ativa não parou: HTTP {stopped.status}")
    settings = page.request.get(urljoin(page.url, "/api/simulation/settings")).json()
    if settings["selected_simulation_id"] is not None:
        raise RuntimeError(
            "Há uma partida salva selecionada: as regras dela não mudam pela API."
        )
    body = settings["simulation"] | {
        "game_type": "FINANCIAL_INDEPENDENCE",
        "salary_mode": "PROFESSIONS",
        "monthly_salary": "5000",
    }
    saved = page.request.put(urljoin(page.url, "/api/simulation/settings"), data=body)
    if not saved.ok:
        raise RuntimeError(
            f"As regras não ligaram as profissões: HTTP {saved.status} {saved.text()[:300]}"
        )
    page.goto("/lobby")
    page.get_by_role("button", name="Minha preparação").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def preparation_profession(page: Page) -> None:
    """Lobby com as profissões ligadas e o diálogo "Minha preparação" na aba Profissão, com os 6 cartões."""
    lobby_with_professions(page)
    page.get_by_role("button", name="Minha preparação").click()
    dialog = page.get_by_role("dialog")
    expect(dialog.get_by_role("button", name=PROFESSION_NAMES)).to_have_count(6)
    page.wait_for_load_state("networkidle")


def preparation_profession_selected(page: Page) -> None:
    """Como preparacao/profissao, com o cartão Empreendedor escolhido e gravado: marcado, e o rodapé diz "Salvo automaticamente"."""
    preparation_profession(page)
    dialog = page.get_by_role("dialog")
    entrepreneur = dialog.get_by_role("button", name=re.compile(r"^Empreendedor"))
    with page.expect_response(
        lambda response: (
            response.request.method == "PUT"
            and "/players/me/profession" in response.url
        )
    ):
        entrepreneur.click()
    expect(entrepreneur).to_have_attribute("aria-pressed", "true")
    dialog.get_by_text("Salvo automaticamente").wait_for()
    page.wait_for_load_state("networkidle")


STATES: dict[str, Callable[[Page], None]] = {
    "carteira/vazia": portfolio_empty,
    "renda-variavel/detalhe": stock_detail,
    "renda-variavel/lista": stocks_list,
    "mapa/padrao": map_default,
    "mapa/estados-expandido": map_states_expanded,
    "mapa/primeira-pesquisa": map_first_poll,
    "mapa/regiao": map_by_region,
    "mapa/erro": map_error,
    "preparacao/profissao": preparation_profession,
    "preparacao/profissao-escolhida": preparation_profession_selected,
}
