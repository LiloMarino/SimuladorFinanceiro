import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { MeasurePreview, ProposeMeasureRequest } from "@/types";

/** O que a medida rascunhada faz: aprovação, marca na régua, chance e quem tem os ativos. */
export function useMeasurePreview(request: ProposeMeasureRequest | null) {
  return useQuery({
    queryKey: queryKeys.measurePreview(request ?? {}),
    queryFn: ({ signal }) =>
      apiFetch<MeasurePreview>("/api/government/measures/preview", { method: "POST", body: request, signal }),
    enabled: request !== null,
    placeholderData: keepPreviousData,
  });
}
