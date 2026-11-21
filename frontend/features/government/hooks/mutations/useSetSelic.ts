import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SelicRequest } from "@/types";

/** O presidente marca (ou desmarca, com nulo) a SELIC da próxima reunião do Copom. */
export function useSetSelic() {
  return useMutation({
    mutationFn: (body: SelicRequest) => apiFetch("/api/government/selic", { method: "POST", body }),
    onError: (err) => toastApiError(err),
  });
}
