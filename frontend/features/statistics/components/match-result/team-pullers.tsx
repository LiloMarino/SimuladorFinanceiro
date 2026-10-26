import type { CSSProperties } from "react";
import { Trophy } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Badge } from "@/shared/components/ui/badge";
import { teamColor, teamName, teamShortName } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport, Team } from "@/types";
import { displayCriterionContribution, displayCriterionValue, rankingMeasure } from "../../lib/criterion";
import { SCORE_AXES } from "../../lib/metrics";
import { membersOf } from "../../lib/teams";

/** Um cartão por equipe com quem mais puxou a média dela e quanto cada membro puxou, para cima ou para baixo. */
export function TeamPullers({
  report,
  currentPlayerName,
}: {
  report: OverviewReport;
  currentPlayerName?: string | undefined;
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {report.teams.map((team) => (
        <TeamPullerCard key={team.team} report={report} team={team} currentPlayerName={currentPlayerName} />
      ))}
    </div>
  );
}

function TeamPullerCard({
  report,
  team,
  currentPlayerName,
}: {
  report: OverviewReport;
  team: Team;
  currentPlayerName?: string | undefined;
}) {
  const { team_naming: naming } = report;
  const criterion = rankingMeasure(report);
  const winner = team.position === 1;
  const members = membersOf(report, team.team);
  const puller = team.top_puller;
  const pullerPlayer = members.find((m) => m.player_nickname === puller?.player_nickname);
  const scale = Math.max(...members.map((m) => Math.abs(Number(m.team_contribution ?? 0))), 0.0001);

  return (
    <section
      style={{ "--team": teamColor(team.team) } as CSSProperties}
      className={cn(
        "grid content-start gap-3.5 rounded-xl border bg-card p-5 shadow-xs",
        winner ? "border-2 border-trophy" : "border-border border-t-[3px] border-t-(--team)",
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-2.5">
          <span className="font-mono text-sm text-muted-foreground">{team.position}º</span>
          <TeamBadge team={team.team} naming={naming} form="full" />
          {winner && (
            <Badge variant="warning">
              <Trophy />
              Vencedora
            </Badge>
          )}
        </span>
        <span className="font-mono text-sm font-semibold">
          {displayCriterionValue(criterion, team.criterion_value)}{" "}
          <span className="text-xs font-normal text-muted-foreground">média</span>
        </span>
      </div>

      {members.length < 2 ? (
        <p className="rounded-lg bg-subtle p-3.5 text-[13px] text-muted-foreground">
          A {teamName(team.team, naming)} é só {members[0]?.player_nickname}: equipe de um conta o valor da própria
          pessoa.
        </p>
      ) : (
        <>
          {puller && pullerPlayer && (
            <div className="flex items-center gap-3 rounded-lg bg-[color-mix(in_srgb,var(--team)_8%,transparent)] p-3.5">
              <PlayerAvatar
                nickname={pullerPlayer.player_nickname}
                color={pullerPlayer.color}
                bot={pullerPlayer.is_bot}
                size="xl"
              />
              <div className="grid gap-0.5">
                <span className="text-xs font-medium text-(--team)">
                  Quem mais puxou a {teamShortName(team.team, naming)}
                </span>
                <span className="font-mono font-semibold">
                  {pullerPlayer.player_nickname} · {displayCriterionValue(criterion, pullerPlayer.criterion_value)}
                </span>
                <span className="text-[13px] text-muted-foreground">
                  <b className="text-success">{displayCriterionContribution(criterion, puller.contribution)}</b> acima
                  da média da equipe
                  {puller.axis && puller.axis_gap !== null && (
                    <>
                      ; puxou mais em <b className="text-foreground">{SCORE_AXES[puller.axis].label}</b> (
                      {displayCriterionContribution("SCORE", puller.axis_gap)})
                    </>
                  )}
                  .
                </span>
              </div>
            </div>
          )}

          <div className="grid gap-2">
            <span className="text-xs text-muted-foreground">
              Quanto cada um puxou a média ({displayCriterionValue(criterion, team.criterion_value)}) para cima ou para
              baixo · o traço é a média
            </span>
            {members.map((m) => {
              const contribution = Number(m.team_contribution ?? 0);
              return (
                <span
                  key={m.player_nickname}
                  className="grid grid-cols-[120px_1fr_90px_60px] items-center gap-2.5 text-[13px]"
                >
                  <span className="flex min-w-0 items-center gap-1.5">
                    <PlayerAvatar nickname={m.player_nickname} color={m.color} bot={m.is_bot} size="sm" />
                    <span className="truncate">{m.player_nickname}</span>
                    {m.player_nickname === currentPlayerName && (
                      <Badge variant="info" size="sm">
                        você
                      </Badge>
                    )}
                  </span>
                  <span className="relative h-2.5 rounded-full bg-muted">
                    <span className="absolute inset-y-0 left-1/2 w-0.5 bg-foreground" />
                    <span
                      className={cn(
                        "absolute inset-y-0",
                        contribution >= 0 ? "left-1/2 rounded-r bg-success" : "right-1/2 rounded-l bg-destructive",
                      )}
                      style={{ width: `${(Math.abs(contribution) / scale) * 50}%` }}
                    />
                  </span>
                  <span className="text-right font-mono">{displayCriterionValue(criterion, m.criterion_value)}</span>
                  <span
                    className={cn(
                      "text-right font-mono text-xs",
                      contribution > 0
                        ? "text-success"
                        : contribution < 0
                          ? "text-destructive"
                          : "text-muted-foreground",
                    )}
                  >
                    {displayCriterionContribution(criterion, m.team_contribution)}
                  </span>
                </span>
              );
            })}
          </div>
        </>
      )}
    </section>
  );
}
