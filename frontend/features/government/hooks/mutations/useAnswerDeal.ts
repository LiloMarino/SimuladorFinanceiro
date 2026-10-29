import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AnswerDealRequest } from "@/types";
import { useRenewBase } from "./useRenewBase";

/** O líder do partido responde à proposta de acordo. */
export function useAnswerDeal() {
  const renew = useRenewBase();

  return useMutation({
    mutationFn: (body: AnswerDealRequest) => apiFetch("/api/government/deals/answer", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
