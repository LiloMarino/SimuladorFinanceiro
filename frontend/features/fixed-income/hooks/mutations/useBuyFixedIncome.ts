import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { BuyFixedIncomeRequest } from "@/types";

export function useBuyFixedIncome(assetId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: BuyFixedIncomeRequest) =>
      apiFetch(`/api/fixed-income/${assetId}/buy`, { method: "POST", body }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationState() });
    },
    onError: (err) => toastApiError(err),
  });
}
