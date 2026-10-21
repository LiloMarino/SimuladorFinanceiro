import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { CreateSimulationRequest, SimulationInfo } from "@/types";

export function useCreateSimulation() {
  return useMutation({
    mutationFn: (body: CreateSimulationRequest) =>
      apiFetch<SimulationInfo>("/api/simulation/create", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
