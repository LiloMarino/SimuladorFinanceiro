import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { GovernmentAction, GovernmentPreview } from "@/types";

export function useGovernmentPreview() {
  return useMutation({
    mutationFn: (body: GovernmentAction) => apiFetch<GovernmentPreview>("/api/government/preview", { method: "POST", body }),
    onError: err => toastApiError(err),
  });
}
