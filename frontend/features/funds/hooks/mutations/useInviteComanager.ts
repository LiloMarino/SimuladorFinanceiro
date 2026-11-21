import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundComanagerInviteRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O gestor convida um jogador para co-gestor: o convite reserva a parte e vale por sete dias. */
export function useInviteComanager(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundComanagerInviteRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/comanagers`, { method: "POST", body: request }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
