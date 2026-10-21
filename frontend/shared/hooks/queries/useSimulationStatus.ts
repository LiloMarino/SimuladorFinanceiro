import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SimulationInfo } from "@/types";

export function useSimulationStatus() {
  return useQuery({
    queryKey: queryKeys.simulationStatus(),
    queryFn: ({ signal }) => apiFetch<SimulationInfo>("/api/simulation/status", { signal }),
    staleTime: 1 * 60 * 1000, // 1min (simulação muda mais rápido)
    gcTime: 5 * 60 * 1000, // 5min cache
  });
}
