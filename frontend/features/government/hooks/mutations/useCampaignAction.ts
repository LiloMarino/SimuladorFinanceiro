import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { CampaignActionRequest, CampaignRoll } from "@/types";

/** Dispara uma ação de campanha; o erro aparece dentro do diálogo do dado, que é quem pede a ação. */
export function useCampaignAction() {
  return useMutation({
    mutationFn: (body: CampaignActionRequest) =>
      apiFetch<CampaignRoll>("/api/government/campaign/actions", { method: "POST", body }),
  });
}
