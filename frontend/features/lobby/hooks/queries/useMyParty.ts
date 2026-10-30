import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PartyIdentity } from "@/types";

/** O Meu partido salvo no perfil; nulo enquanto o jogador não salvou um. */
export function useMyParty() {
  return useQuery({
    queryKey: queryKeys.myParty(),
    queryFn: ({ signal }) => apiFetch<PartyIdentity | null>("/api/settings/party", { signal }),
  });
}
