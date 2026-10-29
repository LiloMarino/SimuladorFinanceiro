import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { ProposeDealRequest } from "@/types";
import { useRenewBase } from "./useRenewBase";

/** Propõe à bancada entrar na base por emenda. */
export function useProposeDeal() {
  const renew = useRenewBase();

  return useMutation({
    mutationFn: (body: ProposeDealRequest) => apiFetch("/api/government/deals", { method: "POST", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
