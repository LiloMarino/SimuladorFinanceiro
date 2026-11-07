import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { CandleChallengeView } from "@/types";
import { withState } from "../../lib/view";

/** O desafio da vela da sala: o estado atual e a resposta de quem pergunta. */
export function useCandleChallenge() {
  return useQuery({
    queryKey: queryKeys.candleChallenge(),
    queryFn: ({ signal }) => apiFetch<CandleChallengeView>("/api/candle-challenge", { signal }),
  });
}

/** Mantém o desafio vivo com o estado que o servidor transmite; vai uma vez só, no lobby. */
export function useCandleChallengeSync() {
  const queryClient = useQueryClient();

  useRealtime("candle_challenge_state", (state) => {
    queryClient.setQueryData(queryKeys.candleChallenge(), (prev: CandleChallengeView | undefined) =>
      withState(prev, state),
    );
  });
}
