import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { OrderPreview, OrderPreviewRequest } from "@/types";

/** O que a ordem faria com o caixa e o IR, antes de enviar. Mantém a prévia anterior enquanto a nova chega. */
export function useOrderPreview(ticker: string, request: OrderPreviewRequest) {
  return useQuery({
    queryKey: queryKeys.orderPreview(ticker, request),
    queryFn: ({ signal }) =>
      apiFetch<OrderPreview>(`/api/variable-income/${ticker}/order-preview`, { method: "POST", body: request, signal }),
    placeholderData: keepPreviousData,
  });
}
