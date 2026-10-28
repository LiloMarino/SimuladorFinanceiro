import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PromiseBalance } from "@/types";

/** Os balanços das promessas dos governos que acabaram, do mais recente ao mais antigo. */
export function useBalances(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.balances(),
    queryFn: ({ signal }) => apiFetch<PromiseBalance[]>("/api/government/balances", { signal }),
    enabled,
  });
}
