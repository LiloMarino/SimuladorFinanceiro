import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AnswerFederationRequest } from "@/types";

/** O fundador do partido convidado responde à proposta de federação. */
export function useAnswerFederation() {
  return useMutation({
    mutationFn: (body: AnswerFederationRequest) =>
      apiFetch("/api/government/federations/answer", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
