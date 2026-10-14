import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";

type RoomPlayer = { nickname: string };

/** Jogadores conectados à sala, mantido vivo via player_join/player_exit. */
export function useRoomPlayers() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.simulationPlayers(),
    queryFn: ({ signal }) => apiFetch<RoomPlayer[]>("/api/simulation/players", { signal }),
  });

  useRealtime("player_join", ({ nickname }) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) => {
      if (!prev) return [{ nickname }];

      if (prev.some((p) => p.nickname === nickname)) {
        return prev;
      }

      return [...prev, { nickname }];
    });
  });

  useRealtime("player_exit", ({ nickname }) => {
    queryClient.setQueryData(queryKeys.simulationPlayers(), (prev: RoomPlayer[] | undefined) => {
      if (!prev) return prev;
      return prev.filter((p) => p.nickname !== nickname);
    });
  });

  return query;
}
