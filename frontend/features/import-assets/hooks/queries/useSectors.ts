import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Sector } from "@/types";

export function useSectors() {
  return useQuery({
    queryKey: queryKeys.sectors(),
    queryFn: ({ signal }) => apiFetch<Sector[]>("/api/import-assets/sectors", { signal }),
  });
}
