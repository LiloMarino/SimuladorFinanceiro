import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GoalProgress } from "@/types";

/**
 * Onde cada jogador está na corrida à meta. Busca inicial via REST, atualizado a cada
 * pregão por goal_progress_update. Na Clássica não há corrida: a busca nem sai e o dado
 * fica indefinido. O cache é por partida, então uma partida nova nunca herda a anterior.
 */
export function useGoalProgress() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;
  const racing = !!current && current.game_type !== "CLASSIC";
  const simulationId = current?.id ?? 0;

  const query = useApiQuery({
    queryKey: queryKeys.goalProgress(simulationId),
    queryFn: ({ signal }) => apiFetch<GoalProgress>("/api/simulation/goal-progress", { signal }),
    enabled: racing,
  });

  useRealtime(
    "goal_progress_update",
    (progress) => queryClient.setQueryData(queryKeys.goalProgress(simulationId), progress),
    racing,
  );

  return query;
}
