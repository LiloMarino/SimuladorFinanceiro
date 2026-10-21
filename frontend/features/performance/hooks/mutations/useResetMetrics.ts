import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

export function useResetMetrics() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/debug/metrics/reset", { method: "POST", body: {} }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.debugMetrics() }),
  });
}
