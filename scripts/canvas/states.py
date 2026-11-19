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
from typing import Any
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
# O sinal de vezes (U+00D7) dos rótulos de velocidade
TIMES = chr(0xD7)

PROFESSION_NAMES = re.compile(
    r"^(CLT|Servidor|Empreendedor|Aposentado|Auxílio|Locador|Exportador|Bancário"
    r"|Autônomo|Corretor|Herdeiro|Recém-formado|Comissionado|Banqueiro de ofertas)\b"
)
# As profissões da sala sem expansões: o Autônomo só existe com a renda corrigida pela inflação
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


def fulfill_get(
    page: Page, glob: str | re.Pattern[str], body: str, status: int = 200
) -> None:
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
        "owner": "player",
        "action": "sell",
        "order_type": "limit",
        "status": "partial",
        "size": "100",
        "remaining": "60",
        "limit_price": 12.4,
        "placed_on": FORGED_DATE,
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
        "owner": "player",
        "order_type": "limit",
        "status": "pending",
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


# As gestoras: a partida com a expansão ligada e a gestora do host em cada fase da vida dela
FUND_NAME = "Aurora Gestão"
FUND_TICKER = "AURO11"
# Governo & Política exige 5 anos de partida: os CSVs da demo começam em jan 2021
GOVERNMENT_RULES = {
    "start_date": "2021-01-05",
    "end_date": "2026-01-05",
    "first_election": "2022-10-02",
}
# A ação que as receitas marcam como estatal, com 51% do governo
STATE_COMPANY_TICKER = "PETR4"
STATE_COMPANY_GOVERNMENT_SHARE = "0.51"
STATE_COMPANY_SHARES = 13_000_000_000
# O dia em que a carteira do presidente deixa de estar congelada, nas receitas que forjam o governo
FROZEN_UNTIL = "2023-01-01"
# Fases da gestora, da recém-fundada à oferta já encerrada
FUND_STAGES = ("founded", "contributed", "offer-open", "offer-closed")


def host_login(page: Page) -> None:
    """Entra com o nickname do host e espera o app abrir: o lobby ou a partida ativa."""
    page.goto("/login")
    page.get_by_label("Seu nickname").fill(demo_settings()["host"]["nickname"])
    page.get_by_role("button", name="Entrar").click()
    returning = page.get_by_role("button", name="Sou eu, entrar")
    lobby = page.get_by_role(
        "button",
        name=re.compile(r"^(Iniciar nova simulação|Continuar|Escolher partida salva)"),
    )
    portfolio = page.get_by_role("heading", name="Carteira")
    returning.or_(lobby).or_(portfolio).first.wait_for()
    if returning.is_visible():
        returning.click()
    page.wait_for_url(re.compile(r"/(lobby)?$"))


def api_json(page: Page, path: str) -> Any:
    response = page.request.get(urljoin(page.url, path))
    if not response.ok:
        raise RuntimeError(f"GET {path}: HTTP {response.status}")
    return response.json()


def api_send(page: Page, method: str, path: str, data: dict | None = None) -> None:
    response = page.request.fetch(urljoin(page.url, path), method=method, data=data)
    if not response.ok:
        raise RuntimeError(
            f"{method} {path}: HTTP {response.status} {response.text()[:300]}"
        )


def fund_stage(funds: list[dict], nickname: str, name: str) -> str | None:
    """A fase da gestora `name` do jogador, lida da lista da sala; nula quando ela não existe."""
    mine = next(
        (
            fund
            for fund in funds
            if fund["manager_nickname"] == nickname and fund["name"] == name
        ),
        None,
    )
    if mine is None:
        return None
    if mine["offer_closed_on"] is not None:
        return "offer-closed"
    if mine["listed_on"] is not None:
        return "offer-open"
    return "contributed" if float(mine["quotas"]) > 0 else "founded"


def fund_matches(page: Page, nickname: str, fund_name: str, stage: str) -> bool:
    """A sala já está na `stage` pedida: sem nenhuma gestora do jogador (`none`) ou com a `fund_name` nessa fase."""
    funds = api_json(page, "/api/funds")
    if stage == "none":
        return not any(fund["manager_nickname"] == nickname for fund in funds)
    return fund_stage(funds, nickname, fund_name) == stage


def fund_match(
    page: Page,
    *,
    funds: bool = True,
    stage: str = "founded",
    government: bool = True,
    game_type: str = "GOAL_RACE",
    fund_name: str = FUND_NAME,
    ticker: str = FUND_TICKER,
    state_company: bool = False,
) -> None:
    """
    Leva o host a uma partida com as regras pedidas e, com `funds`, a gestora dele na
    `stage` pedida (`none`: a expansão ligada e o host sem gestora). A partida que já está aberta com essas regras e nessa fase é reaproveitada;
    senão ela é encerrada e uma nova nasce pela API das regras, a mesma que o formulário chama.
    Com `state_company`, a PETR4 nasce estatal na partida; sem ele, comum. A partida copia as
    marcações da base na criação, e a base só muda fora de uma partida: a marcação se grava a cada
    partida nova, logo antes da criação, e a partida aberta se reaproveita quando a PETR4 dela está
    como o pedido.
    A gestora nasce por `POST /api/funds`, recebe caixa da carteira (R$ 5.000, a 100 por cota) e
    abre a oferta de 20 cotas, como o gestor faria nos diálogos.
    """
    host_login(page)
    nickname = demo_settings()["host"]["nickname"]
    status = api_json(page, "/api/simulation/status")
    running = status.get("simulation")
    if running:
        same_rules = (
            running["funds_enabled"] == funds
            and running["government_enabled"] == government
            and running["game_type"] == game_type
            and (STATE_COMPANY_TICKER in state_owned_tickers(page)) == state_company
        )
        # Sem a expansão a lista de gestoras recusa o pedido: só se consulta com as regras iguais
        same_fund = same_rules and (
            not funds or fund_matches(page, nickname, fund_name, stage)
        )
        if same_fund:
            page.goto("/")
            page.get_by_role("heading", name="Carteira").wait_for()
            page.wait_for_load_state("networkidle")
            dismiss_topic(page)
            return
        api_send(page, "POST", "/api/simulation/stop")
    page.goto("/lobby")
    page.get_by_role("button", name="Minha preparação").wait_for()
    current_settings = api_json(page, "/api/simulation/settings")
    if current_settings["selected_simulation_id"] is not None:
        raise RuntimeError(
            "Há uma partida salva selecionada: as regras não mudam pela API."
        )
    rules = (
        current_settings["simulation"]
        | {
            "game_type": game_type,
            "funds_enabled": funds,
            "government_enabled": government,
            "first_election": None,
        }
        | (GOVERNMENT_RULES if government else {})
    )
    api_send(page, "PUT", "/api/simulation/settings", rules)
    # A gestora nasce só pelos passos desta receita: o perfil não funda nada no 1º dia
    api_send(
        page,
        "PUT",
        "/api/simulation/players/me/fund-preparation",
        {"kind": "NONE"},
    )
    if state_company:
        mark_state_company(page, STATE_COMPANY_TICKER)
    else:
        api_send(
            page, "DELETE", f"/api/import-assets/stocks/{STATE_COMPANY_TICKER}/state"
        )
    api_send(page, "POST", "/api/simulation/create", rules)
    if funds and stage != "none":
        api_send(
            page,
            "POST",
            "/api/funds",
            {
                "name": fund_name,
                "ticker": ticker,
                "management_fee": "0.02",
                "performance_fee": "0.2",
            },
        )
        fund_id = api_json(page, "/api/funds")[0]["id"]
        steps = FUND_STAGES.index(stage)
        if steps >= 1:
            api_send(
                page,
                "POST",
                f"/api/funds/{fund_id}/contributions",
                {"cash": "5000", "stocks": []},
            )
        if steps >= 2:
            api_send(page, "POST", f"/api/funds/{fund_id}/offer", {"quotas": 20})
        if steps >= 3:
            api_send(page, "DELETE", f"/api/funds/{fund_id}/offer")
    page.goto("/")
    page.get_by_role("heading", name="Carteira").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def patch_get(
    page: Page, glob: str | re.Pattern[str], change: Callable[[dict | list], None]
) -> None:
    """
    Dado forjado sobre o dado real: os `GET` de `glob` vão ao servidor e a resposta volta
    depois de `change` alterar o JSON no lugar; os outros métodos seguem sem alteração.
    """

    def handle(route: Route) -> None:
        if route.request.method != "GET":
            route.continue_()
            return
        response = route.fetch()
        body = response.json()
        change(body)
        route.fulfill(response=response, body=json.dumps(body))

    page.route(glob, handle)


