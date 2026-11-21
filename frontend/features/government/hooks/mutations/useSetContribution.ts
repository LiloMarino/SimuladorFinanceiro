import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ContributionRequest } from "@/types";

export function useSetContribution() {
  return useMutation({
    mutationFn: (body: ContributionRequest) =>
      apiFetch("/api/government/membership/contribution", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
