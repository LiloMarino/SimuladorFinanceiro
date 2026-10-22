import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { OrderPreview, OrderPreviewRequest } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

/** A prévia acompanha o book e o saldo, inclusive quando não há novos ticks. */
export function useOrderPreview(ticker: string, request: OrderPreviewRequest) {
  const queryClient = useQueryClient();
  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.orderPreview(ticker) });
  };
  useRealtime("cash_update", refresh);
  useRealtime(`position_update:${ticker}`, refresh);
  useRealtime(`order_book_snapshot:${ticker}`, refresh);
  useRealtime(`order_added:${ticker}`, refresh);
  useRealtime(`order_updated:${ticker}`, refresh);
  return useQuery({
    queryKey: queryKeys.orderPreview(ticker, request),
    queryFn: ({ signal }) =>
      apiFetch<OrderPreview>(`/api/variable-income/${ticker}/order-preview`, { method: "POST", body: request, signal }),
    staleTime: 0,
  });
}