def hang_get(page: Page, glob: str | re.Pattern[str]) -> None:
    """A rota nunca responde: a consulta fica carregando."""
    page.route(glob, lambda route: None)


# Camadas em portal: o menu e a dica do design system
MENU_LAYER = '[role="menu"]'
TOOLTIP_LAYER = '[data-slot="tooltip-content"]'
STATE_GLOB = "**/api/get-simulation-state"
ACCOUNTS_GLOB = "**/api/funds/accounts"
PENDING_GLOB = "**/api/pending"
GOVERNMENT_GLOB = "**/api/government"


def forge_running_speed(page: Page, speed: int = 10) -> None:
    """Dado forjado: o estado da simulação responde rodando na velocidade pedida (a partida da receita fica pausada)."""

    def change(state: dict | list) -> None:
        assert isinstance(state, dict)
        state["speed"] = speed

    patch_get(page, STATE_GLOB, change)


def forge_president(page: Page) -> None:
    """
    Dado forjado: o host governa. O painel do governo responde `is_president` com a carteira
    congelada até `FROZEN_UNTIL`, e as contas do caixa trazem o mesmo congelamento.
    """

    def panel(body: dict | list) -> None:
        assert isinstance(body, dict)
        body["is_president"] = True
        body["computer_until_inauguration"] = False
        body["portfolio"] = {
            "nickname": demo_settings()["host"]["nickname"],
            "total_networth": "18420.35",
            "frozen_until": FROZEN_UNTIL,
            "slices": [],
            "interests": [],
        }

    def accounts(body: dict | list) -> None:
        assert isinstance(body, list)
        for account in body:
            account["frozen_until"] = FROZEN_UNTIL

    patch_get(page, GOVERNMENT_GLOB, panel)
    patch_get(page, ACCOUNTS_GLOB, accounts)


def open_stocks(page: Page) -> None:
    """A página Renda variável, que o board da topbar desenha: o título da topbar vem dela."""
    sidebar(page, "Renda variável").click()
    page.get_by_role("row", name=re.compile(r"^PETR4")).wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def reload_stocks(page: Page) -> None:
    """Recarrega a Renda variável com as rotas forjadas já ligadas: a topbar pede o dado de novo."""
    page.reload()
    page.get_by_role("row", name=re.compile(r"^PETR4")).wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def adopt_layer(page: Page, layer_selector: str, into: str = "header") -> None:
    """
    A camada flutuante aberta (menu, dica) achada por `layer_selector` passa para dentro de `into`: o
    retrato da tela parte de uma raiz só, e o board desenha a camada dentro da topbar. A camada
    segue na mesma posição da tela: o novo pai muda o ponto de referência do posicionamento, e
    o deslocamento que isso causa volta pelo `left`/`top` do posicionador.
    """
    moved = page.evaluate(
        """([selector, into]) => {
            const layer = document.querySelector(selector);
            const target = document.querySelector(into);
            if (!layer || !target) return false;
            let top = layer;
            while (top.parentElement && top.parentElement !== document.body) top = top.parentElement;
            if (target.contains(top)) return true;
            const before = layer.getBoundingClientRect();
            target.appendChild(top);
            const after = layer.getBoundingClientRect();
            let positioner = layer;
            while (positioner !== top && getComputedStyle(positioner).position !== "absolute") {
                positioner = positioner.parentElement;
            }
            positioner.style.left = `${before.x - after.x}px`;
            positioner.style.top = `${before.y - after.y}px`;
            return true;
        }""",
        [layer_selector, into],
    )
    assert moved, f"nenhuma camada {layer_selector} aberta para levar a {into}"


def topbar_open(page: Page, **match) -> None:
    """A Renda variável aberta numa partida com as regras de `match`, pausada."""
    fund_match(page, **match)
    open_stocks(page)


# O nome mais longo que a sala aceita (40 letras): o rótulo do caixa corta com reticências
LONG_FUND_NAME = "Fundo Multiestratégia Patrimonial Rafael"
LONG_FUND_CASH = "12345678901.23"


def cash_button(page: Page) -> Locator:
    """O botão do caixa na topbar: abre o menu "Operar com" quando há mais de uma conta."""
    return page.locator("header").get_by_role("button", name=re.compile(r"Caixa ·"))


def open_account_menu(page: Page) -> None:
    """Abre o menu "Operar com" e o leva para dentro da topbar, onde o retrato o alcança."""
    cash_button(page).click()
    page.get_by_role("menu").get_by_text("Operar com").wait_for()
    adopt_layer(page, MENU_LAYER)


def topbar_default(page: Page) -> None:
    """
    Topbar a 1920 com tudo ligado (gestora, governo do computador, corrida à meta) na conta
    pessoal, rodando a dez vezes. Dado forjado: o estado da simulação responde a velocidade 10 (a
    partida da receita fica pausada).
    """
    topbar_open(page)
    forge_running_speed(page)
    reload_stocks(page)
    expect(
        page.locator("header").get_by_role("button", name="Pausar simulação")
    ).to_be_visible()


def topbar_1366(page: Page) -> None:
    """Como topbar/padrao, a 1366 de largura: o selo do governo vira ícone e uma palavra e a topbar fica numa linha só."""
    topbar_default(page)
    page.set_viewport_size({"width": 1366, "height": 768})
    expect(page.locator("header").get_by_text("Computador", exact=True)).to_be_visible()
    one_row = page.evaluate("() => document.querySelector('header').offsetHeight <= 80")
    assert one_row, "a topbar a 1366 passou de uma linha"


def topbar_paused(page: Page) -> None:
    """Topbar pausada: o jogador pausa a partida que corria a dez vezes, e a data vira "Pausado" sobre o âmbar com o play no lugar do pause."""
    topbar_open(page)
    api_send(page, "POST", "/api/set-speed", {"speed": 10})
    reload_stocks(page)
    page.get_by_role("button", name="Pausar simulação").click()
    expect(page.locator("header").get_by_role("status")).to_contain_text("Pausado")
    expect(page.get_by_role("button", name="Retomar simulação")).to_be_visible()


def topbar_pip_hint(page: Page) -> None:
    """Como topbar/padrao, com a dica do tracinho de dez vezes aberta por hover: a velocidade, a tecla do tracinho e o atalho de pausa."""
    topbar_default(page)
    page.get_by_role("button", name=f"Velocidade 10{TIMES}").hover()
    tooltip = page.locator(TOOLTIP_LAYER)
    expect(tooltip).to_contain_text("tecla")
    expect(tooltip).to_contain_text("Espaço")
    adopt_layer(page, TOOLTIP_LAYER)


def topbar_menu_open(page: Page) -> None:
    """Como topbar/padrao, com o menu "Operar com" aberto: a carteira pessoal marcada e a gestora na lista."""
    topbar_default(page)
    open_account_menu(page)
    expect(page.get_by_role("menu").get_by_text(FUND_NAME)).to_be_visible()


