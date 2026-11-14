"""
Receitas de estado: cada uma leva o app até uma tela ou estado que o canvas desenha.

O palco da skill de canvas carrega este arquivo: `app()` sobe o app e devolve a URL, e
`STATES` liga o nome do estado à função que leva a página até ele. A mesma receita serve
para trazer a tela ao canvas e para conferir a tela implementada contra o board.

O app é o da demonstração (`scripts/demo/`): o front buildado do código atual, sobre uma
cópia descartável do banco-base, semeado com as cotações fixas da demo. Toda rodada
parte do mesmo dado.
"""

import json
import os
import re
from collections.abc import Callable, Generator
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse

from playwright.sync_api import (
    Locator,
    Page,
    Playwright,
    Route,
    expect,
    sync_playwright,
)

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
    orders = page.get_by_role("region", name="Suas ordens")
    # Com o app mantido de pé, a ordem das rodadas anteriores continua aberta: um estado só tem uma
    if orders.is_visible():
        expect(page.locator("#order-size")).to_have_value("")
        page.wait_for_load_state("networkidle")
        return
    page.get_by_label("Tipo de ordem").get_by_text("Limitada").click()
    page.locator("#order-size").fill("100")
    hint = page.get_by_text(re.compile(r"Hoje:")).inner_text()
    today = re.search(r"Hoje:\s*R\$\s*([\d.,]+)", hint)
    assert today, f"o preço de hoje não apareceu na boleta: {hint!r}"
    price = float(today.group(1).replace(".", "").replace(",", ".")) * 0.95
    page.locator("#order-limit").fill(f"{price:.2f}".replace(".", ","))
    page.get_by_role("button", name=re.compile(r"^Comprar 100 PETR4 a")).click()
    page.get_by_role("region", name="Suas ordens").wait_for()
    # A boleta zera a quantidade e refaz a conferência depois do envio: o retrato sai com ela assentada
    expect(page.get_by_text("Conferindo a ordem…")).to_be_hidden()
    expect(page.locator("#order-size")).to_have_value("")
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


# O livro da PETR4 e as rotas que as receitas forjam (o `GET` do livro e o da estratégia)
ORDERS_PATH = "/api/variable-income/PETR4/orders"
ORDERS_GLOB = "**/api/variable-income/PETR4/orders"
STRATEGY_GLOB = "**/api/strategies/me"
LONG_NICKNAME = "Maria Eduarda Albuquerque de Souza Nogueira"
# A data da simulação da demo (02 jan 2023): as datas das ordens forjadas caem nela
FORGED_DATE = "2023-01-02"


def fulfill_get(page: Page, glob: str, body: str, status: int = 200) -> None:
    """
    Responde os `GET` de `glob` com `body`. Os outros métodos seguem para o servidor, então a
    ordem enviada pela boleta continua real.
    """

    def handle(route: Route) -> None:
        if route.request.method != "GET":
            route.continue_()
            return
        route.fulfill(status=status, content_type="application/json", body=body)

    page.route(glob, handle)


def real_orders(page: Page) -> list[dict]:
    """O livro que o servidor devolve agora: a base que as receitas forjadas alteram."""
    response = page.request.get(urljoin(page.url, ORDERS_PATH))
    if not response.ok:
        raise RuntimeError(f"O livro real não respondeu: HTTP {response.status}")
    return response.json()


def reload_detail(page: Page) -> None:
    """Recarrega o detalhe com as rotas já ligadas: o livro e a estratégia são pedidos de novo, forjados."""
    page.reload()
    page.get_by_role("heading", name=re.compile("PETR4")).first.wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def open_stock(page: Page) -> None:
    """Na lista de ações, abre a PETR4 sem esperar a rede assentar: as respostas pendentes ou com erro não assentam."""
    page.get_by_role("row", name=re.compile(r"^PETR4")).click()
    page.get_by_role("heading", name=re.compile("PETR4")).first.wait_for()


def money_value(text: str) -> float:
    """O valor em reais de um texto pt-BR: "R$ 1.234,55" vira 1234.55."""
    found = re.search(r"\d[\d.]*,\d+", text)
    assert found, f"sem valor em reais em {text!r}"
    return float(found.group(0).replace(".", "").replace(",", "."))


