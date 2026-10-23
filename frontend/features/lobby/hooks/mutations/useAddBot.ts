import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RoomBotRequest, RoomPlayer } from "@/types";
import { NAME_TAKEN_STATUS } from "../../lib/bot-form";

/** Põe um bot na sala; quem muda a lista é o evento player_join. O nome repetido volta para o campo do diálogo. */
export function useAddBot() {
  return useMutation({
    mutationFn: (bot: RoomBotRequest) => apiFetch<RoomPlayer>("/api/simulation/bots", { method: "POST", body: bot }),
    onError: (err) => {
      if (err.status !== NAME_TAKEN_STATUS) toastApiError(err);
    },
  });
}
