import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { StateOrderRequest } from "@/types";

export function useSetStateOrder(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: StateOrderRequest) =>
      apiFetch(`/api/government/state-companies/${ticker}/order`, { method: "PUT", body }),
    onError: (err) => toastApiError(err),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanies() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.government() });
    },
  });
}
