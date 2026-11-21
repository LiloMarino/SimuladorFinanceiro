import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { FundComanagerShareRequest } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

type UpdateComanagerShare = FundComanagerShareRequest & { userId: number };

/** A parte nova do co-gestor vale nas taxas do mês seguinte. */
export function useUpdateComanagerShare(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, ...request }: UpdateComanagerShare) =>
      apiFetch<void>(`/api/funds/${fundId}/comanagers/${userId}/share`, { method: "PUT", body: request }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
