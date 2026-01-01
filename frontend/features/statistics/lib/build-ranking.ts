import type { PlayerHistory } from "@/types";
import type { PlayerStat } from "../components/players-ranking-table";

export function buildPlayersRanking(players: PlayerHistory[]): PlayerStat[] {
  const ranked = players.map((p) => {
    const initial = p.starting_cash;
    const lastSnapshot = p.history[p.history.length - 1];

    const final = lastSnapshot?.total_networth ?? initial;
    const returnValue = final - initial;
    const returnPercent = initial > 0 ? returnValue / initial : 0;

    return {
      name: p.player_nickname,
      totalNetWorth: final,
      returnValue,
      returnPercent,
    };
  });

  ranked.sort((a, b) => b.totalNetWorth - a.totalNetWorth);

  return ranked.map((p, index) => ({
    ...p,
    position: index + 1,
  }));
}
