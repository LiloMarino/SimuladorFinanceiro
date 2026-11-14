import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "../fund-keys";

/** Retira do mercado as cotas da oferta que ainda não foram vendidas. */
export function useCloseFundOffer(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>(`/api/funds/${fundId}/offer`, { method: "DELETE" }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
