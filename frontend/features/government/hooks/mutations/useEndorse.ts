import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { EndorsementRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useEndorse() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: EndorsementRequest) => apiFetch("/api/government/runoff/endorsement", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
