import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FoundPartyRequest } from "@/types";

export function useFoundParty() {
  return useMutation({
    mutationFn: (body: FoundPartyRequest) => apiFetch("/api/government/parties", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
