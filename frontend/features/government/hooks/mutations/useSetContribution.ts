import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ContributionRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useSetContribution() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: ContributionRequest) =>
      apiFetch("/api/government/membership/contribution", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
