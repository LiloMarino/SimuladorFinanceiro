import { useQuery } from "@tanstack/react-query";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { StrategyLogPage } from "@/types";

/** As últimas ordens que a estratégia mandou pela carteira da gestora, da mais recente à mais antiga. */
export function useFundStrategyLog(fundId: number, limit: number, enabled: boolean) {
  return useQuery({
    queryKey: [...fundKeys.strategyLog(fundId), limit] as const,
    queryFn: ({ signal }) => {
      const params = new URLSearchParams({ kind: "orders", offset: "0", limit: String(limit) });
      return apiFetch<StrategyLogPage>(`/api/funds/${fundId}/strategy/log?${params}`, { signal });
    },
    enabled,
  });
}
