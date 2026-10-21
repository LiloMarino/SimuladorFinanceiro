import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CorrelationAssets } from "@/types";

export function useCorrelationAssets() {
  return useQuery({
    queryKey: queryKeys.correlationAssets(),
    queryFn: ({ signal }) => apiFetch<CorrelationAssets>("/api/correlation/assets", { signal }),
  });
}
