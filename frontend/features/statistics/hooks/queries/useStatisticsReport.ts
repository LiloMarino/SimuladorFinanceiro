import { keepPreviousData } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { CompositionReport, OperationsReport, OverviewReport, ReturnsReport, RiskReport } from "@/types";

interface StatisticsReports {
  overview: OverviewReport;
  returns: ReturnsReport;
  risk: RiskReport;
  composition: CompositionReport;
  operations: OperationsReport;
}

export type StatisticsTab = keyof StatisticsReports;

/** Uma aba do relatório para as simulações informadas; a anterior fica na tela enquanto a nova carrega. */
export function useStatisticsReport<T extends StatisticsTab>(tab: T, simulationIds: number[]) {
  const params = new URLSearchParams(simulationIds.map((id) => ["simulation_ids", String(id)]));

  return useApiQuery({
    queryKey: queryKeys.statisticsReport(tab, simulationIds),
    queryFn: ({ signal }) => apiFetch<StatisticsReports[T]>(`/api/statistics/${tab}?${params}`, { signal }),
    enabled: simulationIds.length > 0,
    placeholderData: keepPreviousData,
  });
}
