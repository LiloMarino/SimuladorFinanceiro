import { useMutation } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";

/** Marca como vistas as conquistas desbloqueadas até agora (tira o selo "Nova" e o ponto do menu). */
export function useMarkAchievementsSeen() {
  return useMutation({
    mutationFn: () => apiFetch<void>("/api/achievements/seen", { method: "POST", body: {} }),
  });
}
