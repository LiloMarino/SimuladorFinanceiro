import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";
import { saveColorPreference } from "@/shared/lib/player-color-preference";

/** Entra na partida em andamento com a cor escolhida; vale o primeiro pedido, e a sessão deixa de ser pendente. */
export function useJoinMatch() {
  const queryClient = useQueryClient();

  return useApiMutation({
    mutationFn: (color: string) => apiFetch<void>("/api/simulation/join", { method: "POST", body: { color } }),
    onSuccess: async (_, color) => {
      saveColorPreference(color);
      await queryClient.invalidateQueries({ queryKey: queryKeys.authSession() });
    },
    // Quem perdeu a disputa pela cor vê a grade atualizada
    onError: () => void queryClient.invalidateQueries({ queryKey: queryKeys.matchPlayers() }),
  });
}
