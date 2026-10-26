import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { saveColorPreference } from "@/shared/lib/player-color-preference";

/** Entra na partida em andamento com a cor (e a equipe, em partida em equipes); vale o primeiro pedido, e a sessão deixa de ser pendente. */
export function useJoinMatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ color, team }: { color: string; team?: number | undefined }) =>
      apiFetch<void>("/api/simulation/join", { method: "POST", body: { color, team } }),
    onSuccess: async (_, { color }) => {
      saveColorPreference(color);
      await queryClient.invalidateQueries({ queryKey: queryKeys.authSession() });
    },
    // Quem perdeu a disputa pela cor vê a grade atualizada
    onError: () => void queryClient.invalidateQueries({ queryKey: queryKeys.matchPlayers() }),
  });
}
