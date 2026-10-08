import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PatrimonialHistory } from "@/types";

/** Histórico patrimonial mensal do jogador, mantido vivo via snapshot_update (merge por data). */
export function usePatrimonialHistory() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.patrimonialHistory(),
    queryFn: ({ signal }) => apiFetch<PatrimonialHistory[]>("/api/portfolio/history", { signal }),
  });

  useRealtime("snapshot_update", ({ snapshot }) => {
    queryClient.setQueryData(queryKeys.patrimonialHistory(), (prev: PatrimonialHistory[] | undefined) => {
      if (!prev) return prev;

      const map = new Map(prev.map((h) => [h.snapshot_date, h]));

      map.set(snapshot.snapshot_date, {
        snapshot_date: snapshot.snapshot_date,
        total_networth: snapshot.total_networth,
        total_equity: snapshot.total_equity,
        total_fixed: snapshot.total_fixed,
        total_cash: snapshot.total_cash,
        total_contribution: snapshot.total_contribution,
      });

      return Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date));
    });
  });

  return query;
}
