"""
O roteiro da demonstração: uma partida do lobby ao resultado, cena por cena.

Cada cena vira um MP4 e um GIF com o nome dela; as screenshots saem nos momentos em
que a tela mostra algo que as páginas de "Como usar" querem ilustrar.
"""

import re

from playwright.sync_api import Page

from scripts.demo.director import Director
from scripts.demo.server import demo_settings


def sidebar(page: Page, name: str):
    return page.get_by_role("link", name=name, exact=True)


def run(director: Director, page: Page) -> None:
    with director.scene("lobby"):
        director.fill(
            page.get_by_label("Seu nickname"), demo_settings()["host"]["nickname"]
        )
        director.click(page.get_by_role("button", name="Entrar"))
        page.wait_for_url("**/lobby")
        director.wait(1.5)
        director.shot("lobby")
        director.click(page.get_by_role("button", name="Iniciar nova simulação"))
        page.get_by_role("heading", name="Carteira").wait_for()
        director.wait(1.0)

    with director.scene("stocks"):
        director.click(sidebar(page, "Renda variável"))
        page.get_by_role("row", name=re.compile(r"^PETR4")).wait_for()
        director.wait(1.0)
        director.shot("stocks")
        director.click(page.get_by_role("row", name=re.compile(r"^PETR4")))
        page.get_by_label("Quantidade").wait_for()
        director.wait(1.2)
        director.fill(page.get_by_label("Quantidade"), "300")
        director.wait(0.6)
        director.shot("stock-order")
        director.click(
            page.get_by_role("button", name=re.compile(r"^Comprar \d+ PETR4"))
        )
        director.wait(1.5)

    with director.scene("fixed-income"):
        director.click(sidebar(page, "Renda fixa"))
        bond = page.get_by_role("row", name=re.compile(r"^Tesouro")).first
        bond.wait_for()
        director.wait(1.0)
        director.shot("fixed-income")
        director.click(bond.get_by_role("button", name="Investir"))
        page.get_by_label("Quanto investir").wait_for()
        director.wait(1.2)
        # O campo de dinheiro lê os dígitos como centavos
        director.fill(page.get_by_label("Quanto investir"), "300000")
        director.wait(0.6)
        director.shot("fixed-income-bond")
        director.click(page.get_by_role("button", name=re.compile(r"^Investir R\$")))
        director.wait(1.5)

    with director.scene("time"):
        director.click(sidebar(page, "Carteira"))
        director.wait(1.0)
        director.click(page.get_by_role("button", name="100×"))  # noqa: RUF001
        # A velocidade já retoma a partida; a carteira anda num plano aberto
        director.wait(7.0)
        director.click(page.get_by_role("button", name="Pausar simulação"))
        director.wait(1.0)
        director.shot("portfolio")

    with director.scene("statistics"):
        director.click(sidebar(page, "Estatísticas"))
        page.get_by_role("tab", name="Geral").wait_for()
        director.wait(1.5)
        director.shot("statistics")
        director.click(page.get_by_role("tab", name="Rentabilidade"))
        director.wait(2.0)
        director.click(page.get_by_role("tab", name="Risco"))
        director.wait(2.0)

    with director.scene("closing"):
        director.click(sidebar(page, "Configurações"))
        director.click(page.get_by_role("button", name="Encerrar partida"))
        director.click(
            page.get_by_role("alertdialog").get_by_role(
                "button", name="Encerrar partida"
            )
        )
        page.wait_for_url("**/match-result/**")
        director.wait(2.5)
        director.shot("match-result")