def number_in_field(field: Locator) -> float:
    """O número digitado num campo pt-BR; campo vazio ou sem número vira -1, que nunca bate com um preço."""
    found = re.fullmatch(r"\s*(\d[\d.]*)(?:,(\d+))?\s*", field.input_value())
    if not found:
        return -1.0
    return float(f"{found.group(1).replace('.', '')}.{found.group(2) or '0'}")


def book_partial_order(page: Page) -> None:
    """
    Detalhe da PETR4 com uma venda do jogador já parcialmente executada: 40 de 100, 60 restantes a
    R$ 12,40. A faixa "Suas ordens" mostra o progresso e o botão "Cancelar as 60 restantes".
    Dado forjado: a resposta de `GET /api/variable-income/PETR4/orders` é a lista real mais uma ordem
    de venda do jogador logado (status partial, size 100, remaining 60).
    """
    stock_detail(page)
    forged = {
        "id": "ordem-forjada-parcial",
        "player_nickname": demo_settings()["host"]["nickname"],
        "player_color": None,
        "player_is_bot": False,
        "action": "sell",
        "order_type": "limit",
        "status": "partial",
        "size": "100",
        "remaining": "60",
        "limit_price": 12.4,
        "placed_on": FORGED_DATE,
        "synthetic": False,
    }
    fulfill_get(page, ORDERS_GLOB, json.dumps([*real_orders(page), forged]))
    reload_detail(page)
    region = page.get_by_role("region", name="Suas ordens")
    expect(region).to_be_visible()
    expect(page.get_by_text("executou 40 de 100")).to_be_visible()
    expect(
        page.get_by_role("button", name="Cancelar as 60 restantes", exact=True)
    ).to_be_visible()


def book_automatic(page: Page) -> None:
    """
    Detalhe da PETR4 com uma compra limitada do jogador (a de `stock_detail_with_order`) e a
    estratégia automática ligada: a faixa "Suas ordens" diz que a estratégia cuida das ordens, e
    nenhuma ordem tem botão de cancelar.
    Dado forjado: a resposta de `GET /api/strategies/me` é a real com `active` preenchido pela
    primeira estratégia da lista; o resto da resposta fica como veio.
    """
    stock_detail_with_order(page)
    key = page.request.get(urljoin(page.url, "/api/strategies")).json()[0]["key"]
    mine = page.request.get(urljoin(page.url, "/api/strategies/me")).json()
    forged = mine | {"active": {"key": key, "params": {}, "since": FORGED_DATE}}
    fulfill_get(page, STRATEGY_GLOB, json.dumps(forged))
    reload_detail(page)
    region = page.get_by_role("region", name="Suas ordens")
    expect(region).to_be_visible()
    expect(
        page.get_by_text("A estratégia automática cuida das suas ordens")
    ).to_be_visible()
    expect(region.get_by_role("button", name="Cancelar")).to_have_count(0)


def book_click_fills(page: Page) -> None:
    """
    Detalhe da PETR4 sem ordem, com 100 na quantidade. Clicar numa compra do livro prepara uma
    venda; clicar numa venda prepara uma compra limitada ao preço da linha, com a quantidade
    digitada mantida e a boleta dizendo de onde veio ("Preenchido pelo livro"). Com o mouse sobre a
    venda, a linha mostra "Comprar a R$ … →". Sem dado forjado.
    """
    stock_detail(page)
    page.locator("#order-size").fill("100")
    buy_row = page.get_by_role("region", name="Compra").locator("[data-book-row]").first
    sell_row = page.get_by_role("region", name="Venda").locator("[data-book-row]").first
    buy_row.click()
    expect(page.get_by_role("button", name="Vender", exact=True)).to_have_attribute(
        "aria-pressed", "true"
    )
    sell_row.click()
    expect(page.get_by_role("button", name="Comprar", exact=True)).to_have_attribute(
        "aria-pressed", "true"
    )
    # O aviso e o preço do campo mudam no mesmo render: quando o aviso aparece, o campo já tem o valor
    expect(page.get_by_text("Preenchido pelo livro")).to_be_visible()
    price = money_value(sell_row.inner_text())
    assert number_in_field(page.locator("#order-limit")) == price, (
        "o preço limite não veio da linha clicada"
    )
    expect(page.locator("#order-size")).to_have_value("100")
    sell_row.hover()
    expect(sell_row.get_by_text(re.compile(r"Comprar a R\$"))).to_be_visible()


