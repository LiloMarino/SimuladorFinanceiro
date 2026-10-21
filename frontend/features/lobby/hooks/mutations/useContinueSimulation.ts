import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SimulationInfo } from "@/types";

export function useContinueSimulation() {
  return useMutation({
    mutationFn: () => apiFetch<SimulationInfo>("/api/simulation/continue", { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
