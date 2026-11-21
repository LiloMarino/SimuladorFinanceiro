import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { CongressBase } from "@/types";

/**
 * A base do governo no Congresso: os aliados pagos com emenda e a situação de cada bancada.
 * Cada dia do pregão e cada ação do governo trazem a base de quem olha por base_update. O
 * cache vale enquanto a tela escuta o evento; a cada montagem a consulta confere de novo.
 */
export function useBase({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.base(),
    queryFn: ({ signal }) => apiFetch<CongressBase>("/api/government/base", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "base_update",
    (base) => {
      void applyRealtime<CongressBase>(queryClient, queryKeys.base(), base);
    },
    enabled,
  );

  return query;
}
