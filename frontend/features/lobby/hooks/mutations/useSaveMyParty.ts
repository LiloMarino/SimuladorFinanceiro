import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PartyIdentity } from "@/types";

/** Grava o Meu partido no perfil do jogador. */
export function useSaveMyParty() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: PartyIdentity) => apiFetch<PartyIdentity>("/api/settings/party", { method: "PUT", body }),
    onSuccess: (saved) => queryClient.setQueryData(queryKeys.myParty(), saved),
  });
}
