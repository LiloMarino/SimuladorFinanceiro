import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RoomBotRequest, RoomBotsRequest, RoomPlayer } from "@/types";

/** Põe vários bots na sala de uma vez: entram todos ou nenhum; quem muda a lista são os eventos player_join. */
export function useAddBots() {
  return useMutation({
    mutationFn: (bots: RoomBotRequest[]) => {
      const body: RoomBotsRequest = { bots };
      return apiFetch<RoomPlayer[]>("/api/simulation/bots/batch", { method: "POST", body });
    },
    onError: (err) => toastApiError(err),
  });
}
