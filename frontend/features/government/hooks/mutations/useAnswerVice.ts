import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ViceAnswerRequest } from "@/types";

export function useAnswerVice() {
  return useMutation({
    mutationFn: (body: ViceAnswerRequest) => apiFetch("/api/government/vice/answer", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
