import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

/** As estratégias do app, com regra, parâmetros, faixa e padrão da partida; com `fund`, só as que uma gestora segue (sem "Cotas de gestoras"). */
export function useStrategies({ fund = false }: { fund?: boolean } = {}) {
  return useQuery({
    queryKey: fund ? queryKeys.fundStrategyList() : queryKeys.strategyList(),
    queryFn: ({ signal }) =>
      apiFetch<StrategyInfo[]>(fund ? "/api/strategies?fund=true" : "/api/strategies", { signal }),
  });
}
