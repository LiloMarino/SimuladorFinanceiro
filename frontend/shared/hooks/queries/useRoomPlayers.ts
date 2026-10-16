import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { RoomPlayer } from "@/types";

/** Jogadores conectados à sala com a cor de cada um, mantido vivo via player_join/player_exit/player_color. */
export function useRoomPlayers() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.simulationPlayers(),
    queryFn: ({ signal }) => apiFetch<RoomPlayer[]>("/api/simulation/players", { signal }),
  });

  useRealtime("player_join", (player) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) => {
      if (!prev) return [player];

      if (prev.some((p) => p.nickname === player.nickname)) {
        return prev;
      }

      return [...prev, player];
    });
  });

  useRealtime("player_exit", ({ nickname }) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) => {
      if (!prev) return prev;
      return prev.filter((p) => p.nickname !== nickname);
    });
  });

  useRealtime("player_color", (player) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) =>
      prev?.map((p) => (p.nickname === player.nickname ? player : p)),
    );
  });

  return query;
}
