import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { CampaignPanel } from "@/types";

/** O cartão das ações de campanha do partido de quem vê: preços, faixas do dado e retorno de hoje; cada mudança do governo o traz por campaign_update. */
export function useCampaign() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.campaign(),
    queryFn: ({ signal }) => apiFetch<CampaignPanel>("/api/government/campaign", { signal }),
    staleTime: 0,
  });

  useRealtime("campaign_update", (campaign) => {
    void applyRealtime<CampaignPanel>(queryClient, queryKeys.campaign(), campaign);
  });

  return query;
}
