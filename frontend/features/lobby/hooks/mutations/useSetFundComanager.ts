import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundComanagerPreparationRequest, Preparations } from "@/types";

/** Convida um co-gestor para a gestora que o jogador funda; sem `share`, retira o convite ou o co-gestor. */
export function useSetFundComanager() {
  return useMutation({
    mutationFn: (body: FundComanagerPreparationRequest) =>
      apiFetch<Preparations>("/api/simulation/players/me/fund-preparation/comanagers", { method: "PUT", body }),
  });
}
