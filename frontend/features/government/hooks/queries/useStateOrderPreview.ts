import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StateOrderPreview } from "@/types";

/** O que cada degrau do controle e cada política de dividendos fariam na estatal, e o teto que sobra a ela. */
export function useStateOrderPreview(ticker: string) {
  return useQuery({
    queryKey: queryKeys.stateOrderPreview(ticker),
    queryFn: ({ signal }) =>
      apiFetch<StateOrderPreview>(`/api/government/state-companies/${ticker}/order-preview`, { signal }),
    staleTime: 0,
  });
}
