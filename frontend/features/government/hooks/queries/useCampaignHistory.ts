import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { CampaignHistory } from "@/types";

/** Cada ação do partido na campanha, a verba de base e os ataques recebidos; cada ação nova chega por campaign_history_update. */
export function useCampaignHistory({ enabled = true }: { enabled?: boolean } = {}) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.campaignHistory(),
    queryFn: ({ signal }) => apiFetch<CampaignHistory>("/api/government/campaign/history", { signal }),
    enabled,
    staleTime: 0,
  });

  useRealtime(
    "campaign_history_update",
    (history) => {
      void applyRealtime<CampaignHistory>(queryClient, queryKeys.campaignHistory(), history);
    },
    enabled,
  );

  return query;
}
