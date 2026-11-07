import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { PreparationFederationAnswer, Preparations } from "@/types";

/** O fundador convidado aceita ou recusa a federação que outro fundador propôs no lobby. */
export function useAnswerPreparationFederation() {
  return useMutation({
    mutationFn: (body: PreparationFederationAnswer) =>
      apiFetch<Preparations>("/api/simulation/players/me/preparation/federation/answer", { method: "PUT", body }),
  });
}
