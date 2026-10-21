import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SeriesCoverage } from "@/types";

export function useRefreshSeries() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (item: SeriesCoverage) =>
      item.kind === "INDICATOR"
        ? apiFetch(`/api/import-assets/indicators/${item.key}`, { method: "POST" })
        : apiFetch("/api/import-assets/yfinance", { method: "POST", body: { ticker: item.key, overwrite: false } }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
