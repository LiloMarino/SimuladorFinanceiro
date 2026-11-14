import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundFoundRequest, FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

/** Funda a gestora: nasce sem cotas, e quem integraliza depois é o gestor. */
export function useFoundFund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundFoundRequest) => apiFetch<FundSummary>("/api/funds", { method: "POST", body: request }),
    // A conta da gestora nasce junto: o menu e o caixa dela passam a listá-la
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.fundAccounts() }),
      ]),
    onError: (err) => toastApiError(err),
  });
}
