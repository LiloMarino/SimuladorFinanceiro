"""
Grava a demonstração do app: screenshots e um GIF por cena, em `docs/static/demo/`.

Uso:
    pnpm demo                    # builda o front, grava e exporta
    pnpm demo --skip-build       # usa o front já buildado em backend/static
    pnpm demo publish            # publica docs/static/demo no branch `demo`
    pnpm demo fetch-data         # baixa de novo as cotações fixas (muda as imagens)

Pede o ffmpeg no PATH, `POSTGRES_DEMO_DATABASE_URL` no .env e, uma vez,
`uv run playwright install chromium`.

As imagens moram no branch `demo`, que guarda só a última publicação: o `main` não
acumula binários a cada regravação. O deploy dos docs as busca de lá.
"""

import argparse
import json
import os
import shutil
import subprocess
import time

from playwright.sync_api import APIRequestContext, Playwright, Route, sync_playwright

from backend.core.enum import IndicatorSeries
from backend.core.utils import PROJECT_ROOT
from scripts.demo.data import DATA_DIR, STOCKS, fetch_data
from scripts.demo.director import DEVICE_SCALE, VIEWPORT, Director
from scripts.demo.render import make_gif, render_scene
from scripts.demo.script import run
from scripts.demo.server import (
    DEMO_DIR,
    base_database_url,
    build_frontend,
    demo_server,
    recording_database,
)

WORK_DIR = PROJECT_ROOT / "build" / "demo"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "static" / "demo"
# O link de convite mostra o IP da máquina que grava; nas imagens vai um da rede local
INVITE_URL = "http://192.168.0.10:8000"
INDICATOR_ATTEMPTS = 5
PUBLISH_BRANCH = "demo"
DOCS_WORKFLOW = "deploy-docs.yml"


def seed(playwright: Playwright, base_url: str) -> None:
    """
    Prepara o banco-base. As cotações entram sempre, porque os CSVs são a fonte; os
    indicadores, só as séries que ainda não estão lá.
    """
    api = playwright.request.new_context(base_url=base_url)
    for ticker, (sector, segment) in STOCKS.items():
        csv = DATA_DIR / f"{ticker}.csv"
        response = api.post(
            "/api/import-assets/csv",
            multipart={
                "ticker": ticker,
                "overwrite": "true",
                "csv_file": {
                    "name": csv.name,
                    "mimeType": "text/csv",
                    "buffer": csv.read_bytes(),
                },
            },
        )
        if not response.ok:
            raise RuntimeError(f"Importação de {ticker} falhou: {response.text()}")
        response = api.put(
            f"/api/import-assets/stocks/{ticker}/segment",
            data={"sector": sector, "segment": segment},
        )
        if not response.ok:
            raise RuntimeError(f"Classificação de {ticker} falhou: {response.text()}")
    for series in missing_indicators(api):
        fetch_indicator(api, series)
    api.dispose()


def missing_indicators(api: APIRequestContext) -> list[str]:
    coverage = api.get("/api/import-assets/coverage").json()
    present = {
        item["key"]
        for item in coverage
        if item["kind"] == "INDICATOR" and item["start"] is not None
    }
    return [series.value for series in IndicatorSeries if series.value not in present]


def fetch_indicator(api: APIRequestContext, series: str) -> None:
    """O Banco Central às vezes responde 502; a nova tentativa pede a série de novo."""
    for attempt in range(1, INDICATOR_ATTEMPTS + 1):
        response = api.post(f"/api/import-assets/indicators/{series}", timeout=180_000)
        if response.ok:
            return
        print(f"{series}, tentativa {attempt}: {response.text()}")
        time.sleep(5)
    raise RuntimeError(
        f"{series} não veio da fonte depois de {INDICATOR_ATTEMPTS} tentativas."
    )


def mask_invite(route: Route) -> None:
    response = route.fetch()
    status = response.json()
    if status.get("url"):
        status["url"] = INVITE_URL
    route.fulfill(response=response, body=json.dumps(status))


