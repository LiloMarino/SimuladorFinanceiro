import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "../fund-keys";

/** O gestor tira o co-gestor ou retira o convite: o acesso acaba no mesmo pregão. */
export function useRemoveComanager(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => apiFetch<void>(`/api/funds/${fundId}/comanagers/${userId}`, { method: "DELETE" }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
