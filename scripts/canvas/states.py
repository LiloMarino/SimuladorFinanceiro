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

from playwright.sync_api import Locator, Page, Playwright, expect, sync_playwright

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


def stock_detail_with_order(page: Page) -> None:
    """
    Detalhe da PETR4 com uma compra limitada do jogador 5% abaixo do preço de hoje: a ordem
    fica aberta no livro, longe das ofertas do Mercado, até o pregão seguinte.
    """
    stock_detail(page)
    page.get_by_label("Tipo de ordem").get_by_text("Limitada").click()
    page.locator("#order-size").fill("100")
    hint = page.get_by_text(re.compile(r"Hoje:")).inner_text()
    today = re.search(r"Hoje:\s*R\$\s*([\d.,]+)", hint)
    assert today, f"o preço de hoje não apareceu na boleta: {hint!r}"
    price = float(today.group(1).replace(".", "").replace(",", ".")) * 0.95
    page.locator("#order-limit").fill(f"{price:.2f}".replace(".", ","))
    page.get_by_role("button", name=re.compile(r"^Comprar 100 PETR4 a")).click()
    page.get_by_role("row", name=re.compile(r"\(você\)")).wait_for()
    page.wait_for_load_state("networkidle")


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
    select_saved_match(page, simulation_name).click()
    page.get_by_role("heading", name="Carteira").wait_for()


def select_saved_match(page: Page, simulation_name: str) -> Locator:
    """
    No lobby sem partida ativa, deixa a simulação salva pelo nome selecionada e devolve o botão
    "Continuar" dela, sem clicar: se ela já é a selecionada, nada muda; senão ela é escolhida na
    lista de simulações salvas.
    """
    lobby = page.get_by_role(
        "button", name=re.compile(r"^(Continuar|Escolher partida salva|Trocar partida)")
    )
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
    return continue_button


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


# O menos das tabelas é o tipográfico (U+2212), não o hífen
MINUS = chr(0x2212)

PROFESSION_NAMES = re.compile(
    r"^(CLT|Servidor|Empreendedor|Aposentado|Auxílio|Locador|Exportador|Bancário"
    r"|Autônomo|Corretor|Herdeiro|Recém-formado)\b"
)
# As profissões da sala: o Autônomo só existe com a renda corrigida pela inflação
PROFESSION_COUNT = 12


