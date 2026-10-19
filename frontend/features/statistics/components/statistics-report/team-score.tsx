import { useState, type CSSProperties } from "react";
import { ChevronDown, Shield } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { teamColor, teamName, teamShortName } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { OverviewReport, ScoreAxis } from "@/types";
import { SCORE_AXES } from "../../lib/metrics";
import { PlayerScoreCard } from "./player-score-card";
import { membersOf } from "../../lib/teams";

type Team = OverviewReport["teams"][number];
type Player = OverviewReport["players"][number];

// Régua dos eixos da nota: ~100 é um bom desempenho, a escala vai a 200
const AXIS_SCALE = 200;

const AXES = Object.keys(SCORE_AXES) as ScoreAxis[];

/** Quem a nota mostra: uma equipe ou um jogador (`t:<equipe>` ou `p:<apelido>`). */
type Subject = `t:${number}` | `p:${string}`;

const axisPoints = (score: Team["score"] | Player["score"], axis: ScoreAxis) =>
  score?.axes.find((a) => a.axis === axis)?.points ?? null;

/** A nota da equipe em quatro eixos (média dos membros), a comparação entre equipes e os membros eixo a eixo. */
export function TeamScore({ report, currentPlayerName }: { report: OverviewReport; currentPlayerName: string }) {
  const { teams, players, team_naming: naming } = report;
  const you = players.find((p) => p.player_nickname === currentPlayerName);
  const [subject, setSubject] = useState<Subject>(`t:${you?.team ?? teams[0]?.team}`);

  const selectedPlayer = subject.startsWith("p:") ? players.find((p) => p.player_nickname === subject.slice(2)) : undefined;
  const selectedTeam = selectedPlayer
    ? teams.find((t) => t.team === selectedPlayer.team)
    : teams.find((t) => `t:${t.team}` === subject);
  if (!selectedTeam) return null;

  const picker = <SubjectPicker report={report} subject={subject} onSelect={setSubject} />;

  return (
    <>
      {selectedPlayer ? (
        <PlayerScoreCard report={report} player={selectedPlayer} currentPlayerName={currentPlayerName} action={picker} />
      ) : (
        <TeamAxes report={report} team={selectedTeam} picker={picker} />
      )}
      <TeamMembersAxes
        report={report}
        team={selectedTeam}
        currentPlayerName={currentPlayerName}
        title={
          <>
            Membros da <TeamBadge team={selectedTeam.team} naming={naming} form="full" />, eixo a eixo
          </>
        }
      />
    </>
  );
}

