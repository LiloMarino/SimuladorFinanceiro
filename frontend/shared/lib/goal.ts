import type { GoalProgress, GoalRunner, PlayerGrouping, PortfolioHistoryPoint, SeriesPoint } from "@/types";
import { displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";

/** Atalhos da meta: múltiplos do saldo inicial. */
export const GOAL_SHORTCUTS = [5, 10, 20] as const;

/** Múltiplo que o servidor usa quando ninguém escolhe a meta. */
export const DEFAULT_GOAL_MULTIPLE = 10;

/** A meta subiu de um dia para o outro (reajuste pelo IPCA): quanto, e em que dia da partida. */
export type GoalRise = {
  /** Aumento sobre a meta anterior; 0,052 = +5,2% */
  fraction: number;
  date: string;
};

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

/** A meta vigente em `date`: o último degrau que já começou, ou o primeiro antes dele. */
export function goalAt(steps: SeriesPoint[], date: string) {
  let current = steps[0];
  for (const step of steps) {
    if (step.date > date) break;
    current = step;
  }
  return current ? Number(current.value) : undefined;
}

// Dias de um mês médio, para converter o ritmo mensal em data
const DAYS_PER_MONTH = 365.25 / 12;

export type GoalProjection = {
  /** Mês e ano em que o patrimônio alcança a meta, como "jun/2024" */
  monthYear: string;
  /** Meses a partir do último dia do histórico */
  months: number;
};

/**
 * Quando o patrimônio chega à meta se o ritmo dos últimos 12 meses continuar: o ganho
 * médio por mês entre o último dia e o dia de um ano antes cobre o que falta.
 * Sem 12 meses de histórico, sem crescimento ou com a meta já atingida, não há previsão.
 */
export function projectGoalDate(history: PortfolioHistoryPoint[], goal: number | string): GoalProjection | null {
  const last = history.at(-1);
  if (!last) return null;

  const yearAgo = `${Number(last.snapshot_date.slice(0, 4)) - 1}${last.snapshot_date.slice(4)}`;
  const start = history.filter((point) => point.snapshot_date <= yearAgo).at(-1);
  if (!start) return null;

  const lastDay = parseLocalDate(last.snapshot_date);
  const spanMonths = (lastDay.getTime() - parseLocalDate(start.snapshot_date).getTime()) / 86_400_000 / DAYS_PER_MONTH;
  const gainPerMonth = (Number(last.total_networth) - Number(start.total_networth)) / spanMonths;
  const remaining = Number(goal) - Number(last.total_networth);
  if (remaining <= 0 || gainPerMonth <= 0) return null;

  const months = remaining / gainPerMonth;
  const reached = new Date(lastDay.getTime() + months * DAYS_PER_MONTH * 86_400_000);
  const isoDate = `${reached.getFullYear()}-${String(reached.getMonth() + 1).padStart(2, "0")}-01`;
  return { monthYear: displayMonthSlashYear(isoDate), months };
}

/** "daqui a uns 8 anos", "daqui a uns 5 meses": a distância de uma previsão. */
export function displayProjectionDistance(months: number) {
  if (months < 1) return "daqui a menos de 1 mês";
  if (months < 12) {
    const whole = Math.round(months);
    return `daqui a uns ${whole} ${whole === 1 ? "mês" : "meses"}`;
  }
  const years = Math.round(months / 12);
  return `daqui a uns ${years} ${years === 1 ? "ano" : "anos"}`;
}
