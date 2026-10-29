import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { DealPreview } from "@/types";

/** O que a proposta à bancada faz: preço, base, dívida e se o computador deve aceitar. */
export function useDealPreview(blocKey: number | null) {
  return useQuery({
    queryKey: queryKeys.dealPreview(blocKey ?? 0),
    queryFn: ({ signal }) => apiFetch<DealPreview>(`/api/government/deals/preview?bloc_key=${blocKey}`, { signal }),
    enabled: blocKey !== null,
    placeholderData: keepPreviousData,
  });
}
