import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { UserSettings } from "@/types";

/** As notificações do jogador, completas: a posição do jornal, o nível de cada manchete e cada aviso. */
export function useNotificationSettings() {
  return useQuery({
    queryKey: queryKeys.userSettings(),
    queryFn: ({ signal }) => apiFetch<UserSettings>("/api/settings", { signal }),
    select: (settings) => settings.notifications,
  });
}
