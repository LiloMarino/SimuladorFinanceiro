import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { TicketRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useSetTicket() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: TicketRequest) => apiFetch("/api/government/parties/ticket", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
