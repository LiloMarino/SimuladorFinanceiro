import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundOffers } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** As ofertas públicas das gestoras: a preferência de quem consulta, as abertas a todos e as encerradas. Quando algo muda, o servidor entrega as ofertas novas por `fund_offers_update`. */
export function useFundOffers({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: fundKeys.offers(),
    queryFn: ({ signal }) => apiFetch<FundOffers>("/api/funds/offers", { signal }),
    staleTime: 0,
    enabled,
  });

  useRealtime(
    "fund_offers_update",
    (offers) => {
      void applyRealtime<FundOffers>(queryClient, fundKeys.offers(), offers);
    },
    enabled,
  );

  return query;
}
