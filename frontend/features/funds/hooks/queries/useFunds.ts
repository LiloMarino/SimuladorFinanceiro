import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundRoomItem } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** As gestoras da partida, cada uma com o patrimônio por cota de agora, o preço de ranking e as cotas de quem consulta. Quando algo muda, o servidor entrega a lista nova por `funds_list_update`. */
export function useFunds({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.list(),
    queryFn: ({ signal }) => apiFetch<FundRoomItem[]>("/api/funds", { signal }),
    staleTime: 0,
    enabled,
  });

  useRealtime(
    "funds_list_update",
    ({ funds }) => {
      void applyRealtime<FundRoomItem[]>(queryClient, fundKeys.list(), funds);
    },
    enabled,
  );

  return query;
}
