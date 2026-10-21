import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Session } from "@/types";

export function useSession() {
  return useQuery({
    queryKey: queryKeys.authSession(),
    queryFn: ({ signal }) => apiFetch<Session>("/api/session/me", { signal }),
  });
}
