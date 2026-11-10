import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { Preparations, PreparationViceAnswer } from "@/types";

/** O convidado aceita ou recusa a vaga de vice de uma das chapas que o convidaram (`owner`). */
export function useAnswerPreparationVice() {
  return useMutation({
    mutationFn: (body: PreparationViceAnswer) =>
      apiFetch<Preparations>("/api/simulation/players/me/preparation/vice", { method: "PUT", body }),
  });
}
