import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CreditOverview } from "@/types";

/** Dívida, nota de risco, oferta, empréstimos e histórico do jogador. */
export function useCredit() {
  return useQuery({
    queryKey: queryKeys.creditOverview(),
    queryFn: ({ signal }) => apiFetch<CreditOverview>("/api/credit", { signal }),
  });
}