def lobby_with_professions(page: Page, *, rules: dict | None = None) -> None:
    """
    Lobby sem partida ativa, com as profissões ligadas: viver de renda, modo de profissões e
    salário de 5000 do host. As regras vão pela API das settings, a mesma que o formulário chama.
    `rules` sobrescreve campos da sala por cima disso (ex.: governo desligado).
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
    body = (
        settings["simulation"]
        | {
            "game_type": "FINANCIAL_INDEPENDENCE",
            "salary_mode": "PROFESSIONS",
            "monthly_salary": "5000",
        }
        | (rules or {})
    )
    saved = page.request.put(urljoin(page.url, "/api/simulation/settings"), data=body)
    if not saved.ok:
        raise RuntimeError(
            f"As regras não ligaram as profissões: HTTP {saved.status} {saved.text()[:300]}"
        )
    page.goto("/lobby")
    page.get_by_role("button", name="Minha preparação").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def profession_card(dialog: Locator, name: str) -> Locator:
    """O cartão de uma profissão: o pai do radio, que também contém as etiquetas "Afetado por"."""
    return dialog.get_by_role("radio", name=re.compile(rf"^{name}")).locator("xpath=..")


def preparation_profession_with(page: Page, rules: dict | None) -> None:
    """Como preparation_profession, com as regras de `rules` aplicadas à sala."""
    lobby_with_professions(page, rules=rules)
    page.get_by_role("button", name="Minha preparação").click()
    dialog = page.get_by_role("dialog")
    settings = page.request.get(urljoin(page.url, "/api/simulation/settings")).json()
    count = PROFESSION_COUNT - (not settings["simulation"]["inflation_adjusted"])
    expect(dialog.get_by_role("radio", name=PROFESSION_NAMES)).to_have_count(count)
    page.wait_for_load_state("networkidle")


def preparation_profession(page: Page) -> None:
    """Lobby com as profissões ligadas e o diálogo "Minha preparação" na aba Profissão, com os 12 cartões."""
    preparation_profession_with(page, None)


def preparation_profession_selected(page: Page) -> None:
    """Como preparacao/profissao, com o cartão Empreendedor escolhido e gravado: marcado, e o rodapé diz "Salvo automaticamente"."""
    preparation_profession(page)
    dialog = page.get_by_role("dialog")
    entrepreneur = dialog.get_by_role("radio", name=re.compile(r"^Empreendedor"))
    with page.expect_response(
        lambda response: (
            response.request.method == "PUT"
            and "/players/me/profession" in response.url
        )
    ):
        entrepreneur.click()
    expect(entrepreneur).to_have_attribute("aria-checked", "true")
    dialog.get_by_text("Salvo automaticamente").wait_for()
    page.wait_for_load_state("networkidle")


def preparation_profession_tag_open(page: Page) -> None:
    """Como preparacao/profissao, com o hovercard da etiqueta "PIB" do cartão Empreendedor aberto por foco de teclado: a tabela de renda por crescimento."""
    preparation_profession(page)
    dialog = page.get_by_role("dialog")
    profession_card(dialog, "Empreendedor").get_by_role(
        "button", name="PIB", exact=True
    ).focus()
    # O foco programático não abre o cartão: é preciso uma tecla de navegação (Shift+Tab, Tab)
    # para o foco ser de teclado. O cartão sai do diálogo: a tabela é procurada na página inteira
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    expect(
        page.get_by_text("O crescimento da economia nos últimos 12 meses")
    ).to_be_visible()
    expect(page.get_by_text(f"{MINUS}15% ou menos", exact=True)).to_be_visible()
    page.wait_for_load_state("networkidle")


def preparation_profession_no_government(page: Page) -> None:
    """Como preparacao/profissao, com o governo desligado nas regras da sala: o cartão Servidor fica sem etiqueta e diz "Nada que mude na partida", e nenhuma etiqueta "IR das pessoas" aparece."""
    preparation_profession_with(page, {"government_enabled": False})
    dialog = page.get_by_role("dialog")
    expect(
        profession_card(dialog, "Servidor").get_by_text("Nada que mude na partida")
    ).to_be_visible()
    expect(
        dialog.get_by_role("button", name="IR das pessoas", exact=True)
    ).to_have_count(0)


def preparation_profession_no_inflation(page: Page) -> None:
    """Como preparacao/profissao, com a inflação fora do reajuste das regras: o Autônomo sai da lista, o cartão CLT perde "Aumento acima da inflação quando o PIB cresce", e a etiqueta "PIB" segue, já que o PIB não depende da inflação."""
    preparation_profession_with(page, {"inflation_adjusted": False})
    dialog = page.get_by_role("dialog")
    expect(
        dialog.get_by_text("Aumento acima da inflação quando o PIB cresce")
    ).to_have_count(0)
    expect(
        profession_card(dialog, "CLT").get_by_role("button", name="PIB", exact=True)
    ).to_have_count(1)
    expect(dialog.get_by_role("radio", name=re.compile("^Autônomo"))).to_have_count(0)


def preparation_profession_saved_match(page: Page) -> None:
    """
    Lobby com a partida salva selecionada e sem partida ativa, e o diálogo "Minha preparação" na
    aba Profissão: como a salva guarda a profissão do jogador, os cartões ficam travados e o
    aviso diz que a profissão fica com a partida salva. A conta vem de `CANVAS_NICKNAME` e a
    salva, que precisa ter profissões ligadas, de `CANVAS_PROFESSION_SAVE_NAME`.
    """
    nickname, _ = saved_match()
    simulation_name = os.environ.get("CANVAS_PROFESSION_SAVE_NAME")
    if not simulation_name:
        raise RuntimeError(
            "A receita pede CANVAS_PROFESSION_SAVE_NAME: a simulação salva com profissões ligadas."
        )
    open_saved_match(page, nickname, simulation_name)
    # O lobby só abre sem partida ativa. Parar a partida também tira a seleção da salva, então
    # o lobby a seleciona de novo, sem continuar: a aba Profissão só lê a salva selecionada
    stopped = page.request.post(urljoin(page.url, "/api/simulation/stop"))
    if not stopped.ok:
        raise RuntimeError(f"A partida salva não parou: HTTP {stopped.status}")
    page.goto("/lobby")
    select_saved_match(page, simulation_name).wait_for()
    dismiss_topic(page)
    page.get_by_role("button", name="Minha preparação").click()
    dialog = page.get_by_role("dialog")
    radios = dialog.get_by_role("radio", name=PROFESSION_NAMES)
    radios.first.wait_for()
    for radio in radios.all():
        expect(radio).to_be_disabled()
    expect(dialog.get_by_text("A profissão fica com a partida salva")).to_be_visible()
    page.wait_for_load_state("networkidle")


def preparation_profession_refused(page: Page) -> None:
    """
    Como preparacao/profissao, com a troca recusada: a resposta de `PUT /players/me/profession`
    é forjada, um 409 com mensagem própria. O alerta "Não deu para trocar a profissão" aparece e
    o cartão clicado volta a não marcado, porque a escolha só vale com a resposta do servidor.
    """
    preparation_profession(page)
    page.route(
        "**/players/me/profession",
        lambda route: route.fulfill(
            status=409,
            content_type="application/json",
            body='{"message": "A profissão não muda agora."}',
        ),
    )
    dialog = page.get_by_role("dialog")
    entrepreneur = dialog.get_by_role("radio", name=re.compile(r"^Empreendedor"))
    with page.expect_response(
        lambda response: (
            response.request.method == "PUT"
            and "/players/me/profession" in response.url
        )
    ):
        entrepreneur.click()
    expect(dialog.get_by_text("Não deu para trocar a profissão")).to_be_visible()
    expect(dialog.get_by_text("A profissão não muda agora.")).to_be_visible()
    expect(entrepreneur).to_have_attribute("aria-checked", "false")


STATES: dict[str, Callable[[Page], None]] = {
    "carteira/vazia": portfolio_empty,
    "renda-variavel/detalhe": stock_detail,
    "renda-variavel/livro-com-ordem": stock_detail_with_order,
    "renda-variavel/lista": stocks_list,
    "mapa/padrao": map_default,
    "mapa/estados-expandido": map_states_expanded,
    "mapa/primeira-pesquisa": map_first_poll,
    "mapa/regiao": map_by_region,
    "mapa/erro": map_error,
    "preparacao/profissao": preparation_profession,
    "preparacao/profissao-escolhida": preparation_profession_selected,
    "preparacao/profissao-dica": preparation_profession_tag_open,
    "preparacao/profissao-sem-governo": preparation_profession_no_government,
    "preparacao/profissao-sem-inflacao": preparation_profession_no_inflation,
    "preparacao/profissao-partida-salva": preparation_profession_saved_match,
    "preparacao/profissao-recusa": preparation_profession_refused,
}
