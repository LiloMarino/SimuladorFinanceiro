import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { saveColorPreference } from "@/shared/lib/player-color-preference";

/** Pede ao servidor a cor do jogador na sala; vale o primeiro pedido e a escolha vira a preferência do navegador. */
export function useChooseColor() {
  return useApiMutation({
    mutationFn: (color: string) =>
      apiFetch<void>("/api/simulation/players/me/color", { method: "PUT", body: { color } }),
    onSuccess: (_, color) => saveColorPreference(color),
  });
}
