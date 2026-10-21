import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { GeneratedFuture } from "@/types";

/** Os controles do futuro gravado; `null` quando a base ainda não tem um. */
export function useGeneratedFuture() {
  return useQuery({
    queryKey: queryKeys.generatedFuture(),
    queryFn: ({ signal }) => apiFetch<GeneratedFuture | null>("/api/import-assets/future", { signal }),
  });
}