def topbar_operating_fund(page: Page) -> None:
    """Topbar operando a gestora, escolhida no menu "Operar com": rótulo e valor na cor dela e a faixa sob a topbar."""
    topbar_default(page)
    cash_button(page).click()
    page.get_by_role("menuitem", name=re.compile(FUND_NAME)).click()
    expect(page.get_by_text("Você está operando a")).to_be_visible()
    expect(cash_button(page)).to_contain_text(FUND_NAME)
    page.wait_for_load_state("networkidle")


def forge_governing(page: Page) -> None:
    """Como topbar/padrao, com o host governando: carteira congelada (dado forjado em `/api/government` e `/api/funds/accounts`)."""
    topbar_open(page)
    forge_running_speed(page)
    forge_president(page)
    reload_stocks(page)
    expect(
        page.locator("header").get_by_role("img", name=re.compile("^Congelada até"))
    ).to_be_visible()


def topbar_governing_hint(page: Page) -> None:
    """Dado forjado: o host governa (carteira congelada). A dica do cadeado, no rótulo do caixa, aberta por hover."""
    forge_governing(page)
    page.locator("header").get_by_role(
        "img", name=re.compile("^Congelada até")
    ).first.hover()
    tooltip = page.locator(TOOLTIP_LAYER)
    expect(tooltip).to_contain_text("Você governa")
    adopt_layer(page, TOOLTIP_LAYER)


def topbar_governing_menu(page: Page) -> None:
    """Dado forjado: o host governa (carteira congelada). O menu "Operar com" aberto, com as duas contas congeladas e o rodapé que diz isso."""
    forge_governing(page)
    open_account_menu(page)
    expect(
        page.get_by_role("menu").get_by_text("As contas estão congeladas até")
    ).to_be_visible()


def topbar_overdraft(page: Page) -> None:
    """
    Topbar do viver de renda sem gestoras, com o caixa negativo: o rótulo vira "Cheque especial"
    com o juro. Dado forjado: o estado da simulação responde o caixa pessoal negativo.
    """
    topbar_open(page, funds=False, game_type="FINANCIAL_INDEPENDENCE")

    def change(state: dict | list) -> None:
        assert isinstance(state, dict)
        state["cash"] = "-4210"
        state["speed"] = 10

    patch_get(page, STATE_GLOB, change)
    reload_stocks(page)
    expect(page.locator("header").get_by_text("Cheque especial")).to_be_visible()


def topbar_long_fund_name(page: Page) -> None:
    """
    Topbar a 1366 operando uma gestora de nome no limite de 40 letras e caixa de 11 dígitos:
    o rótulo corta com reticências e o selo do governo fica curto. Dado forjado: o caixa da
    gestora em `/api/funds/accounts`.
    """
    topbar_open(page, fund_name=LONG_FUND_NAME, ticker="FMPR11")
    forge_running_speed(page)

    def change(accounts: dict | list) -> None:
        assert isinstance(accounts, list)
        for account in accounts:
            if account["fund_id"] is not None:
                account["cash"] = LONG_FUND_CASH

    patch_get(page, ACCOUNTS_GLOB, change)
    reload_stocks(page)
    page.set_viewport_size({"width": 1366, "height": 768})
    cash_button(page).click()
    page.get_by_role("menuitem", name=re.compile("^Fundo Multi")).click()
    expect(page.get_by_text("Você está operando a")).to_be_visible()
    page.wait_for_load_state("networkidle")


def topbar_classic(page: Page) -> None:
    """Topbar da partida clássica: sem gestora, sem governo e sem corrida à meta."""
    topbar_open(page, funds=False, government=False, game_type="CLASSIC")
    forge_running_speed(page)
    reload_stocks(page)
    expect(page.locator("header").get_by_text("Meta")).to_have_count(0)


def topbar_loading(page: Page) -> None:
    """Dado forjado: o estado da simulação nunca responde, e a data e o caixa ficam em esqueleto."""
    topbar_open(page)
    hang_get(page, STATE_GLOB)
    page.reload()
    page.locator("header").get_by_role("heading").wait_for()


# A gestora de outro jogador, vista pelo host: o dono do cartão é a Duda
OTHER_MANAGER_ID = 999_999
FUND_DETAIL_PATTERN = re.compile(r"/api/funds/\d+$")
FUNDS_LIST_PATTERN = re.compile(r"/api/funds$")


def open_funds_page(page: Page) -> None:
    """A página das gestoras pelo menu: com gestora própria ela abre na página da gestora."""
    page.goto("/funds")
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def fund_page(page: Page, stage: str, **match) -> None:
    """A página da gestora do host na fase `stage`, aberta pelo menu Gestoras."""
    fund_match(page, stage=stage, **match)
    open_funds_page(page)
    page.locator(CONTENT).get_by_role(
        "heading", name=match.get("fund_name", FUND_NAME)
    ).wait_for()


def open_fund_tab(page: Page, tab: str, ready: str | None = None) -> None:
    """A aba `tab` da página da gestora, aberta pelo rótulo; com `ready`, espera esse texto dela."""
    page.get_by_role("tab", name=re.compile(rf"^{tab}")).click()
    if ready:
        page.get_by_text(ready).first.wait_for()
    page.wait_for_load_state("networkidle")


def fund_tab_page(
    page: Page, stage: str, tab: str, ready: str | None = None, **match
) -> None:
    """A página da gestora do host na fase `stage`, na aba `tab`."""
    fund_page(page, stage, **match)
    open_fund_tab(page, tab, ready)


def funds_none(page: Page) -> None:
    """A página das gestoras de quem ainda não fundou: o convite e a lista da sala."""
    fund_match(page, stage="none")
    open_funds_page(page)
    page.get_by_role("heading", name="Funde a sua gestora").wait_for()


def funds_founded(page: Page) -> None:
    """A gestora fundada junto com a sala: nasce sem caixa nem cotas."""
    fund_page(page, "founded")
    page.get_by_text("Para abrir a gestora").first.wait_for()


def tab_actions(page: Page) -> None:
    """Suas ações do gestor com a oferta pública encerrada."""
    fund_page(page, "offer-closed")
    page.get_by_text("Como gestor").first.wait_for()
    page.wait_for_load_state("networkidle")


def tab_actions_closed(page: Page) -> None:
    """Suas ações da gestora fechada: os três passos para abrir."""
    fund_page(page, "contributed")
    page.get_by_text("Para abrir a gestora").first.wait_for()
    page.wait_for_load_state("networkidle")


def tab_actions_holder(page: Page) -> None:
    """Suas ações de quem só tem cotas (a gestora é de outro jogador)."""
    funds_viewer(page)
    page.get_by_text("Como cotista").first.wait_for()


def tab_overview(page: Page) -> None:
    """A Visão geral da gestora listada."""
    fund_tab_page(page, "offer-closed", "Visão geral", "Quanto rendeu")


def tab_overview_closed(page: Page) -> None:
    """A Visão geral da gestora fechada: o estado vazio."""
    fund_tab_page(
        page, "contributed", "Visão geral", "Preço e histórico chegam com o mercado"
    )


def tab_portfolio(page: Page) -> None:
    """A Carteira do gestor."""
    fund_tab_page(page, "offer-closed", "Carteira", "Patrimônio da gestora")


def tab_portfolio_frozen(page: Page) -> None:
    """Dado forjado: o gestor governa e a carteira da gestora fica congelada."""

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        body["frozen_until"] = FROZEN_UNTIL

    fund_match(page, stage="offer-closed")
    patch_get(page, FUND_DETAIL_PATTERN, change)
    open_funds_page(page)
    open_fund_tab(page, "Carteira", "Patrimônio da gestora")


def tab_quotas(page: Page) -> None:
    """A aba Cotas: cotistas, emissões e ofertas."""
    fund_tab_page(page, "offer-closed", "Cotas", "Emissões")


def tab_income(page: Page) -> None:
    """A aba Rendimentos."""
    fund_tab_page(page, "offer-closed", "Rendimentos", "Quanto a cota paga")


