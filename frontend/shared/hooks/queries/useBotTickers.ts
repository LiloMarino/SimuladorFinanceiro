import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { BotTicker } from "@/types";

/** As ações que um bot pode operar (código e nome), em ordem alfabética: as opções dos parâmetros de ações. */
export function useBotTickers() {
  return useQuery({
    queryKey: queryKeys.botTickers(),
    queryFn: ({ signal }) => apiFetch<BotTicker[]>("/api/simulation/bots/tickers", { signal }),
  });
}
