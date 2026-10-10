import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { MatchSummaryCard } from "./match-summary-card";
import { PlayersRankingTable } from "./players-ranking-table";
import { ScoreBreakdownCard } from "./score-breakdown-card";
import { TabStatus, type ReportProps } from "./shared";

export function OverviewTab({ simulationIds, showSimulation, currentPlayerName = "" }: ReportProps) {
  const { data, isLoading } = useStatisticsReport("overview", simulationIds);
  if (!data) return <TabStatus loading={isLoading} />;

  return (
    <div className="space-y-6">
      {data.players.length > 0 && <MatchSummaryCard report={data} currentPlayerName={currentPlayerName} />}
      <PlayersRankingTable
        players={data.players}
        currentPlayerName={currentPlayerName}
        showSimulation={showSimulation}
      />
      {data.players.length > 0 && (
        <ScoreBreakdownCard report={data} showSimulation={showSimulation} currentPlayerName={currentPlayerName} />
      )}
    </div>
  );
}
