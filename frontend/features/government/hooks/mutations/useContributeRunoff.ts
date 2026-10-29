import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RunoffContributionRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useContributeRunoff() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: RunoffContributionRequest) =>
      apiFetch("/api/government/runoff/contribution", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
