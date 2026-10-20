import { Link } from "react-router-dom";
import { ArrowUp, ChevronDown, Flag, Shield } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { RaceStandings } from "@/shared/components/race-standings";
import { Button } from "@/shared/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { Progress, ProgressEndMark, ProgressMarker } from "@/shared/components/ui/progress";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import { useGoalProgress } from "@/shared/hooks/queries/useGoalProgress";
import { useGoalRise } from "@/shared/hooks/queries/useGoalSteps";
import { displayGoalPercent, goalPercent, playerStandings, remainingToGoal, teamStandings } from "@/shared/lib/goal";
import { GOAL_PERCENT } from "@/shared/lib/goal-metrics";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";
import { teamColor, teamName } from "@/shared/lib/teams";
import { displayMoneyWhole, displayMoneyCompact, displaySignedPercent } from "@/shared/lib/utils/display";
import type { PlayerGrouping, TeamNaming } from "@/types";

// A partir de quanto da meta o aviso "a partida pode acabar amanhã" aparece
const NEAR_GOAL = 0.95;

type TopbarGoalProps = {
  grouping: PlayerGrouping;
  teamNaming: TeamNaming;
  /** Dia da partida, para saber se o último reajuste da meta ainda é recente */
  currentDate: string | undefined;
};

/** Corrida à meta na topbar: a meta, a trilha com um marcador por jogador (ou equipe) e o seu percentual. */
export function TopbarGoal({ grouping, teamNaming, currentDate }: TopbarGoalProps) {
  const { user } = useAuth();
  const { data: progress } = useGoalProgress();
  const rise = useGoalRise(currentDate);
  const nickname = user?.nickname ?? "";
  const inTeams = grouping === "TEAMS";

  if (!progress) return <TopbarGoalSkeleton />;

  const players = playerStandings(progress);
  const teams = teamStandings(progress);
  const you = players.find((p) => p.nickname === nickname);
  const yours = inTeams ? teams.find((t) => t.team === you?.team) : you;

  // Quem lidera: o nome que o aviso de "quase lá" cita
  const leaderFraction = (inTeams ? teams[0] : players[0])?.fraction ?? 0;
  const leaderName = inTeams
    ? teams[0]?.team === you?.team
      ? "Sua equipe"
      : teamName(teams[0]?.team ?? 0, teamNaming)
    : players[0]?.nickname === nickname
      ? "Você"
      : players[0]?.nickname;
  const nearGoal = leaderFraction >= NEAR_GOAL && leaderFraction < 1;

  const markers = inTeams
    ? teams.map((team) => (
        <ProgressMarker
          key={team.team}
          position={team.fraction}
          color={teamColor(team.team)}
          foreground="var(--primary-foreground)"
          highlighted={team.team === you?.team}
          title={teamName(team.team, teamNaming)}
        >
          <Shield className="fill-current stroke-current" />
        </ProgressMarker>
      ))
    : // O seu marcador vem por último: com marcadores colados, fica por cima
      [...players]
        .sort((a, b) => Number(a.nickname === nickname) - Number(b.nickname === nickname))
        .map((player) => {
          const { background, foreground } = playerColorStyle(player.color);
          return (
            <ProgressMarker
              key={player.nickname}
              position={player.fraction}
              color={background}
              foreground={foreground}
              highlighted={player.nickname === nickname}
              title={player.nickname}
            >
              {playerInitials(player.nickname)}
            </ProgressMarker>
          );
        });

  return (
    <Popover>
      <PopoverTrigger render={<Button variant="outline" size="auto" aria-label="Abrir a corrida até a meta" />}>
        {/* Meta */}
        <span className="grid gap-px">
          <span className="flex items-center gap-1 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
            <Flag className="size-3" />
            Meta
          </span>
          <span className="font-mono text-[13px] font-semibold">{displayMoneyCompact(progress.goal)}</span>
          {nearGoal ? (
            <span className="text-[11px] font-normal text-warning">
              {leaderName} a {100 - goalPercent(leaderFraction)}% da meta
            </span>
          ) : rise ? (
            <span className="flex items-center gap-0.5 text-[11px] font-normal text-warning">
              <ArrowUp className="size-3" />
              {displaySignedPercent(rise.fraction, 1)} com o IPCA
            </span>
          ) : (
            inTeams && <span className="text-[11px] font-normal text-muted-foreground">média da sua equipe</span>
          )}
        </span>

        {/* Trilha */}
        <Progress
          value={Math.min(yours?.fraction ?? 0, 1) * 100}
          variant="markers"
          size="md"
          indicatorTone="soft"
          markers={
            <>
              {markers}
              <ProgressEndMark />
            </>
          }
          className="h-7 w-60 items-center"
        />

        {/* Seu percentual */}
        <span className="grid justify-items-end">
          <span className="font-mono text-[13px] font-semibold">
            {yours ? displayGoalPercent(yours.fraction) : "—"}
          </span>
          <span className="text-[11px] font-normal text-muted-foreground">você</span>
        </span>
        <ChevronDown className="text-faint-foreground" />
      </PopoverTrigger>

      {/* Corrida de todos */}
      <PopoverContent align="end" sideOffset={8} className="w-110">
        <div className="grid gap-1 p-1.5">
          <div className="flex items-baseline justify-between">
            <b className="flex items-center gap-1.5 text-sm">
              Corrida até {displayMoneyCompact(progress.goal)}
              <InfoHint label={`O que é ${GOAL_PERCENT.label}`}>
                <div className="space-y-1 text-left">
                  <p>{GOAL_PERCENT.definition}</p>
                  <p>{GOAL_PERCENT.example}</p>
                  <p>{GOAL_PERCENT.reading}</p>
                </div>
              </InfoHint>
            </b>
            <span className="text-xs text-muted-foreground">{inTeams ? "média da equipe" : "patrimônio de hoje"}</span>
          </div>
          <p className="mb-1.5 text-xs text-muted-foreground">A partida termina no dia em que alguém chegar.</p>
          <RaceStandings progress={progress} grouping={grouping} teamNaming={teamNaming} currentNickname={nickname} />
          <div className="mt-1 flex items-center justify-between border-t border-border pt-3 text-[13px]">
            {yours ? (
              <span className="text-muted-foreground">
                Faltam{" "}
                <b className="font-mono text-foreground">
                  {displayMoneyWhole(remainingToGoal(yours.networth, progress.goal))}
                </b>{" "}
                para {inTeams ? "sua equipe" : "você"} chegar
              </span>
            ) : (
              <span />
            )}
            <Button variant="link" size="sm" nativeButton={false} render={<Link to="/statistics" />}>
              Ver estatísticas →
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

/** Esqueleto do bloco antes do primeiro pregão. */
function TopbarGoalSkeleton() {
  return (
    <div
      className="flex items-center gap-3 rounded-lg border border-border bg-card py-1.5 pr-3 pl-2.5"
      aria-busy="true"
    >
      <span className="grid gap-px">
        <span className="flex items-center gap-1 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
          <Flag className="size-3" />
          Meta
        </span>
        <span className="font-mono text-[13px] font-semibold text-faint-foreground">—</span>
      </span>
      <Skeleton className="h-2 w-60" />
      <span className="grid justify-items-end">
        <span className="font-mono text-[13px] font-semibold text-faint-foreground">—</span>
        <span className="text-[11px] text-muted-foreground">você</span>
      </span>
    </div>
  );
}
