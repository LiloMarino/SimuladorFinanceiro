import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useUnmarkStateOwned(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${ticker}/state`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateOwned(ticker) });
    },
  });
}
