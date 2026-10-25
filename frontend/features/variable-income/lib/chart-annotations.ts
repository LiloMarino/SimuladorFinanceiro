import type { SeriesMarker, Time } from "lightweight-charts";
import type { CandlePattern } from "@/types";
import type { OverlayShape } from "./chart-overlay";
import { PATTERN_INFO } from "./candle-patterns";
import { crossovers, type SeriesPoint } from "./crossovers";

/** As cores do tema que as anotações usam, lidas uma vez do documento. */
export interface AnnotationColors {
  up: string;
  down: string;
  neutral: string;
  band: string;
}

/** Quantos pregões depois do padrão o desfecho é conferido. */
export const OUTCOME_SESSIONS = 5;

/** Um rótulo por padrão sobre a vela em que ele termina: verde embaixo (alta), vermelho em cima (baixa), cinza no doji. */
export function patternMarkers(patterns: CandlePattern[], colors: AnnotationColors): SeriesMarker<Time>[] {
  return patterns.map((pattern) => ({
    time: pattern.end as Time,
    position: pattern.direction === "up" ? "belowBar" : "aboveBar",
    shape: pattern.direction === "up" ? "arrowUp" : pattern.direction === "down" ? "arrowDown" : "circle",
    color: pattern.direction === "up" ? colors.up : pattern.direction === "down" ? colors.down : colors.neutral,
    text: PATTERN_INFO[pattern.code].name,
    size: 1,
  }));
}

/**
 * A faixa atrás de cada padrão de várias velas e, no padrão em foco, o contorno dos
 * 5 pregões que vêm depois dele. `days` são os pregões do histórico, em ordem.
 */
export function patternShapes(
  patterns: CandlePattern[],
  active: CandlePattern | undefined,
  days: string[],
  colors: AnnotationColors,
): OverlayShape[] {
  const shapes: OverlayShape[] = patterns
    .filter((pattern) => pattern.start !== pattern.end)
    .map((pattern) => ({ kind: "band", from: pattern.start, to: pattern.end, color: colors.band }));

  if (active) {
    const after = days.slice(days.indexOf(active.end) + 1, days.indexOf(active.end) + 1 + OUTCOME_SESSIONS);
    if (after.length > 0) {
      const color = active.direction === "down" ? colors.down : active.direction === "up" ? colors.up : colors.neutral;
      shapes.push({ kind: "outline", from: after[0], to: after[after.length - 1], color });
    }
  }
  return shapes;
}

/** As legendas dos níveis do IFR, fora da zona neutra: o que sobrecomprado e sobrevendido querem dizer. */
export function rsiShapes(overbought: number, oversold: number, colors: AnnotationColors): OverlayShape[] {
  return [
    {
      kind: "level-label",
      value: overbought,
      dy: -13,
      text: "Sobrecomprado: subiu rápido demais e costuma devolver",
      color: colors.down,
    },
    {
      kind: "level-label",
      value: oversold,
      dy: 13,
      text: "Sobrevendido: caiu rápido demais e costuma voltar",
      color: colors.up,
    },
  ];
}

interface CrossoverPhrases {
  up: string;
  down: string;
}

/**
 * Um círculo em cada cruzamento do período e a frase só no último. Os círculos ficam na
 * linha `a`, onde ela passa pela `b`.
 */
export function crossoverShapes(
  a: SeriesPoint[],
  b: SeriesPoint[],
  from: string | null,
  phrases: CrossoverPhrases,
  colors: AnnotationColors,
): OverlayShape[] {
  const valueOn = new Map(a.map((point) => [point.date, point.value]));
  const found = crossovers(a, b).filter((crossing) => from === null || crossing.date >= from);

  return found.flatMap((crossing, index): OverlayShape[] => {
    const value = valueOn.get(crossing.date);
    if (value === undefined) return [];
    const color = crossing.direction === "up" ? colors.up : colors.down;
    const circle: OverlayShape = { kind: "circle", time: crossing.date, value, color };
    if (index < found.length - 1) return [circle];
    return [circle, { kind: "note", time: crossing.date, value, text: phrases[crossing.direction], color }];
  });
}

export const MACD_PHRASES: CrossoverPhrases = {
  up: "Cruzou para cima: o impulso virou de baixa para alta",
  down: "Cruzou para baixo: o impulso virou de alta para baixa",
};

export const AVERAGE_PHRASES: CrossoverPhrases = {
  up: "A média curta cruzou para cima da longa: o preço ganhou força",
  down: "A média curta cruzou para baixo da longa: o preço perdeu força",
};
