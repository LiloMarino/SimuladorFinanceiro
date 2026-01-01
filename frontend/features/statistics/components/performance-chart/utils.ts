import type { PlayerHistory, PerformanceMetric } from "@/types";

export function buildChartData(players: PlayerHistory[], metric: PerformanceMetric) {
  const map = new Map<number, Record<string, number>>();

  players.forEach((player) => {
    player.history.forEach((h) => {
      const timestamp = new Date(`${h.snapshot_date}T00:00:00`).getTime();

      if (!map.has(timestamp)) {
        map.set(timestamp, { timestamp });
      }

      map.get(timestamp)![player.player_nickname] = h[metric];
    });
  });

  return Array.from(map.values()).sort((a, b) => a.timestamp - b.timestamp);
}
