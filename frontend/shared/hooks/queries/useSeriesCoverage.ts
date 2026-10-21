import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SeriesCoverage } from "@/types";

export function useSeriesCoverage() {
  return useQuery({
    queryKey: queryKeys.seriesCoverage(),
    queryFn: ({ signal }) => apiFetch<SeriesCoverage[]>("/api/import-assets/coverage", { signal }),
  });
}