def tab_report(page: Page) -> None:
    """A aba Relatório."""
    fund_tab_page(page, "offer-closed", "Relatório", "O primeiro relatório")


def tab_settings(page: Page) -> None:
    """A aba Configurações do gestor."""
    fund_tab_page(page, "offer-closed", "Configurações", "Taxas")


def assembly_tally(total: float, favor: float, against: float) -> dict:
    """O placar em cotas de uma votação: o que falta de abstenção e quantas cotas a favor ainda faltam para vencer."""
    return {
        "in_favor": str(favor),
        "against": str(against),
        "abstention": str(total - favor - against),
        "total": str(total),
        "missing_to_win": str(max(against - favor + 1, 0)),
    }


def assembly_voters(total: float, stances: list[tuple[str, float, str]]) -> list[dict]:
    """Os cotistas jogadores da votação: (apelido, cotas, posição)."""
    return [
        {
            "user_id": 100 + index,
            "nickname": nickname,
            "color": None,
            "quotas": str(quotas),
            "share": str(quotas / total),
            "stance": stance,
            "is_manager": False,
        }
        for index, (nickname, quotas, stance) in enumerate(stances)
    ]


ASSEMBLY_HISTORY = [
    {
        "id": 91,
        "agenda": "REPLACE_MANAGER",
        "status": "KEPT",
        "convener_nickname": "Bia",
        "candidate_nickname": "Bia",
        "previous_manager_nickname": "Ana",
        "started_on": "2026-10-27",
        "closed_on": "2026-11-02",
        "tally": {
            "in_favor": "2",
            "against": "9",
            "abstention": "9",
            "total": "20",
            "missing_to_win": "8",
        },
        "fee": None,
        "effective_on": None,
    },
    {
        "id": 90,
        "agenda": "FEE_INCREASE",
        "status": "APPROVED",
        "convener_nickname": "Ana",
        "candidate_nickname": None,
        "previous_manager_nickname": "Ana",
        "started_on": "2026-06-02",
        "closed_on": "2026-06-08",
        "tally": {
            "in_favor": "9",
            "against": "2",
            "abstention": "9",
            "total": "20",
            "missing_to_win": "0",
        },
        "fee": {
            "management_from": "0.015000",
            "management_to": "0.020000",
            "performance_from": "0.200000",
            "performance_to": "0.200000",
        },
        "effective_on": "2026-07-01",
    },
]


def assembly_current(agenda: str, **over) -> dict:
    """Uma votação aberta como a página a recebe; `over` ajusta o que a cena pede."""
    fee = (
        {
            "management_from": "0.020000",
            "management_to": "0.030000",
            "performance_from": "0.200000",
            "performance_to": "0.200000",
        }
        if agenda == "FEE_INCREASE"
        else None
    )
    return {
        "id": 1 if agenda == "REPLACE_MANAGER" else 2,
        "agenda": agenda,
        "status": "VOTING",
        "convener_user_id": 7,
        "convener_nickname": "Bia",
        "candidate_user_id": 7 if agenda == "REPLACE_MANAGER" else None,
        "candidate_nickname": "Bia" if agenda == "REPLACE_MANAGER" else None,
        "fee": fee,
        "called_on": "2026-11-18",
        "started_on": "2026-11-18",
        "ends_on": "2026-11-24",
        "session": 2,
        "sessions": 5,
        "tally": assembly_tally(20, 6, 4),
        "voters": assembly_voters(20, [("Bia", 6, "favor"), ("Caio", 4, "against")]),
        "non_voting": "5",
        "my_vote": None,
        "can_vote": True,
    } | over


def forge_assembly(page: Page, panel: dict, **fund_fields) -> None:
    """Dado forjado: a seção Assembleia da gestora do host vem com o `panel` pedido, e `fund_fields` ajusta o resto da página."""

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        body["assembly"] = panel
        body.update(fund_fields)

    patch_get(page, FUND_DETAIL_PATTERN, change)


def assembly_panel(**over) -> dict:
    """O painel da assembleia sem votação aberta: as duas pautas liberadas e o histórico."""
    return {
        "current": [],
        "history": ASSEMBLY_HISTORY,
        "options": [
            {
                "agenda": "REPLACE_MANAGER",
                "can_convene": True,
                "block": None,
                "next_allowed_on": None,
            },
            {
                "agenda": "FEE_INCREASE",
                "can_convene": False,
                "block": "manager_only",
                "next_allowed_on": None,
            },
        ],
        "convene_quotas": "2",
        "my_quotas": "5",
        "blocked_founding_until": None,
    } | over


def tab_assembly(page: Page) -> None:
    """Dado forjado: uma troca de gestor em votação, vista por um cotista que ainda não votou."""
    fund_match(page, stage="offer-closed")
    forge_assembly(
        page,
        assembly_panel(current=[assembly_current("REPLACE_MANAGER")]),
        manager_user_id=OTHER_MANAGER_ID,
        manager_nickname="Duda",
        my_role="viewer",
        my_quotas="5",
    )
    open_funds_page(page)
    open_fund_tab(page, "Assembleia", "Como a assembleia decide")


def tab_assembly_fee(page: Page) -> None:
    """Dado forjado: um aumento de taxa em votação, visto pelo gestor, que não vota."""
    fund_match(page, stage="offer-closed")
    forge_assembly(
        page,
        assembly_panel(
            current=[assembly_current("FEE_INCREASE", can_vote=False)],
            options=[
                {
                    "agenda": "REPLACE_MANAGER",
                    "can_convene": False,
                    "block": "manager",
                    "next_allowed_on": None,
                },
                {
                    "agenda": "FEE_INCREASE",
                    "can_convene": False,
                    "block": "pending",
                    "next_allowed_on": None,
                },
            ],
        ),
    )
    open_funds_page(page)
    open_fund_tab(page, "Assembleia", "Como a assembleia decide")


def tab_assembly_empty(page: Page) -> None:
    """Dado forjado: sem votação aberta, com votações passadas e a convocação do aumento liberada ao gestor."""
    fund_match(page, stage="offer-closed")
    forge_assembly(
        page,
        assembly_panel(
            options=[
                {
                    "agenda": "REPLACE_MANAGER",
                    "can_convene": False,
                    "block": "manager",
                    "next_allowed_on": None,
                },
                {
                    "agenda": "FEE_INCREASE",
                    "can_convene": True,
                    "block": None,
                    "next_allowed_on": None,
                },
            ]
        ),
    )
    open_funds_page(page)
    open_fund_tab(page, "Assembleia", "Como a assembleia decide")


def funds_closed(page: Page) -> None:
    """A gestora fechada, com as cotas do gestor e sem oferta."""
    fund_page(page, "contributed")


def funds_offer_open(page: Page) -> None:
    """A gestora com a oferta pública aberta, vista pelo gestor."""
    fund_tab_page(page, "offer-open", "Cotas", "Oferta pública em andamento")


def funds_offer_closed(page: Page) -> None:
    """A gestora depois da oferta pública encerrada."""
    fund_tab_page(page, "offer-closed", "Cotas", "Oferta pública encerrada")


def funds_long_distributions(page: Page) -> None:
    """
    A gestora listada vista pelo gestor, com 14 meses de rendimentos na tabela, de dezembro de
    2020 para trás. Dado forjado: a partida nova não tem rendimento apurado, e as linhas vêm
    prontas em `distributions`.
    """

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        rows = []
        for index in range(14):
            year, month = divmod(11 - index, 12)
            day = f"{2020 + year}-{month + 1:02d}-28"
            profit = 4200 + 310 * (index % 5)
            rows.append(
                {
                    "data_com": day,
                    "realized_profit": str(profit),
                    "rate": "0.9",
                    "quotas": "500",
                    "per_quota": str(round(profit * 0.9 / 500, 2)),
                    "paid_per_quota": str(round(profit * 0.9 / 500, 2)),
                    "paid": str(round(profit * 0.9, 2)),
                    "paid_on": day,
                }
            )
        body["distributions"] = rows

    fund_match(page, stage="offer-closed")
    patch_get(page, FUND_DETAIL_PATTERN, change)
    open_funds_page(page)
    open_fund_tab(page, "Rendimentos", "Pago em")


