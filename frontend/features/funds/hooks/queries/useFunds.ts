import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

/** As gestoras da partida, cada uma com o patrimônio por cota de agora e o preço de ranking. Quando algo muda (funds_update), busca de novo. */
export function useFunds({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.list(),
    queryFn: ({ signal }) => apiFetch<FundSummary[]>("/api/funds", { signal }),
    enabled,
  });

  useRealtime(
    "funds_update",
    () => {
      void queryClient.invalidateQueries({ queryKey: fundKeys.all() });
    },
    enabled,
  );

  return query;
}
