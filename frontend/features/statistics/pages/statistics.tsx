import { MatchSummaryCard } from "../components/match-summary-card";
import { PlayersRankingTable } from "../components/players-ranking-table";
import { PerformanceChart } from "../components/performance-chart";
import { RiskSummaryCard } from "../components/risk-summary-card";
import { useStatistics } from "../hooks/queries/useStatistics";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";
import { useAuth } from "@/shared/hooks/useAuth";

export default function StatisticsPage() {
  const { data: statistics, isLoading: loading, error } = useStatistics();
  const { user: currentUser } = useAuth();

  if (loading) {
    return <LoadingPage />;
  } else if (!statistics || !currentUser) {
    return (
      <ErrorPage
        code={String(error?.status) || "500"}
        title="Erro ao carregar estatísticas"
        message={String(error?.message)}
      />
    );
  }

  const currentNickname = currentUser.nickname;
  const currentPlayer = statistics.players.find((p) => p.player_nickname === currentNickname);

  return (
    <section className="p-4 space-y-6">
      <PlayersRankingTable players={statistics.players} currentPlayerName={currentNickname} />

      <PerformanceChart players={statistics.players} />

      {statistics.players.length > 0 && <MatchSummaryCard report={statistics} currentPlayerName={currentNickname} />}

      {currentPlayer && <RiskSummaryCard player={currentPlayer} />}
    </section>
  );
}
