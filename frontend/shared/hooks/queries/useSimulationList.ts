import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SimulationListItem } from "@/types";

export function useSimulationList({ refetchOnMount = true }: { refetchOnMount?: boolean | "always" } = {}) {
  return useQuery({
    queryKey: queryKeys.simulationList(),
    queryFn: ({ signal }) => apiFetch<SimulationListItem[]>("/api/simulation/list", { signal }),
    refetchOnMount,
  });
}
