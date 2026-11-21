import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { StateCompanyDetail } from "@/types";

/**
 * A estatal por trás de uma ação: origem, valor justo, dividendos, meses e quem tem as ações.
 * Vem nula quando a ação não é estatal ou a partida não tem o Governo. O preço e o mês fechado
 * andam com o pregão: a cada dia o servidor entrega a estatal por `state_company_update:{ticker}`.
 */
export function useStateCompanyDetail(ticker: string, { enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();
  const queryKey = queryKeys.stateCompanyDetail(ticker);

  useRealtime(
    `state_company_update:${ticker}`,
    ({ detail }) => {
      void applyRealtime<StateCompanyDetail | null>(queryClient, queryKey, detail);
    },
    enabled,
  );

  return useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      apiFetch<StateCompanyDetail | null>(`/api/variable-income/${ticker}/state-company`, { signal }),
    enabled,
    staleTime: 0,
  });
}
