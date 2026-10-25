import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { SimulationSettings } from "@/types";

/** Configuração da sala. As regras mudam para todos na hora, via simulation_settings_update. */
export function useSimulationSettings() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.simulationSettings(),
    queryFn: ({ signal }) => apiFetch<SimulationSettings>("/api/simulation/settings", { signal }),
  });

  useRealtime("simulation_settings_update", (simulation) => {
    queryClient.setQueryData<SimulationSettings>(
      queryKeys.simulationSettings(),
      (prev) => prev && { ...prev, simulation },
    );
  });
  // Qual preset vale e o que mudou nele chegam juntos de cada mudança de regras
  useRealtime("preset_applied_update", ({ applied }) => {
    queryClient.setQueryData<SimulationSettings>(
      queryKeys.simulationSettings(),
      (prev) => prev && { ...prev, applied_preset: applied },
    );
  });

  return query;
}
