import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useRefreshOutdatedStocks() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tickers: string[]) =>
      apiFetch("/api/import-assets/yfinance/batch", { method: "POST", body: { tickers, overwrite: false } }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
