import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { revalidateOrder } from "@/shared/lib/simulation-cache";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SubmitOrderRequest, SubmitOrderResponse } from "@/types";

export function useSubmitOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: SubmitOrderRequest) =>
      apiFetch<SubmitOrderResponse>(`/api/variable-income/${ticker}/orders`, { method: "POST", body: order }),
    onSettled: () => revalidateOrder(queryClient, ticker),
    onError: (err) => toastApiError(err),
  });
}
