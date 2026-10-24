import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

/** As estratégias que um bot pode jogar, com os parâmetros na faixa válida para a data de início (a das regras do lobby, ou `startDate`). */
export function useBotStrategies(startDate?: string) {
  return useQuery({
    queryKey: queryKeys.botStrategies(startDate),
    queryFn: ({ signal }) =>
      apiFetch<StrategyInfo[]>(
        `/api/simulation/bots/strategies${startDate === undefined ? "" : `?start_date=${startDate}`}`,
        { signal },
      ),
    // A faixa depende da data de início: cada abertura do diálogo pede de novo
    staleTime: 0,
  });
}
