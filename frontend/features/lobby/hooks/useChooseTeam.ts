import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";

/** Pede ao servidor a equipe do jogador na sala; quem muda a lista é o evento player_team. */
export function useChooseTeam() {
  return useMutation({
    mutationFn: (team: number) => apiFetch<void>("/api/simulation/players/me/team", { method: "PUT", body: { team } }),
  });
}
