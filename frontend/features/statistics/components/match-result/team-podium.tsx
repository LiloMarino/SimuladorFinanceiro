import type { CSSProperties } from "react";
import { Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { teamColor } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport } from "@/types";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { displayCriterionValue, rankingMeasure } from "../../lib/criterion";
import { membersOf } from "../../lib/teams";
import { PodiumSteps } from "./podium-steps";

/** Pódio de equipes: o degrau é da cor da equipe e o selo dela fica em cima, com os membros. */
export function TeamPodium({ report }: { report: OverviewReport }) {
  const measure = rankingMeasure(report);

  return (
    <PodiumSteps
      items={report.teams}
      emptyLabel={(position) => `Sem ${position}ª equipe`}
      columnStyle={(team) => ({ "--team": teamColor(team.team) }) as CSSProperties}
      stepClassName={(team) => (team ? "bg-(--team)" : "bg-sidebar-accent")}
      renderEntry={(team, first) => (
        <>
          {first && <Trophy className="size-[26px] text-trophy" />}
          <span className="flex -space-x-2">
            {membersOf(report, team.team).map((m) => (
              <PlayerAvatar
                key={m.player_nickname}
                nickname={m.player_nickname}
                color={m.color}
                bot={m.is_bot}
                size={first ? "xl" : "lg"}
              />
            ))}
          </span>
          <TeamBadge team={team.team} naming={report.team_naming} form="full" solid />
          {/* Equipe de uma pessoa: o nome dela, já que o selo só diz a equipe */}
          {team.members === 1 && (
            <span className="max-w-full truncate text-[13px] font-semibold text-white">
              {membersOf(report, team.team)[0]?.player_nickname}
            </span>
          )}
          <span className={cn("font-mono text-[13px]", first ? "text-trophy" : "text-sidebar-muted")}>
            {displayCriterionValue(measure, team.criterion_value)}
            {measure === "GOAL" && ` · ${displayMoneyCompact(team.total_networth)}`}
            {team.measured_members < team.members && ` · ${team.measured_members} de ${team.members}`}
          </span>
        </>
      )}
    />
  );
}
