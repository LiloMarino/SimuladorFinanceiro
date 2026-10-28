import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PartyFlagsRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useSetPartyFlags() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: PartyFlagsRequest) => apiFetch("/api/government/parties/flags", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
