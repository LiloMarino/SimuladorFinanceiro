import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { Preparations } from "@/types";

/** O que cada jogador da sala preparou para a campanha, mantido vivo por preparations_update. */
export function usePreparations() {
  const queryClient = useQueryClient();
  const key = queryKeys.preparations();

  const query = useQuery({
    queryKey: key,
    queryFn: ({ signal }) => apiFetch<Preparations>("/api/simulation/preparations", { signal }),
  });

  useRealtime("preparations_update", (preparations) => queryClient.setQueryData(key, preparations));

  // Quem entra ou sai da sala e as regras da partida mudam as travas e os conflitos
  const refresh = () => void queryClient.invalidateQueries({ queryKey: key });
  useRealtime("player_join", refresh);
  useRealtime("player_exit", refresh);
  useRealtime("simulation_selected", refresh);
  useRealtime("simulation_settings_update", refresh);

  return query;
}
