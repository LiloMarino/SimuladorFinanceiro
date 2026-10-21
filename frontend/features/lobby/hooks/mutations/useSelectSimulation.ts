import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

export function useSelectSimulation() {
  return useMutation({
    mutationFn: (id: number) => apiFetch<void>("/api/simulation/selection", { method: "PUT", body: { id } }),
    onError: (err) => toastApiError(err),
  });
}
