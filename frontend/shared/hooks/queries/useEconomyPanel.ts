import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { EconomyPanel } from "@/types";

/**
 * A SELIC, o IPCA e o juro real desde o início da partida: cada dia do pregão e cada ação do
 * governo trazem o painel por economy_update. O cache vale enquanto a tela escuta o evento; a
 * cada montagem a consulta confere de novo.
 */
export function useEconomyPanel() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.economyPanel(),
    queryFn: ({ signal }) => apiFetch<EconomyPanel>("/api/economy", { signal }),
    staleTime: 0,
  });

  useRealtime("economy_update", (panel) => {
    queryClient.setQueryData(queryKeys.economyPanel(), panel);
  });

  return query;
}
