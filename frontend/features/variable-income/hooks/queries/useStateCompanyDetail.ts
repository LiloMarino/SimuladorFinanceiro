import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StateCompanyDetail } from "@/types";

/**
 * A estatal por trás de uma ação: origem, valor justo, dividendos, meses e quem tem as ações.
 * Vem nula quando a ação não é estatal ou a partida não tem o Governo. O preço e o mês fechado
 * andam com o pregão: a cada dia a consulta confere de novo.
 */
export function useStateCompanyDetail(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  useRealtime(
    "simulation_update",
    () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanyDetail(ticker) });
    },
    enabled,
  );

  return useQuery({
    queryKey: queryKeys.stateCompanyDetail(ticker),
    queryFn: ({ signal }) =>
      apiFetch<StateCompanyDetail | null>(`/api/variable-income/${ticker}/state-company`, { signal }),
    enabled,
    staleTime: 0,
  });
}
