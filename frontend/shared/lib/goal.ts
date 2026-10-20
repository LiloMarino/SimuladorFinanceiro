import type { GoalProgress, GoalRunner, PlayerGrouping } from "@/types";

/** Atalhos da meta: múltiplos do saldo inicial. */
export const GOAL_SHORTCUTS = [5, 10, 20] as const;

/** Múltiplo que o servidor usa quando ninguém escolhe a meta. */
export const DEFAULT_GOAL_MULTIPLE = 10;

export type RunnerStanding = GoalRunner & {
  /** Patrimônio ÷ meta; 1 = chegou */
  fraction: number;
};

export type TeamStanding = {
  team: number;
  /** Média do patrimônio dos membros */
  networth: number;
  fraction: number;
  members: RunnerStanding[];
};

export function goalFraction(networth: number | string, goal: number | string) {
  return Number(networth) / Number(goal);
}

/**
 * Percentual inteiro da meta, truncado: 100% só quando a meta foi atingida
 * (99,96% aparece como 99%).
 */
export function goalPercent(fraction: number) {
  return Math.floor(fraction * 100 + 1e-9);
}

export function displayGoalPercent(fraction: number) {
  return `${goalPercent(fraction)}%`;
}

/** Quanto falta de patrimônio para a meta; zero quando já chegou. */
export function remainingToGoal(networth: number | string, goal: number | string) {
  return Math.max(0, Number(goal) - Number(networth));
}

/** Os jogadores do maior para o menor patrimônio. */
export function playerStandings(progress: GoalProgress): RunnerStanding[] {
  return progress.players
    .map((runner) => ({ ...runner, fraction: goalFraction(runner.networth, progress.goal) }))
    .sort((a, b) => b.fraction - a.fraction);
}

/** As equipes da maior para a menor média; quem está sem equipe fica de fora. */
export function teamStandings(progress: GoalProgress): TeamStanding[] {
  const byTeam = new Map<number, RunnerStanding[]>();
  for (const runner of playerStandings(progress)) {
    if (runner.team === null) continue;
    byTeam.set(runner.team, [...(byTeam.get(runner.team) ?? []), runner]);
  }
  return Array.from(byTeam, ([team, members]) => {
    const networth = members.reduce((sum, m) => sum + Number(m.networth), 0) / members.length;
    return { team, networth, fraction: goalFraction(networth, progress.goal), members };
  }).sort((a, b) => b.fraction - a.fraction);
}

/** O percentual de quem vê a tela: o seu, ou o da sua equipe em partidas em equipes. */
export function ownStanding(progress: GoalProgress, grouping: PlayerGrouping, nickname: string) {
  const you = playerStandings(progress).find((p) => p.nickname === nickname);
  return grouping === "TEAMS" ? teamStandings(progress).find((t) => t.team === you?.team) : you;
}
