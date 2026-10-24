import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { DonationRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useDonate() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: DonationRequest) => apiFetch("/api/government/donations", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
