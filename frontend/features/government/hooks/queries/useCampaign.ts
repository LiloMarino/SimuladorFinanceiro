import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CampaignPanel } from "@/types";

/** O cartão das ações de campanha do partido de quem vê: preços, faixas do dado e retorno de hoje. */
export function useCampaign() {
  return useQuery({
    queryKey: queryKeys.campaign(),
    queryFn: ({ signal }) => apiFetch<CampaignPanel>("/api/government/campaign", { signal }),
  });
}
