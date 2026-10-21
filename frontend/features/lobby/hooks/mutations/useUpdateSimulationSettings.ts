import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { SimulationSettingsData, UpdateSettingsRequest } from "@/types";

export function useUpdateSimulationSettings() {
  return useMutation({
    mutationFn: (body: UpdateSettingsRequest) =>
      apiFetch<SimulationSettingsData>("/api/simulation/settings", { method: "PUT", body }),
  });
}
