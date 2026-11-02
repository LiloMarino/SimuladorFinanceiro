import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { EngineProfileStatus } from "@/types";

/** Diz se o servidor está gravando o perfil do motor agora. */
export function useEngineProfile() {
  return useQuery({
    queryKey: queryKeys.debugEngineProfile(),
    queryFn: ({ signal }) => apiFetch<EngineProfileStatus>("/api/debug/profile/engine", { signal }),
  });
}
