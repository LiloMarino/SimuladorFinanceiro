import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** Marca como lidas todas as entradas do jogador. */
export function useMarkInboxRead(simulationId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/inbox/read", { method: "POST", body: {} }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.inbox(simulationId) }),
    onError: (err) => toastApiError(err),
  });
}
