import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useStopSimulation() {
  return useMutation({
    mutationFn: () => apiFetch("/api/simulation/stop", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
