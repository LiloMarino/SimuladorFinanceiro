import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasuryCover } from "@/types";

/** Se a cobertura automática pode vender também Prefixado e IPCA+, a preço de mercado. */
export function useTreasuryCover() {
  return useQuery({
    queryKey: queryKeys.treasuryCover(),
    queryFn: ({ signal }) => apiFetch<TreasuryCover>("/api/settings/treasury-cover", { signal }),
  });
}
