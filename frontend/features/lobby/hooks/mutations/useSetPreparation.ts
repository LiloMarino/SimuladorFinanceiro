import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { Preparations, PreparationRequest } from "@/types";

/** Troca a preparação do jogador; quem atualiza a lista de todos é o evento preparations_update. */
export function useSetPreparation() {
  return useMutation({
    mutationFn: (body: PreparationRequest) =>
      apiFetch<Preparations>("/api/simulation/players/me/preparation", { method: "PUT", body }),
  });
}
