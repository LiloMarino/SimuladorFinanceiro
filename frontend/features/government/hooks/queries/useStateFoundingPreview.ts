import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FoundStateCompanyRequest, StateFoundingPreview } from "@/types";

/** O que fundar a estatal faria: a medida (voto, vigência e dívida) e os efeitos da empresa. */
export function useStateFoundingPreview(request: FoundStateCompanyRequest | null) {
  return useQuery({
    queryKey: queryKeys.stateFoundingPreview(request ?? {}),
    queryFn: ({ signal }) =>
      apiFetch<StateFoundingPreview>("/api/government/state-companies/found-preview", {
        method: "POST",
        body: request,
        signal,
      }),
    enabled: request !== null,
    placeholderData: keepPreviousData,
  });
}
