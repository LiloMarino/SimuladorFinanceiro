import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useRemoveStockSegment(key: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${key}/segment`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.sectors() });
    },
  });
}
