import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PartyContribution } from "@/types";

/** A contribuição mensal salva no perfil; zero enquanto o jogador não salvou uma. */
export function usePartyContribution() {
  return useQuery({
    queryKey: queryKeys.partyContribution(),
    queryFn: ({ signal }) => apiFetch<PartyContribution>("/api/settings/party/contribution", { signal }),
  });
}
