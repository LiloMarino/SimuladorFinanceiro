import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundPreparationRequest, Preparations } from "@/types";

/** Troca a escolha de gestora do jogador; quem atualiza a lista de todos é o evento preparations_update. */
export function useSetFundPreparation() {
  return useMutation({
    mutationFn: (body: FundPreparationRequest) =>
      apiFetch<Preparations>("/api/simulation/players/me/fund-preparation", { method: "PUT", body }),
  });
}
