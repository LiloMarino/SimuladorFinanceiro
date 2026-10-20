import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GoalProgress } from "@/types";

function currentMatchId(simulation: ReturnType<typeof useSimulation>["simulation"]) {
  const current = simulation?.active ? simulation.simulation : null;
  return { current, simulationId: current?.id ?? 0 };
}

/**
 * Onde cada jogador está na corrida à meta. Busca inicial via REST, atualizado a cada
 * pregão por goal_progress_update. Na Clássica não há corrida: a busca nem sai e o dado
 * fica indefinido. O cache é por partida, então uma partida nova nunca herda a anterior.
 * A meta subir de um pregão para o outro é o reajuste pelo IPCA: o relatório (de onde sai
 * a meta em degraus) e a vida financeira são renovados no mesmo instante.
 */
export function useGoalProgress() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const { current, simulationId } = currentMatchId(simulation);
  const racing = !!current && current.game_type !== "CLASSIC";

  const query = useApiQuery({
    queryKey: queryKeys.goalProgress(simulationId),
    queryFn: ({ signal }) => apiFetch<GoalProgress>("/api/simulation/goal-progress", { signal }),
    enabled: racing,
  });

  useRealtime(
    "goal_progress_update",
    (progress) => {
      const previous = queryClient.getQueryData<GoalProgress>(queryKeys.goalProgress(simulationId));
      queryClient.setQueryData(queryKeys.goalProgress(simulationId), progress);
      if (!previous || Number(progress.goal) <= Number(previous.goal)) return;

      void queryClient.invalidateQueries({ queryKey: queryKeys.statistics() });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeStatus(simulationId),
      });
    },
    racing,
  );

  return query;
}
