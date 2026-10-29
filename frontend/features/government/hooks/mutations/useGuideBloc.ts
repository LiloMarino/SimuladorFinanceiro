import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { GuidanceRequest } from "@/types";
import { useRenewElection } from "./useRenewElection";

/** O líder orienta a bancada dele numa votação (uma medida, ou o pedido de impeachment). */
export function useGuideBloc() {
  const renew = useRenewElection();

  return useMutation({
    mutationFn: (body: GuidanceRequest) => apiFetch("/api/government/congress/guidance", { method: "PUT", body }),
    onSuccess: renew,
    onError: (err) => toastApiError(err),
  });
}
