import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { eventAccountKey } from "@/shared/lib/active-account";
import type { PortfolioState } from "@/types";

/**
 * Carteira do jogador: posições, caixa, totais e rentabilidade, já calculados no backend. A pessoal
 * é o padrão; as páginas de mercado pedem `activeAccount` para ler a da gestora que ele opera.
 * Cada tick traz a carteira de cada conta por portfolio_update, e cada uma entra no cache da
 * própria conta. Existe só durante a partida.
 */
export function usePortfolio({
  enabled = true,
  activeAccount = false,
}: { enabled?: boolean; activeAccount?: boolean } = {}) {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();

  const query = useQuery({
    queryKey: queryKeys.portfolioOf(activeAccount ? accountKey : "personal"),
    queryFn: ({ signal }) => apiFetch<PortfolioState>("/api/portfolio", { signal, activeAccount }),
    enabled,
  });

  useRealtime("portfolio_update", ({ portfolio, account }) => {
    queryClient.setQueryData(queryKeys.portfolioOf(eventAccountKey(account)), portfolio);
  });

  return query;
}
