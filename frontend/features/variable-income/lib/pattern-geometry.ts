import type { DrawnCandle } from "./candle-patterns";

export const DRAWING_WIDTH = 64;
export const DRAWING_HEIGHT = 62;
export const CANDLE_WIDTH = 10;

const TOP = 6;
const BOTTOM = 56;
const SLOT = 18;

/** Preço do desenho (0 embaixo, 100 no alto) para a altura no quadro. */
const toY = (price: number) => BOTTOM - ((BOTTOM - TOP) * price) / 100;

export interface CandleBox {
  /** Centro horizontal da vela. */
  x: number;
  bodyTop: number;
  bodyHeight: number;
  wickTop: number;
  wickBottom: number;
  bullish: boolean;
}

/** Onde cada vela do padrão cai no quadro, centradas em fila. */
export function candleBoxes(candles: DrawnCandle[]): CandleBox[] {
  const first = DRAWING_WIDTH / 2 - ((candles.length - 1) * SLOT) / 2;
  return candles.map((candle, index) => {
    const top = toY(Math.max(candle.open, candle.close));
    const bottom = toY(Math.min(candle.open, candle.close));
    return {
      x: first + index * SLOT,
      bodyTop: top,
      bodyHeight: Math.max(bottom - top, 1.5),
      wickTop: toY(candle.high),
      wickBottom: toY(candle.low),
      bullish: candle.close >= candle.open,
    };
  });
}

/** A cor da vela no tema: a de alta e a de baixa do gráfico. */
export const candleColor = (bullish: boolean) => (bullish ? "var(--candle-up)" : "var(--candle-down)");