/** "Ver nota de": lista com busca; as equipes primeiro, pela nota, depois os jogadores agrupados pela equipe. */
function SubjectPicker({
  report,
  subject,
  onSelect,
}: {
  report: OverviewReport;
  subject: Subject;
  onSelect: (subject: Subject) => void;
}) {
  const [open, setOpen] = useState(false);
  const naming = report.team_naming;
  const choose = (next: Subject) => {
    onSelect(next);
    setOpen(false);
  };

  const label = subject.startsWith("p:") ? subject.slice(2) : teamName(Number(subject.slice(2)), naming);

  return (
    <span className="flex items-center gap-2.5">
      <span className="text-xs font-medium text-muted-foreground">Ver nota de</span>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger render={<Button variant="outline" role="combobox" aria-expanded={open} className="min-w-56 justify-between" />}>
          <span className="flex items-center gap-2 truncate">
            {subject.startsWith("t:") && <TeamBadge team={Number(subject.slice(2))} naming={naming} form="icon" size="sm" />}
            {label}
          </span>
          <ChevronDown className="text-faint-foreground" />
        </PopoverTrigger>
        <PopoverContent align="end" className="w-80">
          <Command>
            <CommandInput placeholder="Buscar equipe ou jogador…" />
            <CommandList>
              <CommandEmpty>Nenhuma equipe ou jogador com esse nome.</CommandEmpty>
              <CommandGroup heading="Equipes">
                {report.teams.map((team) => (
                  <CommandItem
                    key={team.team}
                    value={teamName(team.team, naming)}
                    selected={subject === `t:${team.team}`}
                    onSelect={() => choose(`t:${team.team}`)}
                  >
                    <TeamBadge team={team.team} naming={naming} form="icon" size="sm" />
                    {teamName(team.team, naming)}
                    <span className="font-mono text-xs text-muted-foreground">
                      {team.score ? `${displayNumber(team.score.total, 0)} pts` : "sem nota"}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
              {report.teams.map((team) => (
                <CommandGroup key={team.team} heading={`Jogadores · ${teamName(team.team, naming)}`}>
                  {membersOf(report, team.team).map((player) => (
                    <CommandItem
                      key={player.player_nickname}
                      value={`${player.player_nickname} ${teamName(team.team, naming)}`}
                      selected={subject === `p:${player.player_nickname}`}
                      onSelect={() => choose(`p:${player.player_nickname}`)}
                    >
                      <PlayerAvatar nickname={player.player_nickname} color={player.color} size="sm" />
                      {player.player_nickname}
                    </CommandItem>
                  ))}
                </CommandGroup>
              ))}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </span>
  );
}

/** Nota da equipe: só a média por eixo, com a régua na cor dela e a lista de todas as equipes naquele eixo. */
function TeamAxes({ report, team, picker }: { report: OverviewReport; team: Team; picker: React.ReactNode }) {
  const naming = report.team_naming;
  const style = { "--team": teamColor(team.team) } as CSSProperties;

  if (!team.score) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Nota da equipe</CardTitle>
          <CardDescription>
            A nota só existe a partir de {report.min_score_days} pregões de algum membro. Quem ainda não tem nota fica
            atrás no ranking.
          </CardDescription>
          <CardAction>{picker}</CardAction>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex flex-wrap items-center gap-2">
            Nota da <TeamBadge team={team.team} naming={naming} form="full" />: {displayNumber(team.score.total, 0)}{" "}
            pontos
          </span>
        </CardTitle>
        <CardDescription>
          Cada eixo é a média dos membros nesse eixo; a nota é a soma dos quatro, como na nota de cada um. ~100 por eixo
          é um bom desempenho.
        </CardDescription>
        <CardAction>{picker}</CardAction>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" style={style}>
          {AXES.map((axis) => {
            const points = Number(axisPoints(team.score, axis) ?? 0);
            const ranked = report.teams
              .map((t) => ({ team: t.team, points: Number(axisPoints(t.score, axis) ?? 0), measured: !!t.score }))
              .filter((t) => t.measured)
              .sort((a, b) => b.points - a.points);
            return (
              <div key={axis} className="grid content-start gap-3 rounded-[10px] border border-border p-4">
                <div className="grid gap-0.5">
                  <span className="flex items-baseline justify-between">
                    <span className="font-semibold">{SCORE_AXES[axis].label}</span>
                    <span className="font-mono text-xl font-semibold">{displayNumber(points, 0)}</span>
                  </span>
                  <span className="text-xs text-muted-foreground">{SCORE_AXES[axis].description}</span>
                </div>
                <div className="grid gap-1">
                  <div className="relative h-2 rounded-full bg-muted">
                    <span
                      className="absolute inset-y-0 left-0 rounded-full bg-(--team)"
                      style={{ width: `${Math.min(points / AXIS_SCALE, 1) * 100}%` }}
                    />
                    <span className="absolute -top-1 h-4 w-px bg-faint-foreground" style={{ left: "50%" }} title="100 = bom" />
                  </div>
                  <span className="font-mono text-[11px] text-faint-foreground">0 · 100 = bom · {AXIS_SCALE}</span>
                </div>
                {/* Todas as equipes nesse eixo: uma linha por equipe, a sua destacada */}
                <div className="grid gap-1 border-t border-muted pt-2.5">
                  <span className="text-[11px] text-faint-foreground">Todas as equipes nesse eixo</span>
                  {ranked.map((entry, index) => (
                    <span
                      key={entry.team}
                      style={{ "--team": teamColor(entry.team) } as CSSProperties}
                      className={cn(
                        "grid grid-cols-[22px_1fr_64px_32px] items-center gap-2 rounded-md px-1.5 py-1 text-xs",
                        entry.team === team.team && "bg-[color-mix(in_srgb,var(--team)_8%,transparent)] font-semibold",
                      )}
                    >
                      <span className="font-mono text-faint-foreground">{index + 1}º</span>
                      <span className="flex min-w-0 items-center gap-1.5">
                        <Shield className="size-3.5 shrink-0 fill-(--team) stroke-(--team)" />
                        <span className="truncate">{teamShortName(entry.team, naming)}</span>
                      </span>
                      <span className="h-1.5 overflow-hidden rounded-full bg-muted">
                        <span
                          className="block h-full rounded-full bg-(--team)"
                          style={{ width: `${Math.min(entry.points / AXIS_SCALE, 1) * 100}%` }}
                        />
                      </span>
                      <span className="text-right font-mono">{displayNumber(entry.points, 0)}</span>
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/** Uma barra por membro, na cor dele, com o traço da média da equipe: quem passa dele puxa a equipe para cima. */
function TeamMembersAxes({
  report,
  team,
  currentPlayerName,
  title,
}: {
  report: OverviewReport;
  team: Team;
  currentPlayerName: string;
  title: React.ReactNode;
}) {
  const members = membersOf(report, team.team).filter((m) => m.score);
  // Equipe de uma pessoa não tem o que comparar
  if (!team.score || members.length < 2) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex flex-wrap items-center gap-2">{title}</span>
        </CardTitle>
        <CardDescription>
          Uma barra por membro, na cor dele. O traço é a média da equipe: quem passa dele puxa a equipe para cima.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 lg:grid-cols-2">
          {AXES.map((axis) => {
            const mean = Number(axisPoints(team.score, axis) ?? 0);
            const rows = members
              .map((m) => ({ member: m, points: Number(axisPoints(m.score, axis) ?? 0) }))
              .sort((a, b) => b.points - a.points);
            return (
              <div key={axis} className="grid gap-2.5 rounded-[10px] border border-border p-4">
                <span className="flex items-baseline justify-between">
                  <span className="font-semibold">{SCORE_AXES[axis].label}</span>
                  <span className="text-xs text-muted-foreground">
                    média <b className="font-mono text-foreground">{displayNumber(mean, 0)}</b>
                  </span>
                </span>
                {rows.map(({ member, points }) => {
                  const diff = Math.round(points - mean);
                  return (
                    <span key={member.player_nickname} className="grid grid-cols-[110px_1fr_34px_34px] items-center gap-2.5">
                      <span className="flex min-w-0 items-center gap-1.5 text-[13px]">
                        <PlayerAvatar nickname={member.player_nickname} color={member.color} size="sm" />
                        <span className="truncate">{member.player_nickname}</span>
                        {member.player_nickname === currentPlayerName && (
                          <Badge variant="info" size="sm">
                            você
                          </Badge>
                        )}
                      </span>
                      <span className="relative h-2.5 rounded-full bg-muted">
                        <span
                          className="absolute inset-y-0 left-0 rounded-full"
                          style={{
                            width: `${Math.min(points / AXIS_SCALE, 1) * 100}%`,
                            backgroundColor: `var(--${member.color})`,
                          }}
                        />
                        <span
                          className="absolute -top-0.5 h-3.5 w-0.5 bg-foreground"
                          style={{ left: `${Math.min(mean / AXIS_SCALE, 1) * 100}%` }}
                          title={`Média da equipe: ${displayNumber(mean, 0)}`}
                        />
                      </span>
                      <span className="text-right font-mono text-[13px] font-semibold">{displayNumber(points, 0)}</span>
                      <span
                        className={cn(
                          "text-right font-mono text-xs",
                          diff > 0 ? "text-success" : diff < 0 ? "text-destructive" : "text-muted-foreground",
                        )}
                      >
                        {diff > 0 ? "+" : diff < 0 ? "−" : "+"}
                        {Math.abs(diff)}
                      </span>
                    </span>
                  );
                })}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
