import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StrategyInfo } from "@/types";

type BotStrategiesOptions = {
  /** Com `false` a lista sai sem as estratégias de gestoras; sem o valor valem as regras da sala */
  fundsEnabled?: boolean;
  /** Com `false` a lista sai sem as estratégias do governo; sem o valor valem as regras da sala */
  governmentEnabled?: boolean;
};

/** As estratégias que um bot pode jogar, com os parâmetros na faixa válida para a data de início (a das regras do lobby, ou `startDate`). */
export function useBotStrategies(startDate?: string, { fundsEnabled, governmentEnabled }: BotStrategiesOptions = {}) {
  const params = new URLSearchParams();
  if (startDate !== undefined) params.set("start_date", startDate);
  if (fundsEnabled !== undefined) params.set("funds_enabled", String(fundsEnabled));
  if (governmentEnabled !== undefined) params.set("government_enabled", String(governmentEnabled));
  const query = params.size > 0 ? `?${params}` : "";

  return useQuery({
    queryKey: queryKeys.botStrategies(startDate, fundsEnabled, governmentEnabled),
    queryFn: ({ signal }) => apiFetch<StrategyInfo[]>(`/api/simulation/bots/strategies${query}`, { signal }),
    // A faixa depende da data de início: cada abertura do diálogo pede de novo
    staleTime: 0,
  });
}
