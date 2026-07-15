import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";

/**
 * Saldo em caixa do jogador via `/api/portfolio/cash`, mantido vivo via cash_update.
 * Representa o mesmo valor de backend que `useSimulationState()`'s `cash`, mas por um
 * endpoint/chave separados — não unificados nesta migração (mudaria o backend).
 */
export function usePortfolioCash() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.portfolioCash(),
    queryFn: ({ signal }) => apiFetch<{ cash: number }>("/api/portfolio/cash", { signal }),
  });

  useRealtime("cash_update", ({ cash }) => {
    queryClient.setQueryData(queryKeys.portfolioCash(), { cash });
  });

  return query;
}
