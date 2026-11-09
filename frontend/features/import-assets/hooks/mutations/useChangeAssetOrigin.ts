import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AssetOrigin } from "@/types";

export function useChangeAssetOrigin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticker, value }: { ticker: string; value: AssetOrigin }) =>
      apiFetch(`/api/import-assets/stocks/${ticker}/origin`, { method: "PUT", body: { origin: value } }),
    onError: (err) => toastApiError(err),
    onSettled: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
        queryClient.invalidateQueries({ queryKey: queryKeys.variableIncome() }),
      ]),
  });
}
