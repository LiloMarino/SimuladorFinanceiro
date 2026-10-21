import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Achievement } from "@/types";

/** O catálogo inteiro de conquistas com o que o jogador já tem; a secreta bloqueada chega sem nome e descrição. */
export function useAchievements() {
  return useQuery({
    queryKey: queryKeys.achievements(),
    queryFn: ({ signal }) => apiFetch<Achievement[]>("/api/achievements", { signal }),
  });
}
