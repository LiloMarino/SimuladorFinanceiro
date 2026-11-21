import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ExpelRequest } from "@/types";

export function useExpelMember() {
  return useMutation({
    mutationFn: (body: ExpelRequest) => apiFetch("/api/government/parties/expel", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
