import { useQuery } from "@tanstack/react-query";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { MyStrategy } from "@/types";

/** A estratégia que a carteira da gestora segue (nenhuma é o modo manual) e o painel dela. */
export function useFundStrategy(fundId: number) {
  return useQuery({
    queryKey: fundKeys.strategy(fundId),
    queryFn: ({ signal }) => apiFetch<MyStrategy>(`/api/funds/${fundId}/strategy`, { signal }),
  });
}
