import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ProposeFederationRequest } from "@/types";

/** O fundador propõe a federação a outro partido. */
export function useProposeFederation() {
  return useMutation({
    mutationFn: (body: ProposeFederationRequest) => apiFetch("/api/government/federations", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
