import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AnswerDealRequest } from "@/types";

/** O líder do partido responde à proposta de acordo. */
export function useAnswerDeal() {
  return useMutation({
    mutationFn: (body: AnswerDealRequest) => apiFetch("/api/government/deals/answer", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
