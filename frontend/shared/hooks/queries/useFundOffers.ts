import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { FundOffers } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** As ofertas públicas das gestoras: a preferência de quem consulta, as abertas a todos e as encerradas. Quando algo muda (funds_update), busca de novo. */
export function useFundOffers({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.offers(),
    queryFn: ({ signal }) => apiFetch<FundOffers>("/api/funds/offers", { signal }),
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
