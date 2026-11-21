import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O convidado aceita (opera a carteira já, com a parte nas taxas do mês seguinte) ou recusa. */
export function useAnswerComanagerInvite(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accept: boolean) =>
      apiFetch<void>(`/api/funds/${fundId}/comanagers/${accept ? "acceptance" : "refusal"}`, { method: "POST" }),
    onSettled: () => void queryClient.invalidateQueries({ queryKey: fundKeys.all() }),
    onError: (err) => toastApiError(err),
  });
}
