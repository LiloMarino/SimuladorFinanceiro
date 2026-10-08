import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PortfolioState } from "@/types";

/**
 * Carteira do jogador (posições, caixa, totais e rentabilidade, já calculados no
 * backend), substituída a cada tick via portfolio_update.
 */
export function usePortfolio() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.portfolio(),
    queryFn: ({ signal }) => apiFetch<PortfolioState>("/api/portfolio", { signal }),
  });

  useRealtime("portfolio_update", ({ portfolio }) => {
    queryClient.setQueryData(queryKeys.portfolio(), portfolio);
  });

  return query;
}
