import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PartyContribution } from "@/types";

/** Grava no perfil a contribuição mensal ao partido. */
export function useSavePartyContribution() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (amount: string) =>
      apiFetch<PartyContribution>("/api/settings/party/contribution", { method: "PUT", body: { amount } }),
    onSuccess: (saved) => queryClient.setQueryData(queryKeys.partyContribution(), saved),
  });
}
