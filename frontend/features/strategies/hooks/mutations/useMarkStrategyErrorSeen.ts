import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

/** Registra que o jogador viu o erro que desligou a estratégia: o ponto vermelho do menu sai. */
export function useMarkStrategyErrorSeen() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch("/api/strategies/me/error-seen", { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.myStrategy() }),
  });
}
