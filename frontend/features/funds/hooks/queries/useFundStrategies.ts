import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

/** As estratégias que uma gestora segue: a lista do app sem "Cotas de gestoras". */
export function useFundStrategies() {
  return useQuery({
    queryKey: queryKeys.fundStrategyList(),
    queryFn: ({ signal }) => apiFetch<StrategyInfo[]>("/api/strategies?fund=true", { signal }),
  });
}
