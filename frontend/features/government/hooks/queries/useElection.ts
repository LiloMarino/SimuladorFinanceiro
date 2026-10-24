import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionPanel } from "@/types";

/** Datas, partidos, pesquisas, resultados e rankings da eleição da partida. */
export function useElection() {
  return useQuery({
    queryKey: queryKeys.election(),
    queryFn: ({ signal }) => apiFetch<ElectionPanel>("/api/government/election", { signal }),
  });
}
