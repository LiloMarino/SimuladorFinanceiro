import type { CandlePattern, CandlePatterns, PatternStats } from "@/types";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { MIN_SAMPLE } from "./candle-patterns";

/** Os padrões que terminam dentro do período (de `from` em diante; sem `from`, todos). */
export function patternsSince(patterns: CandlePattern[], from: string | null) {
  return from === null ? patterns : patterns.filter((pattern) => pattern.end >= from);
}

/** Quantos padrões do período já tiveram o lado conferido e quantos acertaram. */
export function periodScore(patterns: CandlePattern[]) {
  const checked = patterns.filter((pattern) => pattern.hit !== null);
  return { hits: checked.filter((pattern) => pattern.hit).length, checked: checked.length };
}

export function statsOf(patterns: CandlePatterns | undefined, code: CandlePattern["code"]): PatternStats {
  return patterns?.stats.find((stats) => stats.code === code) ?? { code, checked: 0, hits: 0 };
}

/** A taxa de acerto só sai quando a amostra sustenta: abaixo disso é `null`. */
export function hitRate(stats: PatternStats) {
  return stats.checked >= MIN_SAMPLE ? stats.hits / stats.checked : null;
}

/** O padrão que cobre o dia (inclusive os de várias velas), o mais recente primeiro. */
export function patternOn(patterns: CandlePattern[], day: string) {
  return [...patterns].reverse().find((pattern) => pattern.start <= day && day <= pattern.end);
}

/** O período mais largo que passa a ter padrões: a sugestão do aviso de período vazio. */
export function nextScaleWithPatterns<S extends string>(
  scales: readonly S[],
  current: S,
  count: (scale: S) => number,
): { scale: S; count: number } | null {
  for (const scale of scales.slice(scales.indexOf(current) + 1)) {
    const found = count(scale);
    if (found > 0) return { scale, count: found };
  }
  return null;
}

/** "26–27 dez", ou "27 jan" quando o padrão cabe numa vela só. */
export function displayPatternDays(pattern: Pick<CandlePattern, "start" | "end">) {
  if (pattern.start === pattern.end) return displayDayMonth(pattern.end);
  const start = displayDayMonth(pattern.start);
  const end = displayDayMonth(pattern.end);
  const [startDay, startMonth] = start.split(" ");
  const [, endMonth] = end.split(" ");
  return startMonth === endMonth ? `${startDay}–${end}` : `${start} – ${end}`;
}
