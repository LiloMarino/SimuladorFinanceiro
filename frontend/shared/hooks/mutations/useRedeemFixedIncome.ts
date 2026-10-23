import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RedeemFixedIncomeRequest } from "@/types";

export function useRedeemFixedIncome(assetId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: RedeemFixedIncomeRequest) =>
      apiFetch(`/api/fixed-income/${assetId}/redeem`, { method: "POST", body }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationState() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.fixedIncomeAsset(assetId) });
    },
    onError: (err) => toastApiError(err),
  });
}
