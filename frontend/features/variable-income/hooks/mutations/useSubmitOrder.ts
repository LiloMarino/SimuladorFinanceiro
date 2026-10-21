import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SubmitOrderRequest, SubmitOrderResponse } from "@/types";

export function useSubmitOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: SubmitOrderRequest) =>
      apiFetch<SubmitOrderResponse>(`/api/variable-income/${ticker}/orders`, { method: "POST", body: order }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.portfolioPosition(ticker) }),
    onError: (err) => toastApiError(err),
  });
}
