import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { JoinPartyRequest } from "@/types";

export function useJoinParty(partyId: number) {
  return useMutation({
    mutationFn: (body: JoinPartyRequest) =>
      apiFetch(`/api/government/parties/${partyId}/members`, { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
