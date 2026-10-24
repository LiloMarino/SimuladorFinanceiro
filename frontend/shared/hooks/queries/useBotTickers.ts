import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

/** As ações que um bot pode operar, em ordem alfabética: as opções do "Escolher" dos parâmetros. */
export function useBotTickers() {
  return useQuery({
    queryKey: queryKeys.botTickers(),
    queryFn: ({ signal }) => apiFetch<string[]>("/api/simulation/bots/tickers", { signal }),
  });
}
