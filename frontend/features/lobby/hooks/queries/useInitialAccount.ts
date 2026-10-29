import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { InitialAccountPreview } from "@/types";

/** O que a partida herda nas duas contas iniciais do governo, para a data de início das regras. */
export function useInitialAccount(start: string, { enabled }: { enabled: boolean }) {
  return useQuery({
    queryKey: queryKeys.initialAccount(start),
    queryFn: ({ signal }) =>
      apiFetch<InitialAccountPreview>(`/api/government/initial-account?start=${start}`, { signal }),
    enabled,
  });
}
