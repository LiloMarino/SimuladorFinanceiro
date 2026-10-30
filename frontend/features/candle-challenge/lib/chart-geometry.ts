import type { ChallengeBar } from "@/types";

/** Velas que o jogador vê e lugares reservados para as 5 que entram na revelação. */
export const SHOWN_CANDLES = 30;
export const HIDDEN_CANDLES = 5;

export interface ChartBox {
  width: number;
  height: number;
}

const PAD = { top: 14, right: 12, bottom: 14, left: 52 };

/** Folga acima da máxima e abaixo da mínima, em fração da amplitude. */
const MARGIN = 0.1;

export interface Scale {
  /** Da posição vertical em % para y no desenho. */
  y: (value: number) => number;
  /** Do índice da vela (0 a 34) para o x do centro dela. */
  x: (index: number) => number;
  step: number;
  min: number;
  max: number;
}

/** A escala do eixo em % que cobre as velas da pergunta e, na revelação, as que entraram depois. */
export function chartScale(bars: ChallengeBar[], box: ChartBox): Scale {
  const values = bars.flatMap((bar) => [bar.high, bar.low]);
  const low = Math.min(...values);
  const high = Math.max(...values);
  const span = high - low || 1;
  const min = low - span * MARGIN;
  const max = high + span * MARGIN;
  const inner = { width: box.width - PAD.left - PAD.right, height: box.height - PAD.top - PAD.bottom };
  const step = inner.width / (SHOWN_CANDLES + HIDDEN_CANDLES);
  return {
    y: (value) => PAD.top + ((max - value) / (max - min)) * inner.height,
    x: (index) => PAD.left + step * (index + 0.5),
    step,
    min,
    max,
  };
}

/** Marcas do eixo em % em passos redondos (1, 2, 5 × 10ⁿ), dentro de [min, max]. */
export function axisTicks(min: number, max: number, wanted = 5): number[] {
  const raw = (max - min) / wanted;
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * magnitude).find((candidate) => candidate >= raw) ?? raw;
  const ticks: number[] = [];
  for (let tick = Math.ceil(min / step) * step; tick <= max; tick += step) {
    ticks.push(Math.round(tick / step) * step);
  }
  return ticks;
}

export function displayTick(value: number) {
  const rounded = Number.isInteger(value) ? value : Number(value.toFixed(1));
  return `${rounded > 0 ? "+" : ""}${rounded.toString().replace(".", ",")}%`;
}

export const chartPadding = PAD;
