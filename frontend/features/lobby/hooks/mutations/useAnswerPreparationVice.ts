import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { Preparations, ViceAnswerRequest } from "@/types";

/** O convidado aceita ou recusa a vaga de vice que outro jogador preparou. */
export function useAnswerPreparationVice() {
  return useMutation({
    mutationFn: (body: ViceAnswerRequest) =>
      apiFetch<Preparations>("/api/simulation/players/me/preparation/vice", { method: "PUT", body }),
  });
}
