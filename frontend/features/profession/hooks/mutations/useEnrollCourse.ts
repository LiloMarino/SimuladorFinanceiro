import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** Matricula o jogador do Auxílio no curso técnico; a página, a vida financeira e o histórico leem de novo. */
export function useEnrollCourse() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;
  const simulationId = current?.id ?? 0;

  return useMutation({
    mutationFn: () => apiFetch("/api/simulation/enroll-course", { method: "POST" }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.profession(simulationId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.lifeStatusAll() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.lifeHistoryAll(simulationId) });
    },
    onError: (err) => toastApiError(err),
  });
}