def book_own_row(page: Page) -> None:
    """
    Detalhe da PETR4 com a compra do jogador no livro, "Mostrar todas" aberto. A linha própria
    (com "(você)" na seção Compra) não é botão: clicar nela não mexe no preço da boleta.
    Dado forjado: nenhum; usa a ordem real de `stock_detail_with_order`.
    """
    stock_detail_with_order(page)
    page.get_by_role("button", name=re.compile(r"^Mostrar todas")).click()
    page.get_by_role(
        "button", name="Mostrar só as 8 mais perto do preço", exact=True
    ).wait_for()
    own = (
        page.get_by_role("region", name="Compra")
        .locator("[data-book-row]")
        .filter(has_text="(você)")
    )
    expect(own).to_have_count(1)
    expect(own.locator("button")).to_have_count(0)
    limit = page.locator("#order-limit")
    before = limit.input_value()
    own.click()
    expect(limit).to_have_value(before)
    expect(page.get_by_text("Preenchido pelo livro")).to_have_count(0)


def book_show_all(page: Page) -> None:
    """
    Detalhe da PETR4 com "Mostrar todas" aberto: o livro mostra todas as compras e vendas abertas,
    não só as 8 mais perto do preço. A contagem de linhas de cada seção bate com o botão.
    Sem dado forjado.
    """
    stock_detail(page)
    show = page.get_by_role("button", name=re.compile(r"^Mostrar todas"))
    counts = re.search(r"(\d+) compras e (\d+) vendas", show.inner_text())
    assert counts, "o botão 'Mostrar todas' não trouxe a contagem do livro"
    buys, sells = int(counts.group(1)), int(counts.group(2))
    show.click()
    page.get_by_role(
        "button", name="Mostrar só as 8 mais perto do preço", exact=True
    ).wait_for()
    expect(
        page.get_by_role("region", name="Compra").locator("[data-book-row]")
    ).to_have_count(buys)
    expect(
        page.get_by_role("region", name="Venda").locator("[data-book-row]")
    ).to_have_count(sells)


def book_hint(page: Page) -> None:
    """
    Detalhe da PETR4 com o popover "De onde vêm essas ofertas" aberto pelo botão (i): explica
    a diferença entre as duas melhores ofertas e a barra de quantidade. Sem dado forjado.
    """
    stock_detail(page)
    page.get_by_role("button", name="De onde vêm essas ofertas").click()
    expect(page.get_by_text("Diferença", exact=True)).to_be_visible()
    expect(page.get_by_text("Barra", exact=True)).to_be_visible()


def book_loading(page: Page) -> None:
    """
    Detalhe da PETR4 com o `GET` do livro pendente: ele nunca responde, então o card mostra o
    esqueleto e não tem as seções Compra e Venda. O título "Livro de ofertas" já está na tela.
    Dado forjado: a rota do livro recebe a requisição e não responde (não há fulfill nem continue).
    """
    stocks_list(page)
    page.route(ORDERS_GLOB, lambda route: None)
    open_stock(page)
    page.wait_for_selector('[data-slot="skeleton"]')
    expect(page.get_by_text("Livro de ofertas", exact=True)).to_be_visible()
    expect(page.get_by_role("region", name="Compra")).to_have_count(0)
    expect(page.get_by_role("region", name="Venda")).to_have_count(0)
    dismiss_topic(page)


def book_history(page: Page) -> None:
    """
    Detalhe da PETR4 com a aba "Histórico" do livro aberta. O banco da demo não tem negócio
    fechado na PETR4, então a aba mostra o vazio "Nenhum negócio ainda" (a tabela com a coluna
    "Comprou · vendeu" só aparece com negócios). Sem dado forjado.
    """
    stock_detail(page)
    page.get_by_role("button", name="Histórico", exact=True).click()
    expect(page.get_by_text("Nenhum negócio ainda", exact=True)).to_be_visible()


