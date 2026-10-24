import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ExpelRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

export function useExpelMember() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: ExpelRequest) => apiFetch("/api/government/parties/expel", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
