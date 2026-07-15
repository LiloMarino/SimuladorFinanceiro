import { MatchSummaryCard } from "../components/match-summary-card";
import { PlayersRankingTable } from "../components/players-ranking-table";
import { PerformanceChart } from "../components/performance-chart";
import { useStatistics } from "../hooks/queries/useStatistics";
import { LoadingPage } from "@/pages/loading";
import { buildMatchSummary } from "../lib/build-match-summary";
import { buildPlayersRanking } from "../lib/build-ranking";
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

  const ranking = buildPlayersRanking(statistics);
  const summary = buildMatchSummary(ranking, currentNickname);

  return (
    <section className="p-4 space-y-6">
      <PlayersRankingTable playersStats={ranking} currentPlayerName={currentNickname} />

      <PerformanceChart playersHistory={statistics} />

      <MatchSummaryCard summary={summary} />
    </section>
  );
}
