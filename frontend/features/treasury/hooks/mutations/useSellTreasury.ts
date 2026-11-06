import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SellTreasuryRequest } from "@/types";

export function useSellTreasury(assetId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: SellTreasuryRequest) => apiFetch(`/api/treasury/${assetId}/sell`, { method: "POST", body }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.treasuryPositions() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationState() });
    },
    onError: (err) => toastApiError(err),
  });
}
