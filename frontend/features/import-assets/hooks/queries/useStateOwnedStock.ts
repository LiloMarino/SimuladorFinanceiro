import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StateOwnedStock } from "@/types";

/** A marcação de estatal do ativo: a fatia do governo, as ações e a alavanca; nulo quando não é estatal. */
export function useStateOwnedStock(ticker: string) {
  return useQuery({
    queryKey: queryKeys.stateOwned(ticker),
    queryFn: ({ signal }) => apiFetch<StateOwnedStock | null>(`/api/import-assets/stocks/${ticker}/state`, { signal }),
  });
}
