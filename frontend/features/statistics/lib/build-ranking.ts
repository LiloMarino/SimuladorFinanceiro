import type { PlayerHistory } from "@/types";
import type { PlayerStat } from "../components/players-ranking-table";

export function buildPlayersRanking(players: PlayerHistory[]): PlayerStat[] {
  const ranked = players.map((p) => {
    const lastSnapshot = p.history[p.history.length - 1];

    const totalContributions = lastSnapshot.total_contribution;
    const capitalProvided = p.starting_cash + totalContributions;
    const finalNetWorth = lastSnapshot.total_networth ?? capitalProvided;
    const returnValue = finalNetWorth - capitalProvided;
    const returnPercent = capitalProvided > 0 ? returnValue / capitalProvided : 0;

    return {
      name: p.player_nickname,
      totalNetWorth: finalNetWorth,
      returnValue,
      returnPercent,
    };
  });

  ranked.sort((a, b) => b.returnPercent - a.returnPercent);

  return ranked.map((p, index) => ({
    ...p,
    position: index + 1,
  }));
}
