import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O co-gestor sai da gestão: o acesso acaba no mesmo pregão. */
export function useLeaveComanagement(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>(`/api/funds/${fundId}/comanagers/me`, { method: "DELETE" }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
