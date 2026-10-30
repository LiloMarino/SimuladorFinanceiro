import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** Entrar no desafio; o estado novo chega pelo tempo real, e a consulta é refeita por garantia. */
export function useJoinCandleChallenge() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<void>("/api/candle-challenge/join", { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.candleChallenge() }),
    onError: (err) => toastApiError(err),
  });
}
