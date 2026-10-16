import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { RoomPlayer } from "@/types";

/** Quem joga a partida em andamento, online ou não, com a cor de cada um; refeito quando alguém entra. */
export function useMatchPlayers() {
  const queryClient = useQueryClient();

  const refresh = () => void queryClient.invalidateQueries({ queryKey: queryKeys.matchPlayers() });
  useRealtime("player_join", refresh);
  useRealtime("player_color", refresh);

  return useApiQuery({
    queryKey: queryKeys.matchPlayers(),
    queryFn: ({ signal }) => apiFetch<RoomPlayer[]>("/api/simulation/match-players", { signal }),
  });
}
