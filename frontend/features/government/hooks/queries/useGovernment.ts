import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GovernmentView } from "@/types";
import { revalidateGovernmentImpact } from "@/shared/lib/simulation-cache";

export function useGovernment() {
  const { simulation } = useSimulation();
  const match = simulation?.simulation;
  const client = useQueryClient();
  const key = queryKeys.government(match?.id ?? 0);
  return useQuery({
    queryKey: key,
    queryFn: async ({ signal }) => {
      const data = await apiFetch<GovernmentView>("/api/government", { signal });
      const before = client.getQueryData<GovernmentView>(key);
      if (before && before.state.revision !== data.state.revision) void revalidateGovernmentImpact(client);
      return data;
    },
    enabled: !!simulation?.active && !!match?.government?.enabled,
    staleTime: 1000,
    refetchInterval: 2500,
  });
}
