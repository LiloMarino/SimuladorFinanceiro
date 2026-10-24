import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { UserSettings } from "@/types";

/** O que o jogador deixou ligado no gráfico; é a mesma consulta das configurações do jogador. */
export function useIndicatorSettings() {
  return useQuery({
    queryKey: queryKeys.userSettings(),
    queryFn: ({ signal }) => apiFetch<UserSettings>("/api/settings", { signal }),
    select: (settings) => settings.indicators,
  });
}
