import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { StateReservationRequest } from "@/types";

export function useReserveStateOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: StateReservationRequest) =>
      apiFetch("/api/government/state-companies/offer/reservation", { method: "POST", body }),
    onError: (err) => toastApiError(err),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.stateCompanies() });
    },
  });
}
