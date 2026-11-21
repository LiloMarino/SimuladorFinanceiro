import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import type { TreasuryHistoryPoint } from "@/types";
import { mergeHistoryPoint } from "../../lib/treasury";

/** Um ponto por fechamento de mês; o servidor entrega o ponto novo por `treasury_history_update`. */
export function useTreasuryHistory() {
  const queryClient = useQueryClient();

  useRealtime("treasury_history_update", ({ point }) => {
    void applyRealtimeDelta<TreasuryHistoryPoint[]>(queryClient, queryKeys.treasuryHistory(), (current) =>
      mergeHistoryPoint(current, point),
    );
  });

  return useQuery({
    queryKey: queryKeys.treasuryHistory(),
    queryFn: ({ signal }) => apiFetch<TreasuryHistoryPoint[]>("/api/treasury/history", { signal }),
    staleTime: 0,
  });
}
