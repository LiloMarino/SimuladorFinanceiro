import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { playerColorName } from "@/shared/lib/player-colors";
import { toastApiError } from "@/shared/notifications/toast-api-error";
import type { RoomPlayer } from "@/types";
import { toBotRequest } from "../../lib/bot-form";
import { useAddBot } from "./useAddBot";

/** Tira o bot da sala e oferece "Desfazer", que o recoloca com a mesma configuração, nome e cor. */
export function useRemoveBot() {
  const restore = useAddBot();

  return useMutation({
    mutationFn: (player: RoomPlayer) =>
      apiFetch<void>(`/api/simulation/bots/${encodeURIComponent(player.nickname)}`, { method: "DELETE" }),
    onSuccess: (_, player) => {
      const request = toBotRequest(player);
      if (!request) return;
      toast.info(`${player.nickname} saiu da sala`, {
        description: `A vaga e a cor ${playerColorName(player.color)} ficaram livres.`,
        duration: 8000,
        action: { label: "Desfazer", onClick: () => restore.mutate(request) },
      });
    },
    onError: (err) => toastApiError(err),
  });
}
