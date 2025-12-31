import { MatchSummaryCard } from "../components/match-summary-card";
import { PlayersRankingTable } from "../components/players-ranking-table";
import { PerformanceChart } from "../components/performance-chart";
import type { PlayerHistory } from "@/types";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { LoadingPage } from "@/pages/loading";
import { buildMatchSummary } from "../lib/build-match-summary";
import { buildPlayersRanking } from "../lib/build-ranking";
import { ErrorPage } from "@/pages/error";

export default function StatisticsPage() {
  const { data: statistics, loading, error } = useQueryApi<PlayerHistory[]>("/api/statistics");

  if (loading) {
    return <LoadingPage />;
  } else if (!statistics) {
    return (
      <ErrorPage
        code={String(error?.status) || "500"}
        title="Erro ao carregar estatísticas"
        message={String(error?.message)}
      />
    );
  }

  const ranking = buildPlayersRanking(statistics);
  const summary = buildMatchSummary(ranking, "Você");

  return (
    <section className="p-4 space-y-6">
      <PlayersRankingTable playersStats={ranking} />

      {/* Card principal */}
      <PerformanceChart playersHistory={statistics} />

      {/* Resumo compacto */}
      <MatchSummaryCard summary={summary} />
    </section>
  );
}
