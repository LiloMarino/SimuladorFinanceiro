import { queryOptions, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionTimeline } from "@/types";

const electionTimelineQuery = (year: number | null) =>
  queryOptions({
    queryKey: queryKeys.electionTimeline(year),
    queryFn: ({ signal }) =>
      apiFetch<ElectionTimeline>(`/api/government/map/timeline${year === null ? "" : `?year=${year}`}`, { signal }),
  });

/** A linha do tempo do mapa: os anos de eleição, os pontos da régua e os marcos do ano escolhido. */
export function useElectionTimeline(year: number | null) {
  return useQuery(electionTimelineQuery(year));
}
