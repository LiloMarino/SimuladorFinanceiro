import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useClearSimulationSelection() {
  return useMutation({
    mutationFn: () => apiFetch<void>("/api/simulation/selection", { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
