import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { RouteProfilesData } from "@/types";
import { REFRESH_MS } from "../../lib/stats";

/** O interruptor do perfil das rotas e os últimos perfis; com ele ligado, a lista se atualiza a cada 2 s. */
export function useRouteProfiles() {
  return useQuery({
    queryKey: queryKeys.debugRouteProfiles(),
    queryFn: ({ signal }) => apiFetch<RouteProfilesData>("/api/debug/profile/routes", { signal }),
    refetchInterval: (query) => (query.state.data?.enabled ? REFRESH_MS : false),
  });
}
