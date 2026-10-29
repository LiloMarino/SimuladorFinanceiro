"""Texto das manchetes: números em português e a variação de frase que o sorteio escolhe."""

import re
from decimal import ROUND_HALF_UP, Decimal
from random import Random

MONTH_NAMES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

# Sufixos de razão social que a manchete dispensa: "WEG S.A." vira "WEG"
_LEGAL_SUFFIX = re.compile(r"[\s,.-]+(S\.?\s?/?\s?A\.?|SA|S/A|LTDA\.?|N\.?V\.?)$", re.I)
MAX_NAME_LENGTH = 22


def number(value: Decimal | float, places: int = 2) -> str:
    """Número em português com até `places` casas, sem zeros à direita: 0,5 e 14,25."""
    exact = Decimal(str(value)).quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)
    text = f"{exact:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def grouped(value: Decimal | float) -> str:
    """Inteiro com ponto de milhar: 134.567."""
    return f"{round(value):,}".replace(",", ".")


def price(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def short_name(name: str, ticker: str) -> str:
    """O nome da empresa como a manchete o diz; nome longo demais vira o ticker."""
    trimmed = _LEGAL_SUFFIX.sub("", name.strip())
    return trimmed if 0 < len(trimmed) <= MAX_NAME_LENGTH else ticker


def pick[T](options: tuple[T, ...], *seed: object) -> T:
    """
    Uma variação de frase escolhida pela semente: o mesmo fato na mesma partida sai com
    a mesma frase, e fatos diferentes se espalham pelas variações.
    """
    return options[Random(":".join(str(part) for part in seed)).randrange(len(options))]
