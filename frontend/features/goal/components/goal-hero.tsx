import { MetricHint } from "@/shared/components/metric-hint";
import { Progress } from "@/shared/components/ui/progress";
import { displayAnnualMultiple } from "@/shared/lib/financial-independence";
import { GAME_TYPES } from "@/shared/lib/game-types";
import {
  displayGoalPercent,
  type GoalProjection,
  ownStanding,
  playerStandings,
  remainingToGoal,
  teamStandings,
} from "@/shared/lib/goal";
import { GOAL_PERCENT, GOAL_REMAINING } from "@/shared/lib/goal-metrics";
import { GOAL_ETA } from "@/shared/lib/life-metrics";
import { teamName } from "@/shared/lib/teams";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { GameType, GoalProgress, LifeStatus, PlayerGrouping, TeamNaming } from "@/types";

type GoalHeroProps = {
  gameType: GameType;
  progress: GoalProgress;
  /** A vida financeira, que o viver de renda tem; ausente na corrida à meta */
  life: LifeStatus | undefined;
  /** Previsão da chegada à meta pelo ritmo dos últimos 12 meses; nula quando não há como estimar */
  projection: GoalProjection | null;
  grouping: PlayerGrouping;
  teamNaming: TeamNaming;
  nickname: string;
};

/** Topo da página Meta: o seu progresso até a meta, o que falta e a distância para o líder. */
export function GoalHero({ gameType, progress, life, projection, grouping, teamNaming, nickname }: GoalHeroProps) {
  const inTeams = grouping === "TEAMS";
  const yours = ownStanding(progress, grouping, nickname);

  // Colocação entre jogadores, ou entre equipes pela média
  const ranking = inTeams
    ? teamStandings(progress).map((t) => ({
        key: String(t.team),
        name: teamName(t.team, teamNaming),
        networth: t.networth,
      }))
    : playerStandings(progress).map((p) => ({ key: p.nickname, name: p.nickname, networth: Number(p.networth) }));
  const yourKey = yours && ("nickname" in yours ? yours.nickname : String(yours.team));
  const position = ranking.findIndex((r) => r.key === yourKey) + 1;

  // Quem está logo à frente (ou, liderando, logo atrás): a distância que a frase cita
  const rival = position === 1 ? ranking[1] : ranking[0];
  const gap = yours && rival ? Math.abs(rival.networth - Number(yours.networth)) : 0;

  return (
    <section className="grid gap-3.5 rounded-2xl bg-sidebar px-7.5 py-6.5 text-sidebar-foreground">
      <div className="flex items-end justify-between gap-5">
        <div className="grid gap-1.5">
          <span className="text-[11px] font-semibold tracking-[.06em] text-sidebar-primary uppercase">
            {inTeams ? "A corrida da sua equipe · média dos membros" : "Sua corrida"} · {GAME_TYPES[gameType]?.label}
            {life && (
              <>
                {" "}
                · {displayAnnualMultiple(Number(life.withdrawal_rate))} a despesa anual de{" "}
                {displayMoneyWhole(Number(life.monthly_expense) * 12)}
              </>
            )}
          </span>
          <span className="text-[28px] font-bold text-white">
            <span className="font-mono">{yours ? displayMoneyWhole(yours.networth) : "—"}</span>{" "}
            <span className="text-lg font-medium text-sidebar-muted">de</span>{" "}
            <span className="font-mono">{displayMoneyWhole(progress.goal)}</span>
          </span>
        </div>
        <span className="flex items-center gap-2 font-mono text-[40px] leading-none font-semibold text-white">
          {yours ? displayGoalPercent(yours.fraction) : "—"}
          <MetricHint metric={GOAL_PERCENT} />
        </span>
      </div>

      <Progress
        value={Math.min(yours?.fraction ?? 0, 1) * 100}
        size="lg"
        tone="inverse"
        aria-label="Seu progresso até a meta"
      />

      {yours && (
        <div className="flex flex-wrap items-center justify-between gap-x-5 gap-y-1 text-[13px]">
          <p className="flex flex-wrap items-center gap-x-1.5">
            <span className="inline-flex items-center gap-1">
              Falta para a meta <MetricHint metric={GOAL_REMAINING} />
            </span>
            <b className="font-mono text-white">{displayMoneyWhole(remainingToGoal(yours.networth, progress.goal))}</b>
            {rival && (
              <>
                · {position}º lugar, <b className="font-mono text-white">{displayMoneyWhole(gap)}</b>{" "}
                {position === 1 ? "à frente de" : "atrás de"} {rival.name}
              </>
            )}
          </p>
          {projection && !inTeams && (
            <p className="inline-flex items-center gap-1">
              No ritmo atual, chega em <b className="text-white">{projection.monthYear}</b>
              <MetricHint metric={GOAL_ETA} />
            </p>
          )}
        </div>
      )}
    </section>
  );
}
