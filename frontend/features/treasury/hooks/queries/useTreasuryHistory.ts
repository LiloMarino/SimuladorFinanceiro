import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasuryHistoryPoint } from "@/types";

/** Um ponto por fechamento de mês; o ponto novo chega no dia 1º. */
export function useTreasuryHistory() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", ({ current_date }) => {
    if (current_date.endsWith("-01")) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.treasuryHistory() });
    }
  });

  return useQuery({
    queryKey: queryKeys.treasuryHistory(),
    queryFn: ({ signal }) => apiFetch<TreasuryHistoryPoint[]>("/api/treasury/history", { signal }),
  });
}
