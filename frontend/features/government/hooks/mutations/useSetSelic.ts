import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { SelicRequest } from "@/types";

/** O presidente marca (ou desmarca, com nulo) a SELIC da próxima reunião do Copom. */
export function useSetSelic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: SelicRequest) => apiFetch("/api/government/selic", { method: "POST", body }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.government() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.pending() });
    },
    onError: (err) => toastApiError(err),
  });
}
