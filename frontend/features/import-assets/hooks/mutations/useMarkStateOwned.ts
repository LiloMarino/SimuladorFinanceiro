import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { StateOwnedStockRequest } from "@/types";

export function useMarkStateOwned(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: StateOwnedStockRequest) =>
      apiFetch(`/api/import-assets/stocks/${ticker}/state`, { method: "PUT", body }),
    onError: (err) => toastApiError(err),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateOwned(ticker) });
    },
  });
}
