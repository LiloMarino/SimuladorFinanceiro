import type { LineSeries } from "./series";

/** "date": as séries no calendário; "index": cada uma pelo número do pregão, para partidas de períodos diferentes. */
export type ChartAxis = "date" | "index";

export interface LineChartRow {
  x: number;
  numbers: Record<string, number>;
  values: Record<string, string>;
}

/** Marcas redondas do eixo Y (1, 2, 2,5 ou 5 por potência de 10) que englobam de `min` a `max`. */
export function niceTicks(min: number, max: number, count = 5): number[] {
  if (min === max) {
    const pad = Math.abs(min) * 0.1 || 1;
    return niceTicks(min - pad, max + pad, count);
  }
  const rough = (max - min) / count;
  const base = 10 ** Math.floor(Math.log10(rough));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * base).find((s) => s >= rough) ?? 10 * base;
  const start = Math.floor(min / step) * step;
  const end = Math.ceil(max / step) * step;
  const ticks: number[] = [];
  for (let tick = start; tick <= end + step / 2; tick += step) ticks.push(Number(tick.toFixed(10)));
  return ticks;
}

/** Um marco por mês, no dia 1, entre `min` e `max` (timestamps), com no máximo `limit` marcas. */
export function monthStartTicks(min: number, max: number, limit = 8): number[] {
  const first = new Date(min);
  const months: number[] = [];
  for (
    let cursor = new Date(first.getFullYear(), first.getMonth() + (first.getDate() > 1 ? 1 : 0), 1);
    cursor.getTime() <= max;
    cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1)
  ) {
    months.push(cursor.getTime());
  }
  const every = Math.max(1, Math.ceil(months.length / limit));
  return months.filter((_, i) => i % every === 0);
}

/** Uma linha por posição no eixo; séries em number só para a geometria, o tooltip formata a string original. */
export function buildChartData(series: LineSeries[], axis: ChartAxis) {
  const rows = new Map<number, LineChartRow>();

  series.forEach((s) => {
    s.points.forEach((point, i) => {
      const x = axis === "index" ? i + 1 : new Date(`${point.date}T00:00:00`).getTime();
      const row = rows.get(x) ?? { x, numbers: {}, values: {} };

      row.numbers[s.key] = Number(point.value);
      row.values[s.key] = point.value;
      rows.set(x, row);
    });
  });

  return Array.from(rows.values()).sort((a, b) => a.x - b.x);
}
