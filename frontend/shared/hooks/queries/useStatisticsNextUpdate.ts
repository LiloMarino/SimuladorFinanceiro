import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { StatisticsNextUpdate } from "@/types";

/** Dia em que as estatísticas fecham o mês de novo; refeita na virada, pelo prefixo `statistics`. */
export function useStatisticsNextUpdate() {
  return useQuery({
    queryKey: queryKeys.statisticsNextUpdate(),
    queryFn: ({ signal }) => apiFetch<StatisticsNextUpdate>("/api/statistics/next-update", { signal }),
  });
}
