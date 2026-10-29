import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { GuidanceRuleRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

/** O líder muda a orientação padrão do partido para um valor. */
export function useSetGuidanceRule() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: GuidanceRuleRequest) => apiFetch("/api/government/parties/guidance", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
