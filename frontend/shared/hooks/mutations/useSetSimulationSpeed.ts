import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { logger } from "@/shared/lib/logger";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { SetSpeedResponse, SimulationState } from "@/types";

/**
 * Muda a velocidade da partida com o cache atualizado já no clique. O evento WS speed_update
 * (via useSimulationState()) mantém os outros clientes sincronizados; o invalidate no onSettled
 * é a rede de segurança caso esse broadcast se perca. mutationKey + o guard isMutating
 * evitam que uma mutação antiga atropele o resultado de uma mais recente
 * (ver https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query).
 */
export function useSetSimulationSpeed() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: queryKeys.simulationState(),
    mutationFn: (speed: number) => apiFetch<SetSpeedResponse>("/api/set-speed", { method: "POST", body: { speed } }),
    onMutate: async (speed) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.simulationState() });
      const previous = queryClient.getQueryData<SimulationState>(queryKeys.simulationState());
      queryClient.setQueryData(queryKeys.simulationState(), (prev: SimulationState | undefined) => ({
        ...prev,
        speed,
      }));
      return { previous };
    },
    onError: (err, _speed, context) => {
      if (queryClient.isMutating({ mutationKey: queryKeys.simulationState() }) === 1) {
        queryClient.setQueryData(queryKeys.simulationState(), context?.previous);
      }
      logger.error("Erro ao alterar velocidade:", err);
    },
    onSettled: () => {
      if (queryClient.isMutating({ mutationKey: queryKeys.simulationState() }) === 1) {
        queryClient.invalidateQueries({ queryKey: queryKeys.simulationState() });
      }
    },
  });
}
