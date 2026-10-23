import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { MyStrategy } from "@/types";

/** A estratégia que o jogador deixou ligada (nenhuma é o modo manual), o erro que o devolveu ao manual e o painel. */
export function useMyStrategy() {
  return useQuery({
    queryKey: queryKeys.myStrategy(),
    queryFn: ({ signal }) => apiFetch<MyStrategy>("/api/strategies/me", { signal }),
  });
}
