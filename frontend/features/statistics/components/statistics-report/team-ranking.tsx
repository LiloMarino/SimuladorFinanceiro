import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber, sortTableRows, type TableSort } from "@/shared/lib/table-sort";
import { useState, type CSSProperties } from "react";
import { ChevronDown } from "lucide-react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricHint } from "@/shared/components/metric-hint";
import { teamColor, teamName } from "@/shared/lib/teams";
import { cn } from "@/shared/lib/utils";
import { displayNumber, displaySignedMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import { GOAL_PERCENT, GOAL_REMAINING } from "@/shared/lib/goal-metrics";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, Player, Team } from "@/types";
import {
  criterionLabel,
  displayCriterionContribution,
  displayCriterionGap,
  displayCriterionValue,
  displayRemainingToGoal,
  rankingMeasure,
} from "../../lib/criterion";
import { SCORE, SCORE_AXES, displayMetric } from "../../lib/metrics";
import { membersOf } from "../../lib/teams";

/** Quanto tempo cabe de pregões: a equipe tem tantos pregões quanto o membro que mais jogou. */
function daysOf(members: Player[]) {
  return Math.max(...members.map((m) => m.days), 0);
}

const MEMBER_PLURAL = (count: number) => `${count} ${count === 1 ? "jogador" : "jogadores"}`;

