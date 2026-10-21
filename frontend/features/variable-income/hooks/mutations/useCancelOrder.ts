import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useCancelOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) =>
      apiFetch<void>(`/api/variable-income/${ticker}/orders`, { method: "DELETE", body: { order_id: orderId } }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.variableIncomeOrders(ticker) }),
  });
}
