import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PlayerHistory } from "@/types";

/** Histórico de patrimônio de todos os jogadores, mantido vivo via statistics_snapshot_update. */
export function useStatistics() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.statistics(),
    queryFn: ({ signal }) => apiFetch<PlayerHistory[]>("/api/statistics", { signal }),
  });

  useRealtime("statistics_snapshot_update", ({ snapshots }) => {
    queryClient.setQueryData(queryKeys.statistics(), (prev: PlayerHistory[] | undefined) => {
      if (!prev) return prev;

      return prev.map((player) => {
        const updates = snapshots.filter((s) => s.player_nickname === player.player_nickname);

        if (!updates.length) return player;

        const map = new Map(player.history.map((h) => [h.snapshot_date, h]));

        updates.forEach(({ snapshot }) => {
          map.set(snapshot.snapshot_date, snapshot);
        });

        return {
          ...player,
          history: Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date)),
        };
      });
    });
  });

  return query;
}
