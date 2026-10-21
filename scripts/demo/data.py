"""
Cotações fixas da demonstração, baixadas do yfinance uma vez e versionadas em `data/`.

A gravação importa estes CSVs em vez de buscar na rede, para sair igual toda vez.
Refazer o download (`pnpm demo fetch-data`) muda o que aparece
nos vídeos e nas imagens.
"""

import csv
from pathlib import Path

from backend.features.import_data.importer_service import from_yfinance

DATA_DIR = Path(__file__).parent / "data"
# Setor e segmento da classificação da B3: a importação por CSV chega sem eles
STOCKS = {
    "PETR4": ("Petróleo, Gás e Biocombustíveis", "Exploração, Refino e Distribuição"),
    "VALE3": ("Materiais Básicos", "Minerais Metálicos"),
    "ITUB4": ("Financeiro", "Bancos"),
    "WEGE3": ("Bens Industriais", "Motores, Compressores e Outros"),
    "BBAS3": ("Financeiro", "Bancos"),
}
START, END = "2021-01-01", "2026-01-01"


def brazilian_decimal(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def write_csv(ticker: str) -> Path:
    """Grava no formato que a importação por CSV lê (`importer_service.from_csv`)."""
    frame = from_yfinance(f"{ticker}.SA", START, END)
    path = DATA_DIR / f"{ticker}.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(["Data", "Último", "Abertura", "Máxima", "Mínima", "Vol."])
        newest_first = frame.sort_index(ascending=False)
        prices = [newest_first[c].tolist() for c in ("Close", "Open", "High", "Low")]
        for day, *quote, volume in zip(
            newest_first.index, *prices, newest_first["Volume"].tolist(), strict=True
        ):
            writer.writerow(
                [
                    day.strftime("%d.%m.%Y"),
                    *(brazilian_decimal(value) for value in quote),
                    str(int(volume)),
                ]
            )
    return path


def fetch_data() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for ticker in STOCKS:
        print(f"{ticker}: {write_csv(ticker)}")
