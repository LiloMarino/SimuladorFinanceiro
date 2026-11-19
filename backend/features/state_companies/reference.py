"""Desvio do preço da estatal fundada em volta do valor justo: a bolsa da partida mais um ruído próprio, que volta ao valor justo com o tempo."""

import math
import random
from collections.abc import Callable, Sequence
from datetime import date

# Quanto do retorno diário do Ibovespa da partida (em log) a ação acompanha
MARKET_BETA = 0.8

# Desvio-padrão do ruído próprio da ação, em log por pregão
NOISE_VOLATILITY = 0.012

# Pregões para o desvio inteiro (bolsa e ruído) cair pela metade
HALF_LIFE_SESSIONS = 30

# Fração do desvio que sobra de um pregão para o seguinte: a raiz 30 de 1/2
PERSISTENCE = 0.5 ** (1 / HALF_LIFE_SESSIONS)

# O ruído do pregão: gaussiano de média 0, semeado por (semente, dia)
type Noise = Callable[[int, date], float]


def seeded_noise(seed: int, day: date) -> float:
    """O ruído do dia: o mesmo (seed, day) dá sempre o mesmo valor."""
    return random.Random(f"{seed}:{day.isoformat()}").gauss(0.0, NOISE_VOLATILITY)


def no_noise(_seed: int, _day: date) -> float:
    return 0.0


def next_deviation(previous: float, market_return: float, noise: float) -> float:
    """O desvio em log do pregão: a parte que persiste do anterior, o beta vezes o retorno da bolsa e o ruído."""
    return PERSISTENCE * previous + MARKET_BETA * market_return + noise


def deviation_path(
    returns: Sequence[tuple[date, float]],
    seed: int,
    *,
    initial: float = 0.0,
    noise: Noise = seeded_noise,
) -> list[float]:
    """
    O desvio em log de cada pregão de `returns` (dia, retorno em log do Ibovespa da
    partida contra o pregão anterior), em ordem. O desvio parte de `initial` (0 na
    fundação, onde o preço é o valor justo). O resultado depende só da série, da semente e
    do ruído: o mesmo pregão dá o mesmo desvio ao vivo e depois de recarregar a partida.
    """
    path: list[float] = []
    current = initial
    for day, market_return in returns:
        current = next_deviation(current, market_return, noise(seed, day))
        path.append(current)
    return path


def log_return(previous: float, current: float) -> float:
    """O retorno em log entre dois níveis; 0 quando o anterior não vale."""
    if previous <= 0 or current <= 0:
        return 0.0
    return math.log(current / previous)
