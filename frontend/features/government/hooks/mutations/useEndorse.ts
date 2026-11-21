import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { EndorsementRequest } from "@/types";

export function useEndorse() {
  return useMutation({
    mutationFn: (body: EndorsementRequest) => apiFetch("/api/government/runoff/endorsement", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
