import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { Profession } from "@/types";

type ProfessionChoice = {
  profession: Profession;
  /** A sigla do partido; só o Comissionado envia */
  party?: string | undefined;
};

/** Pede ao servidor a profissão do jogador na sala; quem muda a lista é o evento player_profession. */
export function useChooseProfession() {
  return useMutation({
    mutationFn: ({ profession, party }: ProfessionChoice) =>
      apiFetch<void>("/api/simulation/players/me/profession", { method: "PUT", body: { profession, party } }),
  });
}
