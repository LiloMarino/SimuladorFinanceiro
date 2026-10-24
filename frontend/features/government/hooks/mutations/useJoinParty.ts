import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { JoinPartyRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useJoinParty(partyId: number) {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: JoinPartyRequest) =>
      apiFetch(`/api/government/parties/${partyId}/members`, { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
