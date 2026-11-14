import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundIssuanceRequest } from "@/types";
import { fundKeys } from "../fund-keys";

/** Anuncia a emissão: cotas novas ao patrimônio por cota do dia, com preferência para quem já é cotista. */
export function useAnnounceFundIssuance(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundIssuanceRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/issuance`, { method: "POST", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
