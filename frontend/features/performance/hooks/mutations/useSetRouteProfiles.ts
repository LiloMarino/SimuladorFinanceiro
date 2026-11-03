import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useSetRouteProfiles() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (enabled: boolean) => apiFetch<void>("/api/debug/profile/routes", { method: "PUT", body: { enabled } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.debugRouteProfiles() }),
    onError: (err) => toastApiError(err),
  });
}
