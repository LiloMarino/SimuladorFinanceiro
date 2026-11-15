import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SovereignFundPanel } from "@/types";

/**
 * O Fundo Soberano: caixa, carteira com a fatia de cada empresa e o que voltou ao Tesouro.
 * O preço e o caixa andam com o pregão: a cada dia a consulta confere de novo.
 */
export function useSovereignFund() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.sovereignFund() });
  });

  return useQuery({
    queryKey: queryKeys.sovereignFund(),
    queryFn: ({ signal }) => apiFetch<SovereignFundPanel>("/api/government/sovereign-fund", { signal }),
    staleTime: 0,
  });
}
