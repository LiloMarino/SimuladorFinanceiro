import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { BacktestStopped } from "@/types";

/** Para o backtest e o deixa salvo até onde chegou; devolve o id da partida salva. */
export function useStopBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<BacktestStopped>("/api/backtest/stop", { method: "POST" }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
    },
    onError: (err) => toastApiError(err),
  });
}
