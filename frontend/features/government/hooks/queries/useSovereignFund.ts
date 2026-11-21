import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { SovereignFundPanel } from "@/types";

/**
 * O Fundo Soberano: caixa, carteira com a fatia de cada empresa e o que voltou ao Tesouro.
 * O preço e o caixa andam com o pregão: a cada dia o servidor entrega o painel por `sovereign_fund_update`.
 */
export function useSovereignFund() {
  const queryClient = useQueryClient();

  useRealtime("sovereign_fund_update", (panel) => {
    void applyRealtime<SovereignFundPanel>(queryClient, queryKeys.sovereignFund(), panel);
  });

  return useQuery({
    queryKey: queryKeys.sovereignFund(),
    queryFn: ({ signal }) => apiFetch<SovereignFundPanel>("/api/government/sovereign-fund", { signal }),
    staleTime: 0,
  });
}
