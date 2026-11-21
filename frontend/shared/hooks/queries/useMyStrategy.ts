import { queryOptions, useQuery } from "@tanstack/react-query";
import { useStrategyRoute } from "@/shared/hooks/useStrategyRoute";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { strategyFundId, strategyPaths } from "@/shared/lib/strategy-route";
import type { MyStrategy } from "@/types";

/** A leitura do automático de uma conta (a pessoal é `null`, a gestora é o id dela): a chave e a rota ficam aqui, num lugar só. */
export const accountStrategyQuery = (fundId: number | null) =>
  queryOptions({
    queryKey: queryKeys.myStrategyOf(fundId ?? "personal"),
    queryFn: ({ signal }) => apiFetch<MyStrategy>(strategyPaths(fundId).mine, { signal }),
  });

/**
 * O automático de uma conta: a estratégia ligada (nenhuma é o modo manual), o erro que a devolveu ao manual e o
 * painel. A pessoal é o padrão; com `activeAccount` vale a conta do topo, a gestora pela rota dela. O Fundo
 * Soberano não tem automático, e a leitura dele cai na conta pessoal. Com a lista de contas ainda a caminho a
 * rota da conta do topo é incerta, e a leitura espera por ela.
 */
export function useMyStrategy({ activeAccount = false }: { activeAccount?: boolean } = {}) {
  const route = useStrategyRoute();
  const fundId = activeAccount ? strategyFundId(route) : null;

  return useQuery({ ...accountStrategyQuery(fundId), enabled: !(activeAccount && route.kind === "pending") });
}
