import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AnswerDealRequest } from "@/types";
import { useRenewBase } from "./useRenewBase";

/** O presidente responde à cobrança da bancada: aceita o preço novo ou deixa o partido sair da base. */
export function useAnswerDemand() {
  const renew = useRenewBase();

  return useMutation({
    mutationFn: ({ dealId, ...body }: AnswerDealRequest & { dealId: number }) =>
      apiFetch(`/api/government/deals/${dealId}/demand`, { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
