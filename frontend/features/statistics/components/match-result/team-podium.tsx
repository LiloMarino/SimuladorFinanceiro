import type { CSSProperties } from "react";
import { Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { teamColor } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport } from "@/types";
import { displayCriterionValue } from "../../lib/criterion";
import { membersOf } from "../../lib/teams";

// Degraus na ordem visual: 2º à esquerda, 1º no meio e mais alto, 3º à direita
const STEPS = [
  { position: 2, height: "h-[110px]" },
  { position: 1, height: "h-[150px]" },
  { position: 3, height: "h-20" },
] as const;

/** Pódio de equipes: o degrau é da cor da equipe e o selo dela fica em cima, com os membros. */
export function TeamPodium({ report }: { report: OverviewReport }) {
  const byPosition = new Map(report.teams.map((t) => [t.position, t]));

  return (
    <div className="flex w-full max-w-[480px] items-end gap-3">
      {STEPS.map((step) => {
        const team = byPosition.get(step.position);
        const first = step.position === 1;
        return (
          <div
            key={step.position}
            className="flex flex-1 flex-col items-center gap-2"
            style={team ? ({ "--team": teamColor(team.team) } as CSSProperties) : undefined}
          >
            {team ? (
              <>
                {first && <Trophy className="size-[26px] text-trophy" />}
                <span className="flex -space-x-2">
                  {membersOf(report, team.team).map((m) => (
                    <PlayerAvatar
                      key={m.player_nickname}
                      nickname={m.player_nickname}
                      color={m.color}
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
                  {displayCriterionValue(report.criterion, team.criterion_value)}
                  {team.measured_members < team.members && ` · ${team.measured_members} de ${team.members}`}
                </span>
              </>
            ) : (
              <span className="text-sidebar-muted">Sem {step.position}ª equipe</span>
            )}
            <div
              className={cn(
                "flex w-full justify-center rounded-t-[10px] pt-2.5",
                step.height,
                team ? "bg-(--team)" : "bg-sidebar-accent",
              )}
            >
              <span className="font-mono text-[22px] font-semibold text-white">{step.position}º</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