def funds_loading(page: Page) -> None:
    """Dado forjado: a lista de gestoras nunca responde e a página fica em esqueleto."""
    fund_match(page, stage="none")
    hang_get(page, FUNDS_LIST_PATTERN)
    page.goto("/funds")
    page.locator('[aria-busy="true"]').first.wait_for()


def funds_error(page: Page) -> None:
    """Dado forjado: a lista de gestoras responde 500 e a página mostra o erro com a nova tentativa."""
    fund_match(page, stage="none")
    fulfill_get(page, FUNDS_LIST_PATTERN, '{"detail": "falha"}', status=500)
    page.goto("/funds")
    page.get_by_role("button", name="Tentar de novo").wait_for()


def funds_long_text(page: Page) -> None:
    """A gestora de nome no limite de 40 letras."""
    fund_page(page, "contributed", fund_name=LONG_FUND_NAME, ticker="FMPR11")


def funds_viewer(page: Page) -> None:
    """
    A gestora de outro jogador vista pelo host, que tem cotas dela. Dado forjado: o gestor
    da gestora é outra pessoa e as cotas do host vêm em `my_quotas`.
    """
    fund_match(page, stage="offer-open")

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        body["manager_user_id"] = OTHER_MANAGER_ID
        body["manager_nickname"] = "Duda"
        body["my_role"] = "other"
        body["my_quotas"] = "5"
        body["my_value"] = "500"
        body["my_return"] = "0.0812"

    patch_get(page, FUND_DETAIL_PATTERN, change)
    open_funds_page(page)
    page.goto(f"/funds/{api_json(page, '/api/funds')[0]['id']}")
    page.get_by_text("Gerida por Duda").wait_for()
    page.wait_for_load_state("networkidle")


def forge_room(page: Page, rows: Callable[[dict], list[dict]]) -> None:
    """
    Dado forjado sobre a lista da sala: `rows` recebe a gestora real do host (cotas dele em
    `my_quotas`) e devolve a lista que a página recebe; cada gestora forjada é uma cópia dela
    com id, nome e dados próprios.
    """

    def change(body: dict | list) -> None:
        assert isinstance(body, list)
        body[:] = rows(body[0])

    patch_get(page, FUNDS_LIST_PATTERN, change)


def room_fund(base: dict, fund_id: int, **fields: object) -> dict:
    """Uma gestora da sala forjada: cópia de `base` com o `fund_id` e os `fields` pedidos."""
    return base | {
        "id": fund_id,
        "founder_user_id": OTHER_MANAGER_ID,
        "manager_user_id": OTHER_MANAGER_ID,
        "manager_nickname": "Duda",
        "frozen_until": None,
        "leave_until": None,
        "leave_manager_user_id": None,
        "comanager_nicknames": [],
        "i_comanage": False,
        "my_quotas": "0",
        **fields,
    }


def open_room(page: Page) -> None:
    """A lista da sala aberta pelo menu Gestoras."""
    open_funds_page(page)
    page.get_by_role("heading", name="Gestoras da sala").wait_for()
    page.wait_for_load_state("networkidle")


def room_blocks(page: Page) -> None:
    """A sala nos três blocos: o host gere uma, tem cotas de outra e vê duas da sala."""
    fund_match(page, stage="offer-open")
    fund_id = api_json(page, "/api/funds")[0]["id"]

    def decisions(body: dict | list) -> None:
        assert isinstance(body, list)
        body += [
            {
                "key": f"FUND_ASSEMBLY_VOTE:{number}",
                "type": "FUND_ASSEMBLY_VOTE",
                "severity": "WARNING",
                "title": "Votação na gestora",
                "detail": "",
                "resolves": "",
                "loan_id": None,
                "fund_id": fund_id,
            }
            for number in range(3)
        ]

    patch_get(page, PENDING_GLOB, decisions)

    def rows(mine: dict) -> list[dict]:
        return [
            mine | {"my_quotas": "0", "comanager_nicknames": ["Duda"]},
            room_fund(
                mine,
                9001,
                name="Boreal Renda",
                ticker="BORE11",
                manager_nickname="Duda",
                my_quotas="12",
            ),
            room_fund(
                mine,
                9002,
                name="Cerrado Ações",
                ticker="CERR11",
                manager_user_id=OTHER_MANAGER_ID + 1,
                manager_nickname="Caio",
            ),
            room_fund(
                mine,
                9003,
                name="Delta Crédito",
                ticker="DELT11",
                manager_user_id=OTHER_MANAGER_ID + 2,
                manager_nickname="Eva",
            ),
        ]

    forge_room(page, rows)
    open_room(page)


def room_president(page: Page) -> None:
    """O host governa e a gestora dele está em licença: o vice a gere e ela volta no fim do mandato."""
    fund_match(page, stage="offer-open")
    host_id = api_json(page, "/api/funds")[0]["manager_user_id"]

    def rows(mine: dict) -> list[dict]:
        return [
            mine
            | {
                "manager_user_id": OTHER_MANAGER_ID,
                "manager_nickname": "Duda",
                "leave_manager_user_id": host_id,
                "leave_until": FROZEN_UNTIL,
            },
            room_fund(mine, 9002, name="Cerrado Ações", ticker="CERR11"),
        ]

    forge_room(page, rows)
    open_room(page)


def room_two_held(page: Page) -> None:
    """O host gere duas gestoras: a que fundou e a que ganhou da assembleia."""
    fund_match(page, stage="offer-open")
    first = api_json(page, "/api/funds")[0]

    def rows(mine: dict) -> list[dict]:
        return [
            mine,
            room_fund(
                mine,
                9001,
                name="Boreal Renda",
                ticker="BORE11",
                manager_user_id=first["manager_user_id"],
                manager_nickname=first["manager_nickname"],
                manager_since="2003-11-10",
            ),
        ]

    forge_room(page, rows)
    open_room(page)


def found_fund_open(page: Page) -> None:
    """A tela de fundar a gestora, de quem ainda não fundou."""
    fund_match(page, stage="none")
    page.goto("/funds/new")
    page.get_by_role("heading", name="Fundar uma gestora").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def found_fund_filled(page: Page) -> None:
    """A fundação com nome, sigla livre e um valor levado do caixa: a conta das cotas ao lado."""
    found_fund_open(page)
    page.get_by_label("Nome da gestora").fill(FUND_NAME)
    page.get_by_label("Sigla da cota").fill("AURO")
    page.get_by_label("Caixa").fill("1000")
    page.get_by_role("button", name="Fundar a Aurora Gestão").wait_for()
    page.wait_for_load_state("networkidle")


def found_fund_ticker_taken(page: Page) -> None:
    """A sigla digitada é a de um ativo da partida: a resposta aparece enquanto o jogador digita."""
    found_fund_open(page)
    page.get_by_label("Sigla da cota").fill("PETR")
    page.get_by_role("status").filter(has_text="já é um ativo da partida").wait_for()


def fund_dialog(page: Page, stage: str, button: str) -> Locator:
    """A página da gestora na fase `stage` com o diálogo do botão `button` aberto."""
    fund_page(page, stage)
    page.get_by_role("button", name=button).first.click()
    dialog = page.get_by_role("dialog")
    dialog.wait_for()
    return dialog


def dialog_offer(page: Page) -> None:
    """Oferta pública: o gestor escolhe quantas cotas a sala pode comprar."""
    dialog = fund_dialog(page, "contributed", "Abrir a oferta")
    dialog.get_by_label("Quantas cotas").fill("20")
    dialog.get_by_text("Você mantém o controle").wait_for()


