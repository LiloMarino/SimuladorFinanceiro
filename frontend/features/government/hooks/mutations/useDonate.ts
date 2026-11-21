import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { DonationRequest } from "@/types";

export function useDonate() {
  return useMutation({
    mutationFn: (body: DonationRequest) => apiFetch("/api/government/donations", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
