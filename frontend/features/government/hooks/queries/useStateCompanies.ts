import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StateCompaniesPanel } from "@/types";

/**
 * As estatais do governo: resumo, uma linha por empresa, movimentos e ofertas de privatização.
 * O preço, o dividendo e a oferta andam com o pregão: a cada dia a consulta confere de novo.
 */
export function useStateCompanies() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanies() });
  });

  return useQuery({
    queryKey: queryKeys.stateCompanies(),
    queryFn: ({ signal }) => apiFetch<StateCompaniesPanel>("/api/government/state-companies", { signal }),
    staleTime: 0,
  });
}
