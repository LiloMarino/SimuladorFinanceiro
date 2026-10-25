import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { GovernmentPanel } from "@/types";

/** Impostos em vigor, aprovação, fila do Congresso e a carteira do presidente. */
export function useGovernment({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.government(),
    queryFn: ({ signal }) => apiFetch<GovernmentPanel>("/api/government", { signal }),
    enabled,
  });
}
