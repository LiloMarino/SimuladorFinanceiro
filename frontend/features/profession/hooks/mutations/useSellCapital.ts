import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { CapitalSaleRequest } from "@/types";

/** Vende parte do capital da empresa do Empreendedor; a página, o caixa, a carteira e o histórico leem de novo. */
export function useSellCapital() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;
  const simulationId = current?.id ?? 0;

  return useMutation({
    mutationFn: (body: CapitalSaleRequest) => apiFetch("/api/simulation/sell-capital", { method: "POST", body }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.profession(simulationId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.lifeStatusAll() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.lifeHistoryAll(simulationId) });
    },
    onError: (err) => toastApiError(err),
  });
}
