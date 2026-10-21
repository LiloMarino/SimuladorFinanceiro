import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AssetClass } from "@/types";

export function useChangeAssetClass() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ticker, value }: { ticker: string; value: AssetClass }) =>
      apiFetch(`/api/import-assets/stocks/${ticker}/asset-class`, { method: "PUT", body: { asset_class: value } }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });
}
