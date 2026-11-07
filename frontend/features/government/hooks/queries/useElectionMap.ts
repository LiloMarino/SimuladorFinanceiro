import { queryOptions, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionMap } from "@/types";

const electionMapQuery = () =>
  queryOptions({
    queryKey: queryKeys.electionMap(),
    queryFn: ({ signal }) => apiFetch<ElectionMap>("/api/government/map", { signal }),
  });

/** O mapa do Brasil: pesquisa, resultado, rejeição e aprovação em cada estado e região. */
export function useElectionMap() {
  return useQuery(electionMapQuery());
}
