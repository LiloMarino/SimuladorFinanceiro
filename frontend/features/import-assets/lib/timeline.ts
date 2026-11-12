import { parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

/** Eixo comum das barras, em milissegundos: do início mais antigo até 20 anos depois de hoje. */
export type TimelineRange = { start: number; end: number; today: number };

export type TimelineTick = { label: string; position: number; align: "start" | "center" | "end" };

/** Anos de futuro que o eixo mostra depois de hoje: o horizonte do futuro gerado. */
const FUTURE_YEARS = 20;

/** Distância mínima entre duas marcas do eixo, em % da largura: abaixo disso os rótulos se tocam. */
const MIN_TICK_GAP = 12;

function startOfToday(): Date {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
}

export function timelineRange(series: SeriesCoverage[], today: Date = startOfToday()): TimelineRange {
  const dates = series
    .flatMap((s) => [s.start, s.real_end, s.generated_end])
    .filter((d): d is string => !!d)
    .map((d) => parseLocalDate(d).getTime());
  const horizon = new Date(today.getFullYear() + FUTURE_YEARS, today.getMonth(), today.getDate()).getTime();
  return {
    start: dates.length ? Math.min(...dates, today.getTime()) : today.getTime(),
    end: Math.max(horizon, ...dates),
    today: today.getTime(),
  };
}

function offsetOf(time: number, range: TimelineRange): number {
  return ((time - range.start) / (range.end - range.start || 1)) * 100;
}

/** Posição de uma data no eixo, em %. */
export function timelineOffset(isoDate: string, range: TimelineRange): number {
  return offsetOf(parseLocalDate(isoDate).getTime(), range);
}

/** Posição de hoje no eixo, em %. */
export function timelineTodayOffset(range: TimelineRange): number {
  return offsetOf(range.today, range);
}

/**
 * As marcas do cabeçalho: o ano inicial, o ano final, "hoje" na posição real e os anos redondos
 * que cabem sem encostar em nenhuma delas. A ordem de entrada é a de prioridade.
 */
export function timelineTicks(range: TimelineRange): TimelineTick[] {
  const first = new Date(range.start).getFullYear();
  const last = new Date(range.end).getFullYear();
  const ticks: TimelineTick[] = [
    { label: String(first), position: 0, align: "start" },
    { label: "hoje", position: timelineTodayOffset(range), align: "center" },
    { label: String(last), position: 100, align: "end" },
  ];

  const step = [5, 10, 20, 25, 50].find((s) => (last - first) / s <= 4) ?? 50;
  for (let year = Math.ceil((first + 1) / step) * step; year < last; year += step) {
    const position = offsetOf(new Date(year, 0, 1).getTime(), range);
    if (ticks.every((tick) => Math.abs(tick.position - position) >= MIN_TICK_GAP)) {
      ticks.push({ label: String(year), position, align: "center" });
    }
  }
  return ticks.sort((a, b) => a.position - b.position);
}
