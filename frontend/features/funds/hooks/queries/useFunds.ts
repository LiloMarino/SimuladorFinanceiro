import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FundRoomItem } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** As gestoras da partida, cada uma com o patrimônio por cota de agora, o preço de ranking e as cotas de quem consulta. Quando algo muda (funds_update), busca de novo. */
export function useFunds({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.list(),
    queryFn: ({ signal }) => apiFetch<FundRoomItem[]>("/api/funds", { signal }),
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
