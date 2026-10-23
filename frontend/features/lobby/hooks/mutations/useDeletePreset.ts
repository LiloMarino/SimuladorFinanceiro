import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useDeletePreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (presetId: number) => apiFetch<void>(`/api/presets/${presetId}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.presets() }),
    onError: (err) => toastApiError(err),
  });
}
