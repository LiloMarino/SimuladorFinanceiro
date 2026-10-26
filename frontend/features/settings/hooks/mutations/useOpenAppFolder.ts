import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { AppFolderTarget } from "@/types";

export function useOpenAppFolder() {
  return useMutation({
    mutationFn: (target: AppFolderTarget) => apiFetch(`/api/settings/open-folder?target=${target}`, { method: "POST" }),
    onError: (err) => toastApiError(err),
  });
}
