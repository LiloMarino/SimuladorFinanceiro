import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { DebugCommands } from "@/types";

/** O catálogo de comandos com as escolhas atuais da partida; lido quando o console abre. */
export function useDebugCommands(open: boolean) {
  return useQuery({
    queryKey: queryKeys.debugCommands(),
    queryFn: ({ signal }) => apiFetch<DebugCommands>("/api/debug/commands", { signal }),
    enabled: open,
    staleTime: 0,
  });
}
