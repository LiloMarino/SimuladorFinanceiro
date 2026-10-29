import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CongressBase } from "@/types";

const REFRESH_MS = 15_000;

/** A base do governo no Congresso: os aliados pagos com emenda e a situação de cada bancada. */
export function useBase({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.base(),
    queryFn: ({ signal }) => apiFetch<CongressBase>("/api/government/base", { signal }),
    enabled,
    refetchInterval: REFRESH_MS,
  });
}
