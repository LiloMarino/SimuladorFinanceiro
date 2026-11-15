import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";

/** As siglas dos partidos da partida em andamento, para quem entra escolher o do Comissionado. */
export function useMatchParties(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.matchParties(),
    queryFn: ({ signal }) => apiFetch<string[]>("/api/simulation/match-parties", { signal }),
    enabled,
  });
}
