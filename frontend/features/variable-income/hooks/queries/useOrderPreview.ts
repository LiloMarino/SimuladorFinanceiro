import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { OrderPreview, OrderPreviewRequest } from "@/types";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import ApiError from "@/shared/lib/models/ApiError";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import { outcomeOfPreviewEvent, previewMatchesDraft, type OrderPreviewOutcome } from "../../lib/asset-feed";

// Status com que a API recusa uma ordem que não cabe
const REFUSED_STATUS = 422;

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
    void applyRealtime<OrderPreviewOutcome>(queryClient, queryKey, outcomeOfPreviewEvent(event));
  });

  const { data, error, isLoading, refetch } = useQuery({
    queryKey,
    queryFn: async ({ signal }): Promise<OrderPreviewOutcome> => {
      try {
        const preview = await apiFetch<OrderPreview>(`/api/variable-income/${ticker}/order-preview`, {
          method: "POST",
          body: request,
          signal,
          activeAccount: true,
        });
        return { preview, refused: null };
      } catch (failure) {
        // A recusa da ordem é dado da prévia, igual ao aviso; as demais falhas ficam como erro da consulta
        if (failure instanceof ApiError && failure.status === REFUSED_STATUS) {
          return { preview: null, refused: failure.message };
        }
        throw failure;
      }
    },
    staleTime: 0,
  });

  return { preview: data?.preview ?? undefined, refused: data?.refused ?? null, error, isLoading, refetch };
}
