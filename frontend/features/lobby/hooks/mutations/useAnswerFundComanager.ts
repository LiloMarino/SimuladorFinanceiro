import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundComanagerAnswer, Preparations } from "@/types";

/** O convidado aceita ou recusa a co-gestão da gestora de um fundador (`owner`). */
export function useAnswerFundComanager() {
  return useMutation({
    mutationFn: (body: FundComanagerAnswer) =>
      apiFetch<Preparations>("/api/simulation/players/me/fund-preparation/comanagers/answer", {
        method: "PUT",
        body,
      }),
  });
}
