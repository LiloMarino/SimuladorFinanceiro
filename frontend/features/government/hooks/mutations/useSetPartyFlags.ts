import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { PartyFlagsRequest } from "@/types";

export function useSetPartyFlags() {
  return useMutation({
    mutationFn: (body: PartyFlagsRequest) => apiFetch("/api/government/parties/flags", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
