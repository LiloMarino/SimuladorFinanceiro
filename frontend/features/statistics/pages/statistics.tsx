import { MatchSummaryCard } from "../components/match-summary-card";
import { PlayersRankingTable, type PlayerStat } from "../components/players-ranking-table";
import { PerformanceChart } from "../components/performance-chart";
import type { PlayerHistory } from "@/types";

export default function StatisticsPage() {
  const playersMock: PlayerStat[] = [
    { position: 1, name: "Você", totalNetWorth: 125430.65, returnPercent: 0.5, returnValue: 125430.65 },
    { position: 2, name: "Ana_Silva", totalNetWorth: 118540.2, returnPercent: -0.5, returnValue: -118540.2 },
    { position: 3, name: "Carlos_Invest", totalNetWorth: 107890.75, returnPercent: 0.5, returnValue: 107890.75 },
    { position: 4, name: "Bia_Trader", totalNetWorth: 98450.3, returnPercent: -0.5, returnValue: -98450.3 },
    { position: 5, name: "Pedro_Bolsa", totalNetWorth: 87670.15, returnPercent: 0.5, returnValue: 87670.15 },
  ];

  const performanceMock: PlayerHistory[] = [];

  return (
    <section className="p-4 space-y-6">
      <PlayersRankingTable players={playersMock} />

      {/* Card principal */}
      <PerformanceChart players={performanceMock} />

      {/* Resumo compacto */}
      <MatchSummaryCard
        summary={{
          position: 1,
          playerReturn: "+12.3%",
          averageReturn: "+5.4%",
          bestReturn: "+12.3%",
          worstReturn: "-2.1%",
        }}
      />
    </section>
  );
}
