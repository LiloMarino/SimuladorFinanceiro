import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FoundPartyRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useFoundParty() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: FoundPartyRequest) => apiFetch("/api/government/parties", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
