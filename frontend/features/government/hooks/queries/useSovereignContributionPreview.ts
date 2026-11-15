import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SovereignContributionPreview } from "@/types";

/** O que o aporte faria: a medida (voto, vigência e dívida) e o caixa do fundo antes e depois. */
export function useSovereignContributionPreview(value: string | null) {
  return useQuery({
    queryKey: queryKeys.sovereignContributionPreview(value ?? ""),
    queryFn: ({ signal }) =>
      apiFetch<SovereignContributionPreview>("/api/government/sovereign-fund/contribution-preview", {
        method: "POST",
        body: { value },
        signal,
      }),
    enabled: value !== null,
    placeholderData: keepPreviousData,
  });
}
