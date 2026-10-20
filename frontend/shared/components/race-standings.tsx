import type { CSSProperties } from "react";
import { Shield } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Progress } from "@/shared/components/ui/progress";
import { cn } from "@/shared/lib/utils";
import { displayGoalPercent, playerStandings, teamStandings } from "@/shared/lib/goal";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { teamColor, teamName } from "@/shared/lib/teams";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { GoalProgress, PlayerGrouping, TeamNaming } from "@/types";

type RaceStandingsProps = {
  progress: GoalProgress;
  grouping: PlayerGrouping;
  teamNaming: TeamNaming;
  currentNickname: string;
};

const ROW = "grid grid-cols-[24px_minmax(0,6rem)_1fr_44px_auto] items-center gap-2.5 border-t border-border py-2";

/** A corrida de todos: uma barra por jogador (ou por equipe, na média) até a meta. */
export function RaceStandings({ progress, grouping, teamNaming, currentNickname }: RaceStandingsProps) {
  if (grouping === "TEAMS") {
    return (
      <div>
        {teamStandings(progress).map((team) => (
          <div key={team.team} className="border-t border-border py-2 first:border-t-0">
            <div className="grid grid-cols-[24px_minmax(0,6rem)_1fr_44px_auto] items-center gap-2.5">
              <Shield
                className="size-5 justify-self-center fill-(--team) stroke-(--team)"
                style={{ "--team": teamColor(team.team) } as CSSProperties}
              />
              <span className="truncate text-[13px] font-semibold">{teamName(team.team, teamNaming)}</span>
              <Progress value={Math.min(team.fraction, 1) * 100} size="md" color={teamColor(team.team)} />
              <span className="text-right font-mono text-[13px] font-semibold">{displayGoalPercent(team.fraction)}</span>
              <span className="text-right font-mono text-xs text-muted-foreground">
                {displayMoneyWhole(team.networth)} média
              </span>
            </div>
            <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1 pl-9.5 text-xs text-muted-foreground">
              {team.members.map((member) => (
                <span key={member.nickname} className="inline-flex items-center gap-1.5">
                  <PlayerAvatar nickname={member.nickname} color={member.color} size="sm" />
                  {member.nickname}
                  <b className="font-mono text-foreground">{displayGoalPercent(member.fraction)}</b>
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      {playerStandings(progress).map((runner) => {
        const you = runner.nickname === currentNickname;
        return (
          <div key={runner.nickname} className={cn(ROW, "first:border-t-0")}>
            <PlayerAvatar nickname={runner.nickname} color={runner.color} size="sm" />
            <span className={cn("truncate text-[13px]", you ? "font-semibold" : "font-medium")}>
              {runner.nickname}
              {you && " (você)"}
            </span>
            <Progress
              value={Math.min(runner.fraction, 1) * 100}
              size="md"
              color={playerColorStyle(runner.color).background}
            />
            <span className="text-right font-mono text-[13px] font-semibold">{displayGoalPercent(runner.fraction)}</span>
            <span className="text-right font-mono text-xs text-muted-foreground">{displayMoneyWhole(runner.networth)}</span>
          </div>
        );
      })}
    </div>
  );
}
