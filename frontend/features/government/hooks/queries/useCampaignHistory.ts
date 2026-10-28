import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CampaignHistory } from "@/types";

/** Cada ação do partido na campanha, a verba de base e os ataques recebidos. */
export function useCampaignHistory({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.campaignHistory(),
    queryFn: ({ signal }) => apiFetch<CampaignHistory>("/api/government/campaign/history", { signal }),
    enabled,
  });
}