def record() -> Director:
    shutil.rmtree(WORK_DIR / "frames", ignore_errors=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    with sync_playwright() as playwright:
        with demo_server(WORK_DIR, base_database_url()) as app_url:
            seed(playwright, app_url)
        with (
            recording_database() as database_url,
            demo_server(WORK_DIR, database_url) as app_url,
        ):
            return film(playwright, app_url)


def film(playwright: Playwright, app_url: str) -> Director:
    """Joga a partida do roteiro num navegador gravado pelo screencast."""
    browser = playwright.chromium.launch()
    context = browser.new_context(
        viewport={"width": int(VIEWPORT.width), "height": int(VIEWPORT.height)},
        device_scale_factor=DEVICE_SCALE,
        locale="pt-BR",
        color_scheme="light",
    )
    context.add_init_script(path=DEMO_DIR / "cursor.js")
    context.route("**/api/tunnel/status", mask_invite)
    page = context.new_page()
    director = Director(
        page,
        context.new_cdp_session(page),
        WORK_DIR / "frames",
        OUTPUT_DIR / "screens",
    )
    page.goto(f"{app_url}/login")
    page.wait_for_load_state("networkidle")
    director.start_recording()
    try:
        run(director, page)
    except Exception:
        page.screenshot(path=WORK_DIR / "failure.png")
        print(f"A tela no momento da falha: {WORK_DIR / 'failure.png'}")
        raise
    finally:
        director.stop_recording()
        browser.close()
    return director


def export(director: Director) -> None:
    """O MP4 de cada cena é o intermediário do GIF e fica na pasta de trabalho."""
    clips, gifs = WORK_DIR / "clips", OUTPUT_DIR / "gifs"
    clips.mkdir(parents=True, exist_ok=True)
    gifs.mkdir(parents=True, exist_ok=True)
    for scene in director.scenes:
        clip = clips / f"{scene.name}.mp4"
        print(f"Exportando {scene.name} ({scene.end - scene.start:.0f} s)")
        render_scene(director.frames, scene, clip)
        make_gif(clip, gifs / f"{scene.name}.gif")


def git(*args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def publish() -> None:
    """
    Troca o conteúdo do branch `demo` por `docs/static/demo/`, num commit sem pai: o
    branch nunca tem mais que a última publicação. O índice é um arquivo próprio, então
    o que está em andamento no `main` fica intocado. Depois, dispara o deploy dos docs.
    """
    if not any(OUTPUT_DIR.rglob("*.gif")):
        raise RuntimeError(f"Nada para publicar em {OUTPUT_DIR}: rode `pnpm demo`.")
    index = WORK_DIR / "publish-index"
    index.unlink(missing_ok=True)
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    git("--work-tree", str(OUTPUT_DIR), "add", "--all", env=env)
    tree = git("write-tree", env=env)
    commit = git(
        "commit-tree", tree, "-m", "docs: Atualizadas as imagens da demonstração"
    )
    git("push", "--force", "origin", f"{commit}:refs/heads/{PUBLISH_BRANCH}")
    subprocess.run(
        ["gh", "workflow", "run", DOCS_WORKFLOW, "--ref", "main"], check=True
    )
    print(f"Publicado no branch {PUBLISH_BRANCH}; deploy dos docs disparado.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="pnpm demo", description=__doc__)
    parser.add_argument(
        "command", nargs="?", choices=["record", "publish", "fetch-data"]
    )
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    if args.command == "fetch-data":
        fetch_data()
        return
    if args.command == "publish":
        publish()
        return
    if not args.skip_build:
        build_frontend()
    export(record())
    shutil.rmtree(WORK_DIR / "frames", ignore_errors=True)
    print(f"Demonstração gravada em {OUTPUT_DIR}; publique com `pnpm demo publish`.")


if __name__ == "__main__":
    main()
