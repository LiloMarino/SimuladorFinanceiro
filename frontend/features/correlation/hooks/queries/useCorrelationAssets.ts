import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CorrelationAssets } from "@/types";

export function useCorrelationAssets() {
  return useApiQuery({
    queryKey: queryKeys.correlationAssets(),
    queryFn: ({ signal }) => apiFetch<CorrelationAssets>("/api/correlation/assets", { signal }),
  });
}
