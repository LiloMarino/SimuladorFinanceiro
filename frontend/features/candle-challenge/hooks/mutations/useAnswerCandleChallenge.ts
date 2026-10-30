import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { CandleChallengeView, ChallengeDirection } from "@/types";
import { withDirection } from "../../lib/view";

/** Responde sobe ou desce; o botão já fica marcado e volta ao que era se o servidor recusar. */
export function useAnswerCandleChallenge() {
  const queryClient = useQueryClient();
  const key = queryKeys.candleChallenge();

  return useMutation({
    mutationFn: (direction: ChallengeDirection) =>
      apiFetch<void>("/api/candle-challenge/answer", { method: "POST", body: { direction } }),
    onMutate: (direction) => {
      const previous = queryClient.getQueryData<CandleChallengeView>(key);
      queryClient.setQueryData(key, withDirection(previous, direction));
      return { previous };
    },
    onError: (err, _direction, context) => {
      queryClient.setQueryData(key, context?.previous);
      toastApiError(err);
    },
  });
}
