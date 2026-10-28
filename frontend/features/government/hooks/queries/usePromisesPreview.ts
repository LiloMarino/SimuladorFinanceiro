import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PromisesPreview, PromisesRequest } from "@/types";

/** O que cada promessa da lista rende em cada grupo hoje, e o que voltar atrás nas já anunciadas custaria. */
export function usePromisesPreview(request: PromisesRequest | null) {
  return useQuery({
    queryKey: queryKeys.promisesPreview(request ?? {}),
    queryFn: ({ signal }) =>
      apiFetch<PromisesPreview>("/api/government/promises/preview", { method: "POST", body: request, signal }),
    enabled: request !== null,
    placeholderData: keepPreviousData,
  });
}
