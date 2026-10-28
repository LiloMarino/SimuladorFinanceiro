import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PromisesRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useSetPromises() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: PromisesRequest) => apiFetch("/api/government/promises", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
