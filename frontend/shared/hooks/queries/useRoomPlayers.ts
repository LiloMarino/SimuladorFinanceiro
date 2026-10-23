import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { RoomPlayer } from "@/types";

/** Jogadores conectados à sala com a cor e a equipe de cada um, mantido vivo via player_join/player_exit/player_color/player_team/player_activity/player_bot. */
export function useRoomPlayers() {
  const queryClient = useQueryClient();

  const query = useQuery({
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

  useRealtime("player_team", (player) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) =>
      prev?.map((p) => (p.nickname === player.nickname ? player : p)),
    );
  });

  useRealtime("player_activity", (player) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) =>
      prev?.map((p) => (p.nickname === player.nickname ? player : p)),
    );
  });

  // Configurar um bot pode trocar o nome: previous_nickname diz qual cartão substituir
  useRealtime("player_bot", ({ previous_nickname, ...player }) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) =>
      prev?.map((p) => (p.nickname === (previous_nickname ?? player.nickname) ? player : p)),
    );
  });

  return query;
}
