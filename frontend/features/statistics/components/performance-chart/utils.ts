import type { PlayerPerformance, PerformanceMetric } from "@/types";
import { playerLabel } from "../../lib/player-label";

export interface PerformanceChartRow {
  timestamp: number;
  numbers: Record<string, number>;
  values: Record<string, string>;
}

/** Uma linha por data; séries em number só para a geometria, o tooltip formata a string original. */
export function buildChartData(players: PlayerPerformance[], metric: PerformanceMetric, showSimulation: boolean) {
  const rows = new Map<number, PerformanceChartRow>();

  players.forEach((player) => {
    const label = playerLabel(player, showSimulation);

    player.history.forEach((h) => {
      const timestamp = new Date(`${h.snapshot_date}T00:00:00`).getTime();
      const row = rows.get(timestamp) ?? { timestamp, numbers: {}, values: {} };

      row.numbers[label] = Number(h[metric]);
      row.values[label] = h[metric];
      rows.set(timestamp, row);
    });
  });

  return Array.from(rows.values()).sort((a, b) => a.timestamp - b.timestamp);
}
