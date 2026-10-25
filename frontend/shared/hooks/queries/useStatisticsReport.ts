import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type {
  BotReport,
  CompositionReport,
  Highlights,
  OperationsReport,
  OverviewReport,
  ReturnsReport,
  RiskReport,
  ScoreHistoryReport,
} from "@/types";

interface StatisticsReports {
  overview: OverviewReport;
  returns: ReturnsReport;
  risk: RiskReport;
  "score-history": ScoreHistoryReport;
  composition: CompositionReport;
  operations: OperationsReport;
  highlights: Highlights;
  bots: BotReport[];
}

export type StatisticsTab = keyof StatisticsReports;

/**
 * Uma parte do relatório (uma aba ou os destaques); a anterior fica na tela enquanto a nova
 * carrega. Com `onlyPlayer`, as linhas de jogador ficam só as dele, em todas as simulações.
 */
export function useStatisticsReport<T extends StatisticsTab>(tab: T, simulationIds: number[], onlyPlayer?: string) {
  const params = new URLSearchParams(simulationIds.map((id) => ["simulation_ids", String(id)]));

  return useQuery({
    queryKey: queryKeys.statisticsReport(tab, simulationIds),
    queryFn: ({ signal }) => apiFetch<StatisticsReports[T]>(`/api/statistics/${tab}?${params}`, { signal }),
    enabled: simulationIds.length > 0,
    placeholderData: keepPreviousData,
    select: (report) =>
      onlyPlayer && !Array.isArray(report) && "players" in report
        ? // O `Array.isArray` já tirou a lista; a regra não estreita o `T` genérico
          // oxlint-disable-next-line typescript/no-misused-spread
          { ...report, players: report.players.filter((p) => p.player_nickname === onlyPlayer) }
        : report,
  });
}
