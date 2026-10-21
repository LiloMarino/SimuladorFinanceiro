import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { MetricsData } from "@/types";
import { REFRESH_MS } from "../../lib/stats";

/**
 * Lê as medições a cada 2 s; pausado, a tabela fica parada para dar tempo de ler.
 * `enabled` espera o servidor confirmar o modo debug (sem ele a rota nem existe).
 */
export function useMetrics({
  paused,
  enabled,
}: {
  paused: boolean;
  enabled: boolean;
}) {
  return useQuery({
    enabled,
    queryKey: queryKeys.debugMetrics(),
    queryFn: ({ signal }) =>
      apiFetch<MetricsData>("/api/debug/metrics", { signal }),
    // Sem nenhum dado e com erro, o polling só faria a tela alternar entre esqueleto e erro:
    // para até o "Tentar de novo". Com dados antigos na tela, segue tentando.
    refetchInterval: (query) =>
      paused || (query.state.status === "error" && !query.state.data) ? false : REFRESH_MS,
    placeholderData: keepPreviousData,
  });
}

export function useResetMetrics() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch<void>("/api/debug/metrics/reset", { method: "POST", body: {} }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.debugMetrics() }),
  });
}
