import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FutureParams, GeneratedFuture } from "@/types";

/** Gera e grava o futuro em todas as séries; o progresso chega pelo evento `future_recording_progress`. */
export function useRecordFuture() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: FutureParams) =>
      apiFetch<GeneratedFuture>("/api/import-assets/future", { method: "POST", body: params }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.generatedFuture() });
    },
  });
}
