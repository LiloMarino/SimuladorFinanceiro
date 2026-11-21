import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ViceInviteRequest } from "@/types";

/** O fundador convida um jogador da sala para vice da chapa. */
export function useInviteVice() {
  return useMutation({
    mutationFn: (body: ViceInviteRequest) => apiFetch("/api/government/parties/vice", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
