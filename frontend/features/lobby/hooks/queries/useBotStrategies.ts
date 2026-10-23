import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

/** As estratégias que um bot pode jogar, com os parâmetros na faixa válida para a data de início das regras. */
export function useBotStrategies() {
  return useQuery({
    queryKey: queryKeys.botStrategies(),
    queryFn: ({ signal }) => apiFetch<StrategyInfo[]>("/api/simulation/bots/strategies", { signal }),
    // A faixa depende da data de início: cada abertura do diálogo pede de novo
    staleTime: 0,
  });
}
