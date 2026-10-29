import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Budget } from "@/types";

const REFRESH_MS = 15_000;

/** A conta do governo no último fechamento de mês; renova enquanto a tela está aberta. */
export function useBudget({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.budget(),
    queryFn: ({ signal }) => apiFetch<Budget>("/api/government/budget", { signal }),
    enabled,
    refetchInterval: REFRESH_MS,
  });
}
