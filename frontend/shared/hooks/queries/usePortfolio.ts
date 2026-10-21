import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { PortfolioState } from "@/types";

/**
 * Carteira do jogador (posições, caixa, totais e rentabilidade, já calculados no
 * backend), substituída a cada tick via portfolio_update. Existe só durante a partida.
 */
export function usePortfolio({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.portfolio(),
    queryFn: ({ signal }) => apiFetch<PortfolioState>("/api/portfolio", { signal }),
    enabled,
  });

  useRealtime("portfolio_update", ({ portfolio }) => {
    queryClient.setQueryData(queryKeys.portfolio(), portfolio);
  });

  return query;
}
