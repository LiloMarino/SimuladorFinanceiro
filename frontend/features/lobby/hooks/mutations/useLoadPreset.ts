import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PresetLoadResponse, SimulationSettings } from "@/types";

export function useLoadPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (presetId: number) => apiFetch<PresetLoadResponse>(`/api/presets/${presetId}/load`, { method: "POST" }),
    onSuccess: ({ settings, applied }) => {
      queryClient.setQueryData<SimulationSettings>(
        queryKeys.simulationSettings(),
        (prev) => prev && { ...prev, simulation: settings, applied_preset: applied },
      );
    },
    onError: (err) => toastApiError(err),
  });
}
