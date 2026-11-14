import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "../fund-keys";

/** Tira do livro o resto da recompra; o que já foi comprado fica queimado. */
export function useCancelFundBuyback(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>(`/api/funds/${fundId}/buyback`, { method: "DELETE" }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
