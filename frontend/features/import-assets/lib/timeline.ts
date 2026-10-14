import { parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

/** Eixo comum das barras: do início mais antigo até hoje, em milissegundos. */
export type TimelineRange = { start: number; end: number };

export function timelineRange(series: SeriesCoverage[]): TimelineRange {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dates = series
    .flatMap((s) => [s.start, s.real_end, s.generated_end])
    .filter((d): d is string => !!d)
    .map((d) => parseLocalDate(d).getTime());
  return {
    start: dates.length ? Math.min(...dates) : today.getTime(),
    end: Math.max(today.getTime(), ...dates),
  };
}

/** Posição de uma data no eixo, em %. */
export function timelineOffset(isoDate: string, range: TimelineRange): number {
  const span = range.end - range.start || 1;
  return ((parseLocalDate(isoDate).getTime() - range.start) / span) * 100;
}

/** Até quatro anos redondos dentro do eixo, com a posição de cada um em %. */
export function timelineTicks(range: TimelineRange): { label: string; position: number }[] {
  const first = new Date(range.start).getFullYear();
  const last = new Date(range.end).getFullYear();
  const step = [5, 10, 20, 25, 50].find((s) => (last - first) / s <= 4) ?? 50;
  const ticks = [];
  for (let year = Math.ceil(first / step) * step; year <= last; year += step) {
    const position = timelineOffset(`${year}-01-01`, range);
    // Ano perto do fim do eixo fica de fora: encostaria no marcador "hoje"
    if (position > 0 && position < 82) ticks.push({ label: String(year), position });
  }
  return ticks;
}
