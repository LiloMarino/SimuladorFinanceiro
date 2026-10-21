import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TunnelStatus } from "@/types";

export function useTunnelStatus() {
  return useQuery({
    queryKey: queryKeys.tunnelStatus(),
    queryFn: ({ signal }) => apiFetch<TunnelStatus>("/api/tunnel/status", { signal }),
  });
}
