import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { SimulationState } from "@/types";

/**
 * Estado "ao vivo" da simulação (data atual, velocidade, saldo em caixa).
 * Busca inicial via REST, mantido atualizado via simulation_update/speed_update/cash_update.
 * Dono único da assinatura WS desses eventos — múltiplos componentes que chamam
 * este hook compartilham uma única busca e uma única assinatura (dedup por queryKey).
 */
export function useSimulationState() {
  const queryClient = useQueryClient();

  const query = useApiQuery({
    queryKey: queryKeys.simulationState(),
    queryFn: ({ signal }) => apiFetch<SimulationState>("/api/get-simulation-state", { signal }),
  });

  const patch = (update: Partial<SimulationState>) => {
    queryClient.setQueryData(queryKeys.simulationState(), (prev: SimulationState | undefined) => ({
      ...prev,
      ...update,
    }));
  };

  useRealtime("simulation_update", patch);
  useRealtime("speed_update", patch);
  useRealtime("cash_update", patch);

  return query;
}
