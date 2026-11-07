import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { PreparationFederationOffer, Preparations } from "@/types";

/** O fundador propõe federação a outro fundador da sala; sem parceiro, retira a proposta ou desfaz a combinada. */
export function useProposePreparationFederation() {
  return useMutation({
    mutationFn: (body: PreparationFederationOffer) =>
      apiFetch<Preparations>("/api/simulation/players/me/preparation/federation", { method: "PUT", body }),
  });
}
