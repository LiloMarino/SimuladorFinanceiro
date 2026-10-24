import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { revalidateOrder } from "@/shared/lib/simulation-cache";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SubmitOrderRequest, SubmitOrderResponse } from "@/types";

/** Compra a mercado: por valor o aviso vem sempre; por quantidade, só quando saiu menos que o pedido. */
export function notifyExecution(ticker: string, order: SubmitOrderRequest, response: SubmitOrderResponse) {
  const executed = Number(response.quantity);
  const total = Number(response.total);
  if (order.amount != null) {
    toast.info(
      `Comprou ${displayQuantity(response.quantity)} ${ticker} por ${displayMoney(total)} · sobraram ${displayMoney(Number(order.amount) - total)}.`,
    );
    return;
  }
  if (order.quantity != null && executed < Number(order.quantity)) {
    toast.info(
      `Comprou ${displayQuantity(response.quantity)} de ${displayQuantity(String(order.quantity))} ${ticker}: o preço subiu para ${displayMoney(total / executed)}.`,
    );
  }
}

export function useSubmitOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (order: SubmitOrderRequest) =>
      apiFetch<SubmitOrderResponse>(`/api/variable-income/${ticker}/orders`, { method: "POST", body: order }),
    onSuccess: (response, order) => {
      if (order.type === "market" && order.action === "buy") notifyExecution(ticker, order, response);
    },
    onSettled: () => revalidateOrder(queryClient, ticker),
    onError: (err) => toastApiError(err),
  });
}
