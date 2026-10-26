import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { AppFolders } from "@/types";

/** Onde o config.toml e os logs moram no computador do host. */
export function useAppFolders() {
  return useQuery({
    queryKey: queryKeys.appFolders(),
    queryFn: ({ signal }) => apiFetch<AppFolders>("/api/settings/folders", { signal }),
  });
}
