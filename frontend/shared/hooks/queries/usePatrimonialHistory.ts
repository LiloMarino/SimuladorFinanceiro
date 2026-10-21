import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PortfolioHistoryPoint } from "@/types";

/** Histórico patrimonial diário do jogador, mantido vivo via snapshot_update (merge por data). */
export function usePatrimonialHistory() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.patrimonialHistory(),
    queryFn: ({ signal }) => apiFetch<PortfolioHistoryPoint[]>("/api/portfolio/history", { signal }),
  });

  useRealtime("snapshot_update", ({ snapshot }) => {
    queryClient.setQueryData(queryKeys.patrimonialHistory(), (prev: PortfolioHistoryPoint[] | undefined) => {
      if (!prev) return prev;

      const map = new Map(prev.map((h) => [h.snapshot_date, h]));

      map.set(snapshot.snapshot_date, snapshot);

      return Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date));
    });
  });

  return query;
}
