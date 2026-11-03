import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SavedStrategyParams } from "@/types";

/** Os últimos parâmetros de cada estratégia salvos no perfil, pela chave dela. */
export function useSavedStrategyParams() {
  return useQuery({
    queryKey: queryKeys.savedStrategyParams(),
    queryFn: ({ signal }) => apiFetch<SavedStrategyParams>("/api/settings/strategy-params", { signal }),
  });
}
