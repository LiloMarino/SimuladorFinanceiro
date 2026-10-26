import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toastApiError } from "@/shared/notifications/toast-api-error";

/** O host tira uma pessoa da sala; quem muda a lista é o evento player_exit. */
export function useRemovePlayer() {
  return useMutation({
    mutationFn: (nickname: string) =>
      apiFetch<void>(`/api/simulation/players/${encodeURIComponent(nickname)}`, { method: "DELETE" }),
    onError: (err) => toastApiError(err),
  });
}
