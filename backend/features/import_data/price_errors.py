import math

import numpy as np
import pandas as pd

# Distância máxima do fechamento à âncora (último fechamento bom) para o dia contar como bom
ERROR_THRESHOLD = 0.5
# Pregões que o preço tem para voltar ao nível da âncora; depois disso o salto é mercado
MAX_RECOVERY_DAYS = 5


def fix_price_errors(
    df: pd.DataFrame,
    anchor_close: float | None = None,
    threshold: float = ERROR_THRESHOLD,
    max_recovery_days: int = MAX_RECOVERY_DAYS,
) -> tuple[pd.DataFrame, list[pd.Timestamp]]:
    """
    Troca por interpolação os dias em que a fonte errou o preço, e devolve o
    DataFrame corrigido com as datas trocadas.

    Um dia é erro quando o fechamento se afasta da âncora além do `threshold` e, em
    até `max_recovery_days` pregões, o preço volta para dentro dele. O trecho entre a
    âncora e o primeiro dia bom que volta ganha o fechamento em linha reta entre os
    dois; abertura, máxima e mínima recebem o mesmo valor e o volume zera, para o dia
    não desenhar uma vela falsa. Salto que não volta (desdobramento, quebra real) e
    trecho no fim da série, sem dia bom depois, ficam como vieram.

    `anchor_close` é o último fechamento bom guardado antes de `df`; sem ele, a
    âncora nasce do primeiro fechamento válido.
    """
    if df.empty:
        return df, []

    closes = df["Close"].to_numpy(dtype=float)
    runs = _error_runs(closes, anchor_close, threshold, max_recovery_days)
    if not runs:
        return df, []

    fixed = df.copy()
    corrected: list[pd.Timestamp] = []
    for start, end, before in runs:
        span = end - start + 1
        for offset, position in enumerate(range(start, end), start=1):
            value = before + (closes[end] - before) * offset / span
            for column in ("Open", "High", "Low", "Close"):
                fixed.iat[position, fixed.columns.get_loc(column)] = value
            fixed.iat[position, fixed.columns.get_loc("Volume")] = 0
            corrected.append(df.index[position])
    return fixed, corrected


def _error_runs(
    closes: np.ndarray,
    anchor_close: float | None,
    threshold: float,
    max_recovery_days: int,
) -> list[tuple[int, int, float]]:
    """Trechos `[início, fim)` de erro com a âncora que os antecede; `fim` é o primeiro
    dia bom que a âncora reencontra."""
    runs: list[tuple[int, int, float]] = []
    ref = anchor_close
    i = 0
    while i < len(closes):
        close = closes[i]
        if ref is None:
            ref = close if _is_valid(close) else None
            i += 1
            continue
        if _is_near(close, ref, threshold):
            ref = close
            i += 1
            continue
        last = min(i + max_recovery_days, len(closes) - 1)
        back = next(
            (k for k in range(i + 1, last + 1) if _is_near(closes[k], ref, threshold)),
            None,
        )
        if back is None:
            # Sem retorno: o nível novo passa a ser a referência
            if _is_valid(close):
                ref = close
            i += 1
            continue
        runs.append((i, back, ref))
        ref = closes[back]
        i = back + 1
    return runs


def _is_valid(close: float) -> bool:
    return math.isfinite(close) and close > 0


def _is_near(close: float, ref: float, threshold: float) -> bool:
    return _is_valid(close) and abs(close / ref - 1) <= threshold
