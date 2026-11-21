import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { TicketRequest } from "@/types";

export function useSetTicket() {
  return useMutation({
    mutationFn: (body: TicketRequest) => apiFetch("/api/government/parties/ticket", { method: "PUT", body }),
    onError: (err) => toastApiError(err),
  });
}
