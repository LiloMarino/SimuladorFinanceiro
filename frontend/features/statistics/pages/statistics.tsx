import { MatchSummaryCard } from "../components/match-summary-card";
import { PlayersRankingTable } from "../components/players-ranking-table";
import { PerformanceChart } from "../components/performance-chart";
import type { PlayerHistory } from "@/types";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { LoadingPage } from "@/pages/loading";
import { buildMatchSummary } from "../lib/build-match-summary";
import { buildPlayersRanking } from "../lib/build-ranking";
import { ErrorPage } from "@/pages/error";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";

export default function StatisticsPage() {
  const { data: statistics, setData: setStatistics, loading, error } = useQueryApi<PlayerHistory[]>("/api/statistics");
  const { user: currentUser } = useAuth();

  useRealtime("statistics_snapshot_update", ({ snapshots }) => {
    setStatistics((prev) => {
      if (!prev) return prev;

      return prev.map((player) => {
        const updates = snapshots.filter((s) => s.player_nickname === player.player_nickname);

        if (!updates.length) return player;

        const map = new Map(player.history.map((h) => [h.snapshot_date, h]));

        updates.forEach(({ snapshot }) => {
          map.set(snapshot.snapshot_date, snapshot);
        });

        return {
          ...player,
          history: Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date)),
        };
      });
    });
  });

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
