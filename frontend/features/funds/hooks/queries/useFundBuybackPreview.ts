import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundBuybackPreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";

/** O aviso só vale para o pedido que a tela mostra: o servidor guarda o último pedido do cliente na gestora. */
const sameDecimal = (sent: number | string, shown: number | string) => Number(sent) === Number(shown);

/**
 * O custo, o ágio e o patrimônio por cota de quem fica, para `quantity` cotas a até `maxPrice` (decimal em string).
 * O servidor guarda o último pedido e entrega a prévia nova por `fund_buyback_preview:{id}`.
 */
export function useFundBuybackPreview(fundId: number, quantity: number, maxPrice: string) {
  const queryClient = useQueryClient();
  const queryKey = fundKeys.buybackPreview(fundId, quantity, maxPrice);
  const active = quantity > 0 && Number(maxPrice) > 0;

  useRealtime(
    `fund_buyback_preview:${fundId}`,
    (event) => {
      if (event.quantity !== quantity || !sameDecimal(event.max_price, maxPrice)) return;
      void applyRealtime<PreviewOutcome<FundBuybackPreview>>(queryClient, queryKey, outcomeOfPreviewEvent(event));
    },
    active,
  );

  const { data, ...query } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<FundBuybackPreview>(
        `/api/funds/${fundId}/buyback/preview?quantity=${quantity}&max_price=${maxPrice}`,
        { signal },
      ),
    enabled: active,
    placeholderData: keepPreviousData,
    staleTime: 0,
  });

  return { ...query, preview: data?.preview ?? undefined, refused: data?.refused ?? null };
}
