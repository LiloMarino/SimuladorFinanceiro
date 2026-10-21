import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ImportResult, ReplacedGenerated, SeriesCoverage } from "@/types";
import { toastReplacedGenerated } from "../../lib/replaced-toast";

export function useRefreshSeries() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (item: SeriesCoverage): Promise<ReplacedGenerated | null> =>
      item.kind === "INDICATOR"
        ? apiFetch<ReplacedGenerated | null>(`/api/import-assets/indicators/${item.key}`, { method: "POST" })
        : (
            await apiFetch<ImportResult>("/api/import-assets/yfinance", {
              method: "POST",
              body: { ticker: item.key, overwrite: false },
            })
          ).replaced,
    onSuccess: (replaced, item) => toastReplacedGenerated(item.key, replaced),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
