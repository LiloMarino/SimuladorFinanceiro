import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { CandleChallenge, ChallengeDirection } from "@/types";

/** Responde ao desafio de hoje; a resposta do servidor já traz a pergunta fechada e o estado de espera. */
export function useAnswerCandleChallenge(ticker: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (direction: ChallengeDirection) =>
      apiFetch<CandleChallenge>(`/api/variable-income/${ticker}/challenge`, { method: "POST", body: { direction } }),
    onSuccess: (challenge) => queryClient.setQueryData(queryKeys.candleChallenge(ticker), challenge),
    onError: (err) => toastApiError(err),
  });
}
