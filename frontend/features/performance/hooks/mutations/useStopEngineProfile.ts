import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { EngineProfileSaved } from "@/types";

/** Para a gravação; devolve o caminho do `.prof` gravado. */
export function useStopEngineProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<EngineProfileSaved>("/api/debug/profile/engine/stop", { method: "POST", body: {} }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.debugEngineProfile() }),
    onError: (err) => toastApiError(err),
  });
}
