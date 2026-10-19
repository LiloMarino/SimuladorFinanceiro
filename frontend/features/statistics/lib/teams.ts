import type { OverviewReport } from "@/types";

/** Os membros de uma equipe, na ordem do ranking individual. */
export function membersOf(report: OverviewReport, team: number): OverviewReport["players"] {
  return report.players.filter((p) => p.team === team);
}

/**
 * Os jogadores agrupados pela ordem das equipes; sem equipes (todos contra todos) é um grupo
 * só, sem equipe, com todo mundo.
 */
export function groupByTeam<P extends { team: number | null }>(players: P[], teamOrder: number[]) {
  if (teamOrder.length === 0) return [{ team: null, players }];
  return teamOrder.map((team) => ({ team, players: players.filter((p) => p.team === team) }));
}
