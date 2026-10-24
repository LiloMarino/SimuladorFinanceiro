import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ViceAnswerRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useAnswerVice() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: ViceAnswerRequest) => apiFetch("/api/government/vice/answer", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
