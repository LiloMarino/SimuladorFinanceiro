import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O co-gestor aceita (compra ao preço e dentro do teto de agora, do caixa pessoal) ou recusa a oferta de cotas novas. */
export function useAnswerDirectedIssuance(fundId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accept: boolean) =>
      apiFetch<void>(`/api/funds/${fundId}/directed-issuance/${accept ? "acceptance" : "refusal"}`, {
        method: "POST",
      }),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: fundKeys.all() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
    },
    onError: (err) => toastApiError(err),
  });
}
