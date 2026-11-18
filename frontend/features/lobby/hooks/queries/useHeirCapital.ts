import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { HeirCapital } from "@/types";

/** O capital inicial do Herdeiro pelas regras da sala; muda junto com elas. */
export function useHeirCapital() {
  const queryClient = useQueryClient();

  useRealtime("simulation_settings_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.heirCapital() });
  });

  return useQuery({
    queryKey: queryKeys.heirCapital(),
    queryFn: ({ signal }) => apiFetch<HeirCapital>("/api/simulation/heir-capital", { signal }),
    refetchOnMount: "always",
  });
}
