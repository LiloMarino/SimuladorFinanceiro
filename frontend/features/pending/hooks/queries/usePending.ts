import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { Pending } from "@/types";

/**
 * O que pede ação do jogador agora, das graves para as de aviso. A lista é o estado do
 * servidor: o caixa, o dia e o governo entregam a lista nova por `pending_update`.
 */
export function usePending() {
  const queryClient = useQueryClient();

  useRealtime("pending_update", ({ items }) => {
    void applyRealtime<Pending[]>(queryClient, queryKeys.pending(), items);
  });

  return useQuery({
    queryKey: queryKeys.pending(),
    queryFn: ({ signal }) => apiFetch<Pending[]>("/api/pending", { signal }),
  });
}