def book_error(page: Page) -> None:
    """
    Detalhe da PETR4 quando `GET /api/variable-income/PETR4/orders` falha: a resposta é forjada
    com status 500 e o corpo de erro da API. O card diz que não deu para carregar o livro e oferece
    "Tentar de novo". Sem ordens do jogador, o erro é o que aparece.
    """
    stocks_list(page)
    fulfill_get(
        page, ORDERS_GLOB, '{"message": "Falha ao consultar o livro."}', status=500
    )
    open_stock(page)
    expect(page.get_by_text("Não deu para carregar o livro.")).to_be_visible(
        timeout=60_000
    )
    expect(
        page.get_by_role("button", name="Tentar de novo", exact=True)
    ).to_be_visible()
    dismiss_topic(page)


def book_empty(page: Page) -> None:
    """
    Detalhe da PETR4 com o livro vazio: `GET /api/variable-income/PETR4/orders` responde `[]`.
    A aba de ofertas mostra "Sem ofertas hoje" e conta "Ofertas · 0".
    Dado forjado: a resposta do livro é uma lista vazia.
    """
    stocks_list(page)
    fulfill_get(page, ORDERS_GLOB, "[]")
    open_stock(page)
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text("Sem ofertas hoje")).to_be_visible()
    expect(page.get_by_role("button", name="Ofertas · 0", exact=True)).to_be_visible()
    dismiss_topic(page)


def book_long_text(page: Page) -> None:
    """
    Detalhe da PETR4 com números grandes no livro: preços de 4 dígitos (R$ 1.234,55 e R$ 1.234,57)
    e quantidades de 8 dígitos (87.650.000, 123.460.000 e 98.770.000), e um jogador com apelido longo.
    A página não pode ganhar rolagem horizontal: o nome longo fica truncado na linha.
    Dado forjado: a resposta real de `GET /api/variable-income/PETR4/orders` ganha três ordens na
    frente (duas compras e uma venda), copiadas de uma ordem real e com preço, quantidade e nome trocados.
    """
    stock_detail(page)
    orders = real_orders(page)
    assert orders, "o livro real da PETR4 veio vazio: não há ordem para usar de modelo"
    base = orders[0] | {
        "player_color": None,
        "player_is_bot": False,
        "order_type": "limit",
        "status": "pending",
        "synthetic": False,
        "placed_on": FORGED_DATE,
    }
    forged = [
        base
        | {
            "id": "forjada-compra-longa",
            "player_nickname": LONG_NICKNAME,
            "action": "buy",
            "limit_price": 1234.55,
            "size": "87650000",
            "remaining": "87650000",
        },
        base
        | {
            "id": "forjada-compra",
            "player_nickname": "Ana",
            "action": "buy",
            "limit_price": 1234.5,
            "size": "98770000",
            "remaining": "98770000",
        },
        base
        | {
            "id": "forjada-venda",
            "player_nickname": "Bruno",
            "action": "sell",
            "limit_price": 1234.57,
            "size": "123460000",
            "remaining": "123460000",
        },
    ]
    fulfill_get(page, ORDERS_GLOB, json.dumps(forged + orders))
    reload_detail(page)
    expect(page.get_by_text(LONG_NICKNAME).first).to_be_visible()
    fits = page.evaluate(
        "() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
    assert fits, (
        "a página ganhou rolagem horizontal com o livro de números e nomes longos"
    )


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
    "renda-variavel/livro-ordem-parcial": book_partial_order,
    "renda-variavel/livro-automatico": book_automatic,
    "renda-variavel/livro-clique-preenche": book_click_fills,
    "renda-variavel/livro-clique-propria": book_own_row,
    "renda-variavel/livro-mostrar-todas": book_show_all,
    "renda-variavel/livro-dica": book_hint,
    "renda-variavel/livro-carregando": book_loading,
    "renda-variavel/livro-historico": book_history,
    "renda-variavel/livro-erro": book_error,
    "renda-variavel/livro-vazio": book_empty,
    "renda-variavel/livro-texto-longo": book_long_text,
}
