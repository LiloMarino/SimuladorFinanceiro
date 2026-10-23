import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { NAME_TAKEN_STATUS } from "../../lib/preset";
import type { Preset } from "@/types";

export function useRenamePreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ presetId, name }: { presetId: number; name: string }) =>
      apiFetch<Preset>(`/api/presets/${presetId}`, { method: "PATCH", body: { name } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.presets() }),
    // Nome repetido volta como erro do campo, na linha
    onError: (err) => {
      if (err.status !== NAME_TAKEN_STATUS) toastApiError(err);
    },
  });
}
