import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundDirectedIssuanceRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** Emite cotas novas dirigidas: para o próprio gestor liquida na hora, para um co-gestor vira oferta que ele responde. */
export function useIssueDirectedFundQuotas(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundDirectedIssuanceRequest) =>
      apiFetch<void>(`/api/funds/${fundId}/directed-issuance`, { method: "POST", body: request }),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: fundKeys.all() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
    },
    onError: (err) => toastApiError(err),
  });
}
