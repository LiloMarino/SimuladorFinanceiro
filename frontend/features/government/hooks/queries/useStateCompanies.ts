import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { StateCompaniesPanel } from "@/types";

/**
 * As estatais do governo: resumo, uma linha por empresa, movimentos e ofertas de privatização.
 * O preço, o dividendo e a oferta andam com o pregão: a cada dia o servidor entrega o painel por `state_companies_update`.
 */
export function useStateCompanies() {
  const queryClient = useQueryClient();

  useRealtime("state_companies_update", (panel) => {
    void applyRealtime<StateCompaniesPanel>(queryClient, queryKeys.stateCompanies(), panel);
  });

  return useQuery({
    queryKey: queryKeys.stateCompanies(),
    queryFn: ({ signal }) => apiFetch<StateCompaniesPanel>("/api/government/state-companies", { signal }),
    staleTime: 0,
  });
}