def dialog_offer_too_big(page: Page) -> None:
    """Oferta que tira o controle do gestor: o aviso troca de cor antes do clique."""
    dialog = fund_dialog(page, "contributed", "Abrir a oferta")
    dialog.get_by_label("Quantas cotas").fill("200")
    dialog.get_by_text("Você perde o controle").wait_for()


def dialog_contribute(page: Page) -> None:
    """Levar da carteira: a gestora fechada recebe caixa do gestor."""
    dialog = fund_dialog(page, "founded", "Levar da carteira")
    dialog.get_by_label("Caixa").fill("1000")


def dialog_fees(page: Page) -> None:
    """Taxas: as duas taxas com o teto da partida e o aviso de que a nova vale no mês seguinte."""
    fund_dialog(page, "contributed", "Conferir taxas")


def fund_account_stock(page: Page) -> None:
    """A página de uma ação operada pela gestora: o painel de ordem leva a cor dela."""
    topbar_operating_fund(page)
    open_stock(page)
    page.wait_for_load_state("networkidle")


def fund_selling(page: Page) -> None:
    """O gestor digita a quantidade e o preço máximo de uma recompra: a prévia de custo aparece antes do clique."""
    dialog = fund_dialog(page, "offer-closed", "Recomprar")
    dialog.get_by_placeholder("Ex.: 500").fill("49")
    dialog.get_by_placeholder("R$ 0,00").fill("10")
    dialog.get_by_text("Custa até").wait_for()


def fund_governing(page: Page) -> None:
    """Dado forjado: o gestor governa e a gestora não tem co-gestor, então a página dela avisa que a carteira está congelada."""

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        body["frozen_until"] = FROZEN_UNTIL

    fund_match(page, stage="contributed")
    patch_get(page, FUND_DETAIL_PATTERN, change)
    open_funds_page(page)
    page.get_by_text("A carteira está congelada").wait_for()
    page.wait_for_load_state("networkidle")


def fund_frozen_panel(page: Page) -> None:
    """Dado forjado: o host governa e opera pela gestora, então o painel de ordem dela avisa o congelamento."""
    fund_match(page, stage="contributed")
    forge_president(page)
    open_funds_page(page)
    page.locator(CONTENT).get_by_role("heading", name=FUND_NAME).wait_for()
    cash_button(page).click()
    page.get_by_role("menuitem", name=re.compile(FUND_NAME)).click()
    page.get_by_text(f"{FUND_NAME} congelada até").wait_for()
    page.wait_for_load_state("networkidle")


def fund_premium_hint(page: Page) -> None:
    """A página da gestora com a dica do ágio aberta por hover."""
    fund_tab_page(page, "offer-closed", "Visão geral", "Quanto rendeu")
    page.get_by_role("button", name="O que é Preço de ranking").hover()
    page.locator('[data-slot="tooltip-content"]').wait_for()


# A identidade da gestora salva no perfil e a rota que grava a escolha da aba Gestora
SAVED_FUND_GLOB = "**/api/settings/fund"
FUND_PREPARATION_GLOB = "**/api/simulation/players/me/fund-preparation"


def lobby_fund_tab(
    page: Page,
    *,
    choice: str = "NONE",
    saved: dict | None = None,
    funds: bool = True,
) -> None:
    """
    Lobby com o diálogo "Minha preparação" na aba Gestora. Com `saved`, a identidade vai ao
    perfil e a escolha `FOUND` à sala, como o formulário faz; sem `saved`, o perfil responde
    vazio (dado forjado em `/api/settings/fund`) e a escolha `FOUND` é a da tela, que o botão
    "Fundar a minha gestora" muda. A aba abre sempre no mesmo ponto, qualquer que seja a
    rodada anterior.
    """
    lobby_with_professions(page, rules={"funds_enabled": funds})
    if funds and saved is not None:
        api_send(page, "PUT", "/api/settings/fund", saved)
    if funds:
        kind = "FOUND" if saved is not None else "NONE"
        api_send(
            page, "PUT", "/api/simulation/players/me/fund-preparation", {"kind": kind}
        )
    if saved is None:
        fulfill_get(page, SAVED_FUND_GLOB, "null")
    page.get_by_role("button", name="Minha preparação").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_role("tab", name=re.compile(r"^Gestora")).click()
    if funds and choice == "FOUND" and saved is None:
        dialog.get_by_role("button", name="Fundar a minha gestora", exact=True).click()
    page.wait_for_load_state("networkidle")


def lobby_fund_none(page: Page) -> None:
    """A aba Gestora de quem não fundou nem salvou nada: abre em "Sem gestora"."""
    lobby_fund_tab(page, choice="NONE")
    page.get_by_role("dialog").get_by_role("button", name="Sem gestora").wait_for()


def lobby_fund_blank(page: Page) -> None:
    """Fundar a minha gestora escolhido pela primeira vez: nome e sigla em branco."""
    lobby_fund_tab(page, choice="FOUND")
    page.get_by_role("dialog").get_by_label("Nome da gestora").wait_for()


def lobby_fund_filled(page: Page) -> None:
    """Fundar a minha gestora com a identidade salva no perfil: nome e sigla preenchidos."""
    lobby_fund_tab(page, saved={"name": FUND_NAME, "ticker": FUND_TICKER})
    expect(page.get_by_role("dialog").get_by_label("Nome da gestora")).to_have_value(
        FUND_NAME
    )


def lobby_fund_ticker_taken(page: Page) -> None:
    """A sigla digitada é a de um ativo da partida: a resposta aparece embaixo do campo."""
    lobby_fund_tab(page, choice="FOUND")
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Sigla da cota").fill("PETR")
    dialog.get_by_text("já é um ativo da partida").wait_for()


def lobby_fund_long_text(page: Page) -> None:
    """A identidade salva com o nome no limite de 40 letras."""
    lobby_fund_tab(page, saved={"name": LONG_FUND_NAME, "ticker": "FMPR11"})
    expect(page.get_by_role("dialog").get_by_label("Nome da gestora")).to_have_value(
        LONG_FUND_NAME
    )


def lobby_fund_disabled(page: Page) -> None:
    """A expansão Gestoras desligada nas regras da sala: a aba explica e aponta o host."""
    lobby_fund_tab(page, funds=False)
    page.get_by_text("Gestora só com a expansão Gestoras").wait_for()


def lobby_fund_loading(page: Page) -> None:
    """Dado forjado: a identidade salva nunca responde, e a aba fica em esqueleto."""
    lobby_with_professions(page, rules={"funds_enabled": True})
    hang_get(page, SAVED_FUND_GLOB)
    page.reload()
    page.get_by_role("button", name="Minha preparação").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_role("tab", name=re.compile(r"^Gestora")).click()
    dialog.locator('[aria-busy="true"]').first.wait_for()


def lobby_fund_save_failed(page: Page) -> None:
    """Dado forjado: o servidor recusa o salvamento da gestora, e o rodapé diz que nada se perdeu."""

    def refuse(route: Route) -> None:
        if route.request.method != "PUT":
            route.continue_()
            return
        route.fulfill(
            status=500,
            content_type="application/json",
            body='{"detail": "falha"}',
        )

    lobby_fund_tab(page, saved={"name": FUND_NAME, "ticker": FUND_TICKER})
    page.route(FUND_PREPARATION_GLOB, refuse)
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Nome da gestora").fill("Aurora Gestão Ltda")
    dialog.get_by_text("Nada se perdeu").wait_for()


def lobby_expansions(page: Page) -> None:
    """As regras da sala na aba Expansões, com o Governo e as Gestoras ligados."""
    lobby_with_professions(
        page,
        rules={"funds_enabled": True, "government_enabled": True} | GOVERNMENT_RULES,
    )
    page.get_by_role("button", name="Editar regras").click()
    page.get_by_role("tab", name=re.compile(r"^Expansões")).click()
    page.get_by_role("switch", name="Ligar Gestoras").wait_for()
    page.wait_for_load_state("networkidle")


