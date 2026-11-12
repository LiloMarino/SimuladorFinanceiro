import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { EconomyPanel } from "@/types";

const REFRESH_MS = 15_000;

/** A SELIC, o IPCA e o juro real desde o início da partida; renova enquanto a tela está aberta. */
export function useEconomyPanel() {
  return useQuery({
    queryKey: queryKeys.economyPanel(),
    queryFn: ({ signal }) => apiFetch<EconomyPanel>("/api/economy", { signal }),
    refetchInterval: REFRESH_MS,
  });
}
