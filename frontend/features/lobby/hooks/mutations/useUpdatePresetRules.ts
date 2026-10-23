import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { Preset, SavePresetRequest } from "@/types";

/** Grava as regras de agora por cima de um preset do host. */
export function useUpdatePresetRules() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ presetId, rules }: { presetId: number; rules: SavePresetRequest["rules"] }) =>
      apiFetch<Preset>(`/api/presets/${presetId}/rules`, { method: "PUT", body: { rules } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.presets() }),
    onError: (err) => toastApiError(err),
  });
}
