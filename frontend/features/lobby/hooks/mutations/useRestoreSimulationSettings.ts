import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { SimulationSettingsData } from "@/types";

export function useRestoreSimulationSettings() {
  return useMutation({
    mutationFn: () => apiFetch<SimulationSettingsData>("/api/simulation/settings", { method: "DELETE" }),
  });
}
