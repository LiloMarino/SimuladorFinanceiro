import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundFeesRequest, FundSummary } from "@/types";
import { fundKeys } from "../fund-keys";

/** Muda as taxas: as novas ficam pendentes e valem no primeiro dia útil do mês seguinte. */
export function useSetFundFees(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: FundFeesRequest) =>
      apiFetch<FundSummary>(`/api/funds/${fundId}/fees`, { method: "PUT", body: request }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
