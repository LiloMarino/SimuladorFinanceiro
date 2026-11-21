import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RunoffContributionRequest } from "@/types";

export function useContributeRunoff() {
  return useMutation({
    mutationFn: (body: RunoffContributionRequest) =>
      apiFetch("/api/government/runoff/contribution", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
