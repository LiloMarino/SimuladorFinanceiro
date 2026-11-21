import { useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { OrderPreview, OrderPreviewRequest } from "@/types";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";
import { previewMatchesDraft } from "../../lib/asset-feed";

/**
 * A prévia do rascunho atual, ou o motivo de a ordem não caber. O servidor guarda o último
 * pedido e entrega o desfecho novo por `order_preview:{ticker}` a cada pregão e a cada mudança
 * de caixa, posição ou book.
 */
export function useOrderPreview(ticker: string, request: OrderPreviewRequest) {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();
  const queryKey = queryKeys.orderPreview(ticker, request);

  useRealtime(`order_preview:${ticker}`, (event) => {
    if (!previewMatchesDraft(event, request, accountKey)) return;
    void applyRealtime<PreviewOutcome<OrderPreview>>(queryClient, queryKey, outcomeOfPreviewEvent(event));
  });

  const { data, error, isLoading, refetch } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<OrderPreview>(`/api/variable-income/${ticker}/order-preview`, {
        method: "POST",
        body: request,
        signal,
        activeAccount: true,
      }),
    staleTime: 0,
  });

  return { preview: data?.preview ?? undefined, refused: data?.refused ?? null, error, isLoading, refetch };
}