# Os co-gestores: dado forjado sobre a gestora real do host, que nasce sem nenhum
COMANAGER_ACTIVE = {
    "nickname": "Duda",
    "color": "#8b5cf6",
    "share": "0.2",
    "pending_share": None,
    "pending_from": None,
    "invited_on": "2021-02-01",
    "since": "2021-02-03",
    "expires_on": None,
    "status": "ACTIVE",
}
COMANAGER_SCHEDULED = COMANAGER_ACTIVE | {
    "nickname": "Caio",
    "color": "#10b981",
    "share": "0.1",
    "pending_share": "0.15",
    "pending_from": "2021-04-01",
    "since": "2021-02-10",
}
COMANAGER_INVITED = {
    "nickname": "Bia",
    "color": "#f59e0b",
    "share": "0",
    "pending_share": "0.1",
    "pending_from": None,
    "invited_on": "2021-03-10",
    "since": None,
    "expires_on": "2021-03-17",
    "status": "INVITED",
}


def forge_comanagers(
    page: Page,
    comanagers: list[dict],
    *,
    role: str = "manager",
    host_is_comanager: bool = False,
) -> None:
    """
    Dado forjado: a página da gestora traz `comanagers` e o papel `role` do host. Com
    `host_is_comanager` a gestora passa a ser de outro jogador e a linha `comanagers[-1]`
    é a do host. A parte do principal é o que sobra das partes em vigor.
    """

    def change(body: dict | list) -> None:
        assert isinstance(body, dict)
        host_id = body["manager_user_id"]
        rows = [
            row
            | {
                "user_id": host_id
                if host_is_comanager and index == len(comanagers) - 1
                else 1000 + index
            }
            for index, row in enumerate(comanagers)
        ]
        if host_is_comanager:
            body["manager_user_id"] = OTHER_MANAGER_ID
            body["manager_nickname"] = "Rafa"
        body["comanagers"] = rows
        body["my_role"] = role
        body["manager_share"] = str(1 - sum(float(row["share"]) for row in rows))
        body["fees"]["management_monthly_estimate"] = "1666.67"

    patch_get(page, FUND_DETAIL_PATTERN, change)


def open_fund_forged(
    page: Page, heading: str | None = None, tab: str | None = None
) -> None:
    """A página da gestora do host depois de `forge_comanagers`, aberta pelo menu e, com `tab`, nessa aba."""
    open_funds_page(page)
    page.locator(CONTENT).get_by_role("heading", name=heading or FUND_NAME).wait_for()
    page.wait_for_load_state("networkidle")
    if tab:
        open_fund_tab(page, tab)


def comanagers_card(page: Page) -> None:
    """Dado forjado: o gestor com um co-gestor ativo, um com mudança de parte agendada e um convite pendente."""
    fund_match(page, stage="contributed")
    forge_comanagers(page, [COMANAGER_ACTIVE, COMANAGER_SCHEDULED, COMANAGER_INVITED])
    open_fund_forged(page, tab="Cotas")
    page.get_by_text("Passa a 15%").wait_for()


def comanagers_full(page: Page) -> None:
    """Dado forjado: três co-gestores, o limite, e o botão de convidar fica desabilitado."""
    fund_match(page, stage="contributed")
    forge_comanagers(
        page,
        [
            COMANAGER_ACTIVE,
            COMANAGER_SCHEDULED,
            COMANAGER_INVITED | {"nickname": "Léo"},
        ],
    )
    open_fund_forged(page, tab="Cotas")
    page.get_by_role("button", name="Convidar co-gestor").wait_for()


def comanager_invite_dialog(page: Page) -> None:
    """O diálogo de convidar um co-gestor, sem convidado escolhido."""
    fund_match(page, stage="contributed")
    forge_comanagers(page, [COMANAGER_ACTIVE])
    open_fund_forged(page, tab="Cotas")
    page.get_by_role("button", name="Convidar co-gestor").click()
    page.get_by_role("dialog").get_by_text(
        "Parte do co-gestor nas taxas"
    ).first.wait_for()


def comanager_share_dialog(page: Page) -> None:
    """O diálogo de mudar a parte de um co-gestor ativo."""
    fund_match(page, stage="contributed")
    forge_comanagers(page, [COMANAGER_ACTIVE, COMANAGER_SCHEDULED])
    open_fund_forged(page, tab="Cotas")
    page.get_by_role("button", name="Mudar parte").first.click()
    page.get_by_role("dialog").get_by_text(
        "Parte do co-gestor nas taxas"
    ).first.wait_for()


def comanager_remove_dialog(page: Page) -> None:
    """A confirmação de remover um co-gestor ativo."""
    fund_match(page, stage="contributed")
    forge_comanagers(page, [COMANAGER_ACTIVE])
    open_fund_forged(page, tab="Cotas")
    page.get_by_role("button", name="Remover").first.click()
    page.get_by_role("alertdialog").wait_for()


def comanager_view(page: Page) -> None:
    """Dado forjado: a gestora é de outro jogador e o host é co-gestor dela: opera a carteira e pode sair."""
    fund_match(page, stage="contributed")
    forge_comanagers(
        page,
        [COMANAGER_ACTIVE | {"nickname": demo_settings()["host"]["nickname"]}],
        role="comanager",
        host_is_comanager=True,
    )
    open_fund_forged(page)
    page.get_by_role("button", name="Sair da gestão").wait_for()


def comanager_invite_received(page: Page) -> None:
    """Dado forjado: o host recebe o convite para co-gestor de uma gestora de outro jogador."""
    fund_match(page, stage="contributed")
    forge_comanagers(
        page,
        [COMANAGER_INVITED | {"nickname": demo_settings()["host"]["nickname"]}],
        role="viewer",
        host_is_comanager=True,
    )
    open_fund_forged(page)
    page.get_by_role("button", name="Aceitar").wait_for()


def stock_fund_quota(page: Page) -> None:
    """
    Detalhe da cota AURO11 de uma gestora já listada, depois da oferta pública encerrada, com a
    expansão Gestoras ligada: o livro, a boleta com o bloco da cota e o card "Sobre a gestora".
    """
    fund_match(page, stage="offer-closed")
    page.goto(f"/variable-income/{FUND_TICKER}")
    page.get_by_role("heading", name=re.compile(FUND_TICKER)).first.wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


def funds_room_list(page: Page) -> None:
    """
    Gestoras de quem ainda não fundou, com a lista da sala: a gestora listada aparece como de
    outro jogador. Dado forjado: o dono da primeira gestora da lista vira a Duda, para o host
    não ter gestora na página e ver o convite para fundar.
    """
    fund_match(page, stage="offer-closed")

    def change(body: dict | list) -> None:
        assert isinstance(body, list)
        body[0]["manager_user_id"] = OTHER_MANAGER_ID
        body[0]["manager_nickname"] = "Duda"

    patch_get(page, FUNDS_LIST_PATTERN, change)
    open_funds_page(page)
    page.get_by_role("heading", name="Funde a sua gestora").wait_for()
    page.get_by_text("Gestoras da sala").wait_for()
    page.wait_for_load_state("networkidle")


def state_owned_tickers(page: Page) -> set[str]:
    """Os ativos que são estatais na partida aberta, como a lista da renda variável os marca."""
    quotes = api_json(page, "/api/variable-income")
    return {quote["ticker"] for quote in quotes if quote["state_owned"]}


def mark_state_company(page: Page, ticker: str) -> None:
    """Marca o ativo como estatal pela API de importação; a marcação vale para as partidas criadas depois."""
    api_send(
        page,
        "PUT",
        f"/api/import-assets/stocks/{ticker}/state",
        {
            "government_share": STATE_COMPANY_GOVERNMENT_SHARE,
            "shares": STATE_COMPANY_SHARES,
            "lever": None,
        },
    )


