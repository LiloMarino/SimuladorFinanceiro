import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useDeleteStock() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ticker: string) =>
      apiFetch(`/api/import-assets/stocks/${encodeURIComponent(ticker)}`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.sectors() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.generatedFuture() });
    },
  });
}