/** Topo: a colocação da sua equipe, a distância para a líder e a sua parte na média; ao lado, a sala em números. */
export function TeamHeadline({ report, currentPlayerName }: { report: OverviewReport; currentPlayerName: string }) {
  const { players, teams, average_return, team_naming, goal_net_worth } = report;
  const measure = rankingMeasure(report);
  const you = players.find((p) => p.player_nickname === currentPlayerName);
  const mine = teams.find((t) => t.team === you?.team);
  const byReturn = [...players].sort((a, b) => Number(b.return_percent) - Number(a.return_percent));
  const best = byReturn[0];
  const worst = byReturn.at(-1)!;
  const subject = mine ?? teams[0];
  const next = subject.position === 1 ? teams[1] : teams[0];

  const kpis = [
    { label: "Média da sala", value: average_return ? displaySignedPercent(average_return) : "—", player: null },
    { label: "Melhor retorno", value: displaySignedPercent(best.return_percent), player: best },
    { label: "Pior retorno", value: displaySignedPercent(worst.return_percent), player: worst },
  ];

  return (
    <Card>
      <CardContent>
        <div
          className="grid items-center gap-5 lg:grid-cols-[1fr_repeat(3,170px)]"
          style={{ "--team": teamColor(subject.team) } as CSSProperties}
        >
          <div className="flex items-center gap-4">
            <span className="grid size-19 shrink-0 place-content-center rounded-xl bg-(--team) text-center text-primary-foreground">
              <span className="text-2xl leading-none font-bold">{subject.position}º</span>
              <span className="text-[11px] opacity-80">de {teams.length}</span>
            </span>
            <div className="grid gap-1">
              <span className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                {mine ? "Sua equipe" : "Equipe líder"}
                <TeamBadge team={subject.team} naming={team_naming} size="sm" />· vitória por{" "}
                <b className="text-foreground">{criterionLabel(report)}</b> · média dos membros
              </span>
              <span className="text-lg font-semibold">
                {measure === "GOAL" ? (
                  <>{displayCriterionValue(measure, subject.criterion_value)} da meta</>
                ) : (
                  <>
                    {measure === "SCORE" ? "Nota da equipe" : VICTORY_CRITERIA[measure].label}{" "}
                    {subject.criterion_value === null
                      ? "ainda sem valor"
                      : measure === "SCORE"
                        ? displayNumber(subject.criterion_value, 0)
                        : displayCriterionValue(measure, subject.criterion_value)}
                  </>
                )}{" "}
                · retorno médio {displaySignedPercent(subject.return_percent)}
              </span>
              <span className="text-[13px] text-muted-foreground">
                {next && subject.position === 1 && (
                  <>
                    <b className="font-mono text-foreground">{displayCriterionGap(measure, next.leader_gap, goal_net_worth)}</b> à
                    frente da {teamName(next.team, team_naming)}.{" "}
                  </>
                )}
                {next && subject.position > 1 && (
                  <>
                    Faltam{" "}
                    <b className="text-foreground">{displayCriterionGap(measure, subject.leader_gap, goal_net_worth)}</b> pra passar a{" "}
                    {teamName(next.team, team_naming)} (1ª).{" "}
                  </>
                )}
                {mine && you && you.team_contribution !== null && Number(you.team_contribution) !== 0 && (
                  <>
                    Sua parte ({displayCriterionValue(measure, you.criterion_value)}) fica{" "}
                    <b className="text-foreground">
                      {displayCriterionGap(measure, String(Math.abs(Number(you.team_contribution))), goal_net_worth)}
                    </b>{" "}
                    {Number(you.team_contribution) > 0 ? "acima" : "abaixo"} da média da equipe
                    {you.weakest_axis && measure === "SCORE" && (
                      <>
                        ; seu eixo mais fraco é <b className="text-foreground">{SCORE_AXES[you.weakest_axis].label}</b>
                      </>
                    )}
                    .
                  </>
                )}
              </span>
            </div>
          </div>
          {kpis.map((k) => (
            <div key={k.label} className="grid gap-0.5 border-l border-border pl-4">
              <span className="text-xs text-muted-foreground">{k.label}</span>
              <span className="font-mono text-lg font-semibold">{k.value}</span>
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                {k.player ? (
                  <>
                    {k.player.player_nickname}
                    <TeamBadge team={k.player.team} naming={team_naming} form="icon" size="sm" />
                  </>
                ) : (
                  `${players.length} jogadores`
                )}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

type RankingView = "TEAMS" | "PLAYERS";

/** Ranking por equipe, com os membros abaixo; "Jogadores" volta ao ranking individual com o selo da equipe. */
export function TeamRanking({
  report,
  currentPlayerName,
  playerRanking,
}: {
  report: OverviewReport;
  currentPlayerName: string;
  /** O ranking individual, que recebe o seletor de visão no cabeçalho */
  playerRanking: (viewToggle: React.ReactNode) => React.ReactNode;
}) {
  const [view, setView] = useState<RankingView>("TEAMS");
  const you = report.players.find((p) => p.player_nickname === currentPlayerName);
  // A sua equipe vem aberta; com poucas equipes as outras também, com muitas ficam recolhidas
  const [open, setOpen] = useState<Record<number, boolean>>(() =>
    Object.fromEntries(report.teams.map((t) => [t.team, report.teams.length <= 3 || t.team === you?.team])),
  );

  const toggle = (
    <ToggleGroup
      variant="segmented"
      aria-label="Ranking por"
      value={[view]}
      onValueChange={(values) => values[0] && setView(values[0] as RankingView)}
    >
      <ToggleGroupItem value="TEAMS">Equipes</ToggleGroupItem>
      <ToggleGroupItem value="PLAYERS">Jogadores</ToggleGroupItem>
    </ToggleGroup>
  );

  const goalRace = rankingMeasure(report) === "GOAL";
  const topScore = Math.max(...report.teams.map((t) => Number(t.score?.total ?? 0)), 1);
  const sorting = useTableSort(report.teams, {
    position: (t) => t.position,
    name: (t) => teamName(t.team, report.team_naming),
    score: (t) => sortNumber(goalRace ? t.criterion_value : t.score?.total),
    wealth: (t) => sortNumber(t.total_networth),
    return: (t) => sortNumber(t.return_percent),
    days: (t) => daysOf(membersOf(report, t.team)),
    gap: (t) => goalRace && report.goal_net_worth
      ? t.criterion_value == null ? null : Math.max(0, (1 - Number(t.criterion_value)) * Number(report.goal_net_worth))
      : t.position === 1 ? null : sortNumber(t.leader_gap),
  });
  if (view === "PLAYERS") return playerRanking(toggle);


  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Ranking por equipe</CardTitle>
        <CardDescription>
          Classificação pela média da equipe no critério da partida: {criterionLabel(report)}
        </CardDescription>
        <CardAction>{toggle}</CardAction>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead label={"#"} {...sorting.header("position")} />
            <SortableTableHead label={"Equipe e membros"} {...sorting.header("name")} />
            <SortableTableHead label={(goalRace ? GOAL_PERCENT : SCORE).label} {...sorting.header("score")} numeric hint={<MetricHint metric={goalRace ? GOAL_PERCENT : SCORE} />} />
            <SortableTableHead label={"Patrimônio"} {...sorting.header("wealth")} numeric />
            <SortableTableHead label={"Retorno"} {...sorting.header("return")} numeric />
            <SortableTableHead label={"Pregões"} {...sorting.header("days")} numeric />
            <SortableTableHead label={goalRace && report.goal_net_worth ? GOAL_REMAINING.label : "Distância do líder"} {...sorting.header("gap")} numeric />
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.teams.length === 0 && (
            <TableEmptyRow colSpan={7}>
              <p className="font-semibold">Ainda sem placar</p>
              <p className="text-[13px] text-muted-foreground">
                Ninguém tem patrimônio registrado ainda. O ranking por equipe aparece depois do primeiro pregão, com as
                equipes do lobby.
              </p>
            </TableEmptyRow>
          )}
          {sorting.rows.map((team) => (
            <TeamRows
              key={team.team}
              report={report}
              team={team}
              topScore={topScore}
              sort={sorting.sort}
              currentPlayerName={currentPlayerName}
              open={open[team.team] ?? false}
              onToggle={() => setOpen((prev) => ({ ...prev, [team.team]: !prev[team.team] }))}
            />
          ))}
        </TableBody>
      </Table>
      <p className="px-5 py-3 text-xs text-muted-foreground">
        Nos membros, a última coluna diz quanto cada um puxa a média da equipe para cima ou para baixo.
      </p>
    </Card>
  );
}

function TeamRows({
  report,
  team,
  topScore,
  currentPlayerName,
  open,
  onToggle,
  sort,
}: {
  report: OverviewReport;
  team: Team;
  topScore: number;
  currentPlayerName: string;
  open: boolean;
  onToggle: () => void;
  sort: TableSort | null;
}) {
  const members = sortTableRows(membersOf(report, team.team), {
    position: (m) => m.position,
    name: (m) => m.player_nickname,
    score: (m) => sortNumber(rankingMeasure(report) === "GOAL" ? m.criterion_value : m.score?.total),
    wealth: (m) => sortNumber(m.total_networth),
    return: (m) => sortNumber(m.return_percent),
    days: (m) => m.days,
    gap: (m) => sortNumber(m.team_contribution),
  }, sort);
  const style = { "--team": teamColor(team.team) } as CSSProperties;
  const naming = report.team_naming;
  const maxScore = topScore;
  const measure = rankingMeasure(report);

  return (
    <>
      <TableRow variant="team" style={style} onActivate={onToggle} aria-expanded={open}>
        <TableCell>
          <span className="grid size-7 place-content-center rounded-md bg-(--team) font-mono text-xs font-semibold text-primary-foreground">
            {team.position}
          </span>
        </TableCell>
        <TableCell>
          <span className="flex items-center gap-2.5">
            <ChevronDown className={cn("size-4 text-muted-foreground transition-transform", !open && "-rotate-90")} />
            <TeamBadge team={team.team} naming={naming} form="full" />
            <span className="flex -space-x-1.5">
              {members.map((m) => (
                <PlayerAvatar key={m.player_nickname} nickname={m.player_nickname} color={m.color} size="sm" />
              ))}
            </span>
            <span className="text-xs font-normal text-muted-foreground">
              {MEMBER_PLURAL(team.members)} · média
              {team.measured_members < team.members && ` · ${team.measured_members} de ${team.members} com valor`}
            </span>
          </span>
        </TableCell>
        <TableCell>
          <ScoreBar {...barOf(measure, team.score?.total, team.criterion_value, maxScore)} tint="solid" />
        </TableCell>
        <TableCell numeric>
          <span className={cn("font-semibold", Number(team.total_networth) < 0 && "text-destructive")}>
            {displaySignedMoney(team.total_networth)}
          </span>
        </TableCell>
        <TableCell numeric>
          <span className={returnTone(team.return_percent)}>{displaySignedPercent(team.return_percent)}</span>
        </TableCell>
        <TableCell numeric>{daysOf(members)}</TableCell>
        <TableCell numeric>
          <span className="font-semibold">
            {measure === "GOAL" && report.goal_net_worth
              ? displayRemainingToGoal(team.criterion_value, report.goal_net_worth)
              : team.position === 1
                ? "—"
                : displayCriterionGap(measure, team.leader_gap, report.goal_net_worth)}
          </span>
        </TableCell>
      </TableRow>

      {open &&
        members.map((m) => {
          const isYou = m.player_nickname === currentPlayerName;
          return (
            <TableRow key={m.player_nickname} variant="member" style={style}>
              <TableCell />
              <TableCell>
                <span className="flex max-w-72 items-center gap-2 pl-7">
                  <PlayerAvatar nickname={m.player_nickname} color={m.color} size="sm" />
                  <span className="truncate" title={m.player_nickname}>
                    {m.player_nickname}
                  </span>
                  {isYou && (
                    <Badge variant="info" size="sm">
                      você
                    </Badge>
                  )}
                  {m.delinquent && (
                    <Badge variant="destructive" size="tag">
                      Negativado
                    </Badge>
                  )}
                </span>
              </TableCell>
              <TableCell>
                <ScoreBar {...barOf(measure, m.score?.total, m.criterion_value, maxScore)} tint="light" />
              </TableCell>
              <TableCell numeric>
                <span className={Number(m.total_networth) < 0 ? "text-destructive" : "text-muted-foreground"}>
                  {displaySignedMoney(m.total_networth)}
                </span>
              </TableCell>
              <TableCell numeric>
                <span className={returnTone(m.return_percent)}>{displaySignedPercent(m.return_percent)}</span>
              </TableCell>
              <TableCell numeric>
                <span className="text-muted-foreground">{m.days}</span>
              </TableCell>
              <TableCell numeric>
                <span
                  className={cn(
                    "text-xs",
                    Number(m.team_contribution ?? 0) > 0
                      ? "text-success"
                      : Number(m.team_contribution ?? 0) < 0
                        ? "text-destructive"
                        : "text-muted-foreground",
                  )}
                >
                  {displayCriterionContribution(measure, m.team_contribution)}
                </span>{" "}
                <span className="text-xs text-muted-foreground">na média</span>
              </TableCell>
            </TableRow>
          );
        })}
    </>
  );
}

function returnTone(value: string) {
  const change = Number(value);
  return change > 0 ? "text-success" : change < 0 ? "text-destructive" : undefined;
}

/** O texto e o comprimento (0 a 1) da barra: a nota contra a maior nota, ou a fração da meta. */
function barOf(measure: ReturnType<typeof rankingMeasure>, score: string | undefined, fraction: string | null, max: number) {
  return measure === "GOAL"
    ? { text: displayCriterionValue(measure, fraction), ratio: Math.min(Number(fraction ?? 0), 1) }
    : { text: displayMetric(SCORE, score), ratio: Number(score ?? 0) / max };
}

/** Valor e barra na cor da equipe (cheia na linha da equipe, mais clara nos membros). */
function ScoreBar({ text, ratio, tint }: { text: string; ratio: number; tint: "solid" | "light" }) {
  return (
    <span className="flex items-center gap-2">
      <span className="w-10 font-mono font-semibold">{text}</span>
      <span className="h-1.5 w-28 overflow-hidden rounded-full bg-muted">
        <span
          className={cn("block h-full rounded-full", tint === "solid" ? "bg-(--team)" : "bg-(--team)/45")}
          style={{ width: `${ratio * 100}%` }}
        />
      </span>
    </span>
  );
}