def stock_state_owned(page: Page) -> None:
    """
    Detalhe da PETR4 numa partida com o governo ligado e a PETR4 estatal. A boleta recebe uma
    quantidade de 100 para mostrar a conta da ordem; o selo "Estatal" aparece na lista de ativos,
    não no detalhe.
    """
    fund_match(page, funds=False, government=True, state_company=True)
    sidebar(page, "Renda variável").click()
    page.get_by_role("row", name=re.compile(rf"^{STATE_COMPANY_TICKER}")).click()
    page.get_by_role("heading", name=re.compile(STATE_COMPANY_TICKER)).first.wait_for()
    page.locator("#order-size").fill("100")
    expect(page.get_by_text("Conferindo a ordem…")).to_be_hidden()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


STATE_COMPANY_GLOB = f"**/api/variable-income/{STATE_COMPANY_TICKER}/state-company"


def founded_state_company(body: dict | list) -> None:
    """
    Dado forjado: a estatal da tela vem fundada pelo governo há oito meses, com o histórico
    completo. A partida da receita não fecha meses, e a importada chega sem histórico.
    """
    assert isinstance(body, dict)
    months = []
    for index in range(8):
        loss = index == 5
        first = index == 0
        months.append(
            {
                "month": f"2026-{index + 3:02d}-01",
                "reason": "FOUNDING" if first else "LOSS" if loss else "PAID",
                "price": f"{24.0 + index * 0.35:.2f}",
                "fair_value": f"{24.6 + index * 0.1:.2f}",
                "profit": None
                if first
                else "-0.40"
                if loss
                else f"{1.6 + index * 0.05:.2f}",
                "dividend": None if first or loss else f"{0.8 + index * 0.04:.2f}",
                "dividend_policy": None if first else "NORMAL",
                "payout": None if first or loss else "0.50",
            }
        )
    body |= {
        "origin": "FOUNDED",
        "status": "ACTIVE",
        "founded_on": "2026-03-01",
        "size": "MEDIUM",
        "government_share": "0.60",
        "price": "26.80",
        "fair_value": "25.10",
        "dividends": "0.87",
        "dividend_policy": "NORMAL",
        "policies": [
            {"dividend_policy": "REINVEST", "payout": "0.25"},
            {"dividend_policy": "NORMAL", "payout": "0.50"},
            {"dividend_policy": "SQUEEZE", "payout": "0.80"},
        ],
        "beta": "0.8",
        "months": months,
        "holders": {
            "government": "7800000000",
            "maker": "2600000000",
            "players": "1300000000",
            "bots": "1300000000",
            "funds": "0",
            "you": "0",
        },
    }


def stock_state_company_detail(page: Page) -> None:
    """
    Detalhe da estatal fundada: o cabeçalho com a origem, os cinco números, os gráficos, o
    mês a mês, quem tem as ações e a política de dividendos. O dado da estatal é forjado sobre
    a resposta real, porque a partida da receita não tem meses fechados.
    """
    fund_match(page, funds=False, government=True, state_company=True)
    patch_get(page, STATE_COMPANY_GLOB, founded_state_company)
    sidebar(page, "Renda variável").click()
    page.get_by_role("row", name=re.compile(rf"^{STATE_COMPANY_TICKER}")).click()
    page.get_by_role("heading", name=re.compile(STATE_COMPANY_TICKER)).first.wait_for()
    page.get_by_text("Mês a mês").wait_for()
    page.wait_for_load_state("networkidle")
    dismiss_topic(page)


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
    "topbar/padrao": topbar_default,
    "topbar/padrao-1366": topbar_1366,
    "topbar/pausado": topbar_paused,
    "topbar/dica-tracinho": topbar_pip_hint,
    "topbar/menu-aberto": topbar_menu_open,
    "topbar/operando-gestora": topbar_operating_fund,
    "topbar/governa-dica": topbar_governing_hint,
    "topbar/governa-menu": topbar_governing_menu,
    "topbar/cheque-especial": topbar_overdraft,
    "topbar/nome-longo-1366": topbar_long_fund_name,
    "topbar/classica": topbar_classic,
    "topbar/carregando": topbar_loading,
    "gestoras/sem-gestora": funds_none,
    "gestoras/fundada-vazia": funds_founded,
    "gestoras/fechada": funds_closed,
    "gestoras/oferta-aberta": funds_offer_open,
    "gestoras/oferta-encerrada": funds_offer_closed,
    "gestoras/rendimentos-longos": funds_long_distributions,
    "gestoras/carregando": funds_loading,
    "gestoras/erro": funds_error,
    "gestoras/texto-longo": funds_long_text,
    "gestoras/cotista": funds_viewer,
    "gestoras/lista-blocos": room_blocks,
    "gestoras/lista-presidente": room_president,
    "gestoras/lista-duas-geridas": room_two_held,
    "gestoras/fundar": found_fund_open,
    "gestoras/fundar-preenchida": found_fund_filled,
    "gestoras/fundar-sigla-recusada": found_fund_ticker_taken,
    "gestoras/dialogo-oferta": dialog_offer,
    "gestoras/dialogo-oferta-grande": dialog_offer_too_big,
    "gestoras/dialogo-levar": dialog_contribute,
    "gestoras/dialogo-taxas": dialog_fees,
    "gestoras/conta-da-gestora": fund_account_stock,
    "gestoras/gestor-vendendo": fund_selling,
    "gestoras/gestor-governa": fund_governing,
    "gestoras/painel-congelado": fund_frozen_panel,
    "gestoras/dica-agio": fund_premium_hint,
    "gestoras/aba-acoes": tab_actions,
    "gestoras/aba-acoes-fechada": tab_actions_closed,
    "gestoras/aba-acoes-cotista": tab_actions_holder,
    "gestoras/aba-geral": tab_overview,
    "gestoras/aba-geral-fechada": tab_overview_closed,
    "gestoras/aba-carteira": tab_portfolio,
    "gestoras/aba-carteira-congelada": tab_portfolio_frozen,
    "gestoras/aba-cotas": tab_quotas,
    "gestoras/aba-rendimentos": tab_income,
    "gestoras/aba-relatorio": tab_report,
    "gestoras/aba-config": tab_settings,
    "gestoras/aba-assembleia": tab_assembly,
    "gestoras/aba-assembleia-taxa": tab_assembly_fee,
    "gestoras/aba-assembleia-vazia": tab_assembly_empty,
    "gestoras/co-gestores": comanagers_card,
    "gestoras/co-gestores-cheio": comanagers_full,
    "gestoras/dialogo-convidar-co-gestor": comanager_invite_dialog,
    "gestoras/dialogo-parte-co-gestor": comanager_share_dialog,
    "gestoras/dialogo-remover-co-gestor": comanager_remove_dialog,
    "gestoras/co-gestor-opera": comanager_view,
    "gestoras/convite-co-gestor": comanager_invite_received,
    "lobby-gestora/sem-gestora": lobby_fund_none,
    "lobby-gestora/fundar-vazia": lobby_fund_blank,
    "lobby-gestora/fundar-preenchida": lobby_fund_filled,
    "lobby-gestora/sigla-recusada": lobby_fund_ticker_taken,
    "lobby-gestora/texto-longo": lobby_fund_long_text,
    "lobby-gestora/expansao-desligada": lobby_fund_disabled,
    "lobby-gestora/carregando": lobby_fund_loading,
    "lobby-gestora/erro-ao-salvar": lobby_fund_save_failed,
    "regras/expansoes": lobby_expansions,
    "renda-variavel/cota-gestora": stock_fund_quota,
    "gestoras/sem-gestora-lista": funds_room_list,
    "renda-variavel/estatal": stock_state_owned,
    "estatal/detalhe": stock_state_company_detail,
}
