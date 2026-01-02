import { displayPercent } from "@/shared/lib/utils/display";
import type { PlayerStat } from "../components/players-ranking-table";

export function buildMatchSummary(ranking: PlayerStat[], currentPlayerName: string) {
  const averageReturn = ranking.reduce((acc, p) => acc + p.returnPercent, 0) / ranking.length;

  const bestReturn = Math.max(...ranking.map((p) => p.returnPercent));
  const worstReturn = Math.min(...ranking.map((p) => p.returnPercent));

  const current = ranking.find((p) => p.name === currentPlayerName);

  return {
    position: current?.position ?? 0,
    playerReturn: displayPercent(current?.returnPercent ?? 0),
    averageReturn: displayPercent(averageReturn),
    bestReturn: displayPercent(bestReturn),
    worstReturn: displayPercent(worstReturn),
  };
}
