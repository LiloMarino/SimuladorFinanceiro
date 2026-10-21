import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useRefreshStockProfile(key: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch(`/api/import-assets/stocks/${key}/profile/refresh`, { method: "POST" }),
    onError: (err) => toastApiError(err),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.segmentSuggestion(key) }),
  });
}
