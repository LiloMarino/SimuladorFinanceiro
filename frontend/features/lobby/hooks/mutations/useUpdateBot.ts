import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RoomBotRequest } from "@/types";
import { NAME_TAKEN_STATUS } from "../../lib/bot-form";

/** Reconfigura um bot da sala (nome, estratégia, parâmetros, cor, equipe); quem muda a lista é o evento player_bot. */
export function useUpdateBot(nickname: string) {
  return useMutation({
    mutationFn: (bot: RoomBotRequest) =>
      apiFetch<void>(`/api/simulation/bots/${encodeURIComponent(nickname)}`, { method: "PUT", body: bot }),
    onError: (err) => {
      if (err.status !== NAME_TAKEN_STATUS) toastApiError(err);
    },
  });
}
