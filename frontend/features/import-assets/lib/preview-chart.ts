import { parseLocalDate } from "@/shared/lib/utils/display";
import type { FuturePreview } from "@/types";

type PreviewSeries = FuturePreview["ibov"];

export type PreviewRow = { time: number; real?: number; generated?: number };

export type PreviewChartData = {
  rows: PreviewRow[];
  /** Último dia real: onde o gerado passa a valer */
  lastRealTime: number | null;
  lastTime: number;
};

const time = (iso: string) => parseLocalDate(iso).getTime();

/** A cauda real e o gerado numa tabela só; o gerado nasce no último ponto real, sem vão entre as duas linhas. */
export function previewChartData(series: PreviewSeries): PreviewChartData {
  const real: PreviewRow[] = series.real.map((p) => ({ time: time(p.date), real: p.value }));
  const lastReal = real.at(-1);
  const bridge: PreviewRow[] = lastReal ? [{ ...lastReal, generated: lastReal.real }] : [];
  const generated: PreviewRow[] = series.generated.map((p) => ({ time: time(p.date), generated: p.value }));
  const rows = [...real.slice(0, -1), ...bridge, ...generated];
  return { rows, lastRealTime: lastReal?.time ?? null, lastTime: rows.at(-1)?.time ?? 0 };
}

/** Marcas de 1º de janeiro, em número que cabe no eixo (no máximo `limit`). */
export function yearTicks(first: number, last: number, limit: number): number[] {
  const firstYear = new Date(first).getFullYear() + 1;
  const lastYear = new Date(last).getFullYear();
  const step = Math.max(1, Math.ceil((lastYear - firstYear + 1) / limit));
  const ticks: number[] = [];
  for (let year = firstYear; year <= lastYear; year += step) ticks.push(new Date(year, 0, 1).getTime());
  return ticks;
}
