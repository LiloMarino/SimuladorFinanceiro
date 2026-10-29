import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { NotificationCatalog } from "@/types";

/** O registro dos tipos de notificação: seções, manchetes (da mais à menos importante) e avisos do jogador. */
export function useNotificationCatalog() {
  return useQuery({
    queryKey: queryKeys.notificationCatalog(),
    queryFn: ({ signal }) => apiFetch<NotificationCatalog>("/api/settings/notification-types", { signal }),
    staleTime: Infinity,
  });
}
