import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useStartEngineProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/debug/profile/engine/start", { method: "POST", body: {} }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.debugEngineProfile() }),
    onError: (err) => toastApiError(err),
  });
}
