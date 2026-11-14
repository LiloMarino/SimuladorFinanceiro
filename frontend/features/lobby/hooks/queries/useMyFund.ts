import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FundIdentity } from "@/types";

/** Nome e sigla da gestora salvos no perfil; nulo enquanto o jogador não salvou uma. */
export function useMyFund() {
  return useQuery({
    queryKey: queryKeys.myFund(),
    queryFn: ({ signal }) => apiFetch<FundIdentity | null>("/api/settings/fund", { signal }),
  });
}
