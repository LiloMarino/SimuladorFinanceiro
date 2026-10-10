import type { LineSeries } from "./series";

export interface LineChartRow {
  timestamp: number;
  numbers: Record<string, number>;
  values: Record<string, string>;
}

/** Uma linha por data; séries em number só para a geometria, o tooltip formata a string original. */
export function buildChartData(series: LineSeries[]) {
  const rows = new Map<number, LineChartRow>();

  series.forEach((s) => {
    s.points.forEach((point) => {
      const timestamp = new Date(`${point.date}T00:00:00`).getTime();
      const row = rows.get(timestamp) ?? { timestamp, numbers: {}, values: {} };

      row.numbers[s.key] = Number(point.value);
      row.values[s.key] = point.value;
      rows.set(timestamp, row);
    });
  });

  return Array.from(rows.values()).sort((a, b) => a.timestamp - b.timestamp);
}
