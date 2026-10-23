import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { NAME_TAKEN_STATUS } from "../../lib/preset";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { Preset, SavePresetRequest } from "@/types";

export function useSavePreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: SavePresetRequest) => apiFetch<Preset>("/api/presets", { method: "POST", body }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.presets() }),
    // Nome repetido volta como erro do campo, no diálogo
    onError: (err) => {
      if (err.status !== NAME_TAKEN_STATUS) toastApiError(err);
    },
  });
}
