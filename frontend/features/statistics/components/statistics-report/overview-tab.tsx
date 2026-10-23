import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber } from "@/shared/lib/table-sort";
import { useState } from "react";
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
import { Progress } from "@/shared/components/ui/progress";
import { GOAL_PERCENT, GOAL_REMAINING } from "@/shared/lib/goal-metrics";
import { cn } from "@/shared/lib/utils";
import { displayNumber, displaySignedMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { OverviewReport, Player } from "@/types";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import {
  criterionLabel,
  displayCriterionContribution,
  displayCriterionGap,
  displayCriterionValue,
  displayRemainingToGoal,
  rankingMeasure,
} from "../../lib/criterion";
import { AXIS_SCALE, SCORE, SCORE_AXES, displayMetric } from "../../lib/metrics";
import { SimulationLetter } from "../compare/simulation-letter";
import { simulationColor, simulationLetter, labelColors } from "../../lib/player-label";
import { playerKey, playerLabel } from "../../lib/player-label";
import { PlayerScoreCard } from "./player-score-card";
import { PlayerCell, PlayerToggle, TabStatus, type ReportProps } from "./shared";
import { TeamHeadline, TeamRanking } from "./team-ranking";
import { TeamScore } from "./team-score";


export function OverviewTab({ simulationIds, currentPlayerName = "", onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("overview", simulationIds, onlyPlayer);
  if (!data) return <TabStatus simulationIds={simulationIds} loading={isLoading} title="o Geral" error={error} onRetry={() => void refetch()} />;

  const colorOf = labelColors(data.players, simulationIds, currentPlayerName);

  // Partida em equipes: o ranking, a nota e os membros são da equipe, com os jogadores abaixo
  if (data.player_grouping === "TEAMS") {
    return (
      <div className="grid gap-5">
        {data.teams.length > 0 && <TeamHeadline report={data} currentPlayerName={currentPlayerName} />}
        <TeamRanking
          report={data}
          currentPlayerName={currentPlayerName}
          playerRanking={(viewToggle) => (
            <Ranking
              report={data}
              currentPlayerName={currentPlayerName}
              simulationIds={simulationIds}
              title="Ranking por jogador"
              description={`Classificação pelo critério da partida: ${criterionLabel(data)}`}
              action={viewToggle}
            />
          )}
        />
        <TeamScore report={data} currentPlayerName={currentPlayerName} />
      </div>
    );
  }

  return (
    <div className="grid gap-5">
      {simulationIds.length === 1 && data.players.length > 0 && (
        <Headline report={data} currentPlayerName={currentPlayerName} />
      )}
      <Ranking report={data} currentPlayerName={currentPlayerName} simulationIds={simulationIds} />
      {data.players.length > 0 && (
        <ScoreAxes
          report={data}
          currentPlayerName={currentPlayerName}
          simulationIds={simulationIds}
          colorOf={colorOf}
        />
      )}
      {simulationIds.length > 1 && (
        <YouVersusYou report={data} simulationIds={simulationIds} currentPlayerName={currentPlayerName} />
      )}
    </div>
  );
}

/** Seus eixos da nota em cada partida, uma barra por partida; a diferença é contra a primeira escolhida. */
function YouVersusYou({
  report,
  simulationIds,
  currentPlayerName,
}: {
  report: OverviewReport;
  simulationIds: number[];
  currentPlayerName: string;
}) {
  const mine = report.players
    .filter((p) => p.player_nickname === currentPlayerName && p.score)
    .sort((a, b) => simulationIds.indexOf(a.simulation_id) - simulationIds.indexOf(b.simulation_id));
  if (mine.length < 2) return null;

  const pointsOf = (p: Player, axis: string) => p.score?.axes.find((a) => a.axis === axis)?.points ?? null;
  const base = mine[0];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Você contra você</CardTitle>
        <CardDescription>
          Seus eixos da nota em cada partida. ~100 por eixo é um bom desempenho; a diferença é contra a partida{" "}
          {simulationLetter(simulationIds, base.simulation_id)}.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-5 md:grid-cols-2">
          {Object.entries(SCORE_AXES).map(([axis, info]) => (
            <div key={axis} className="grid gap-2">
              <span className="text-[13px] font-semibold">{info.label}</span>
              {mine.map((p, i) => {
                const value = pointsOf(p, axis);
                const reference = pointsOf(base, axis);
                const rawDiff = i > 0 && value !== null && reference !== null ? Number(value) - Number(reference) : null;
                // Diferença que arredonda para 0 não vira "+0"
                const diff = rawDiff !== null && Math.round(rawDiff) !== 0 ? rawDiff : null;
                return (
                  <div key={p.simulation_id} className="flex items-center gap-2.5">
                    <SimulationLetter
                      letter={simulationLetter(simulationIds, p.simulation_id)}
                      color={simulationColor(simulationIds, p.simulation_id)}
                    />
                    <span className="h-2.5 flex-1 overflow-hidden rounded-full bg-muted">
                      <span
                        className="block h-full rounded-full"
                        style={{
                          width: `${Math.min(Number(value ?? 0) / AXIS_SCALE, 1) * 100}%`,
                          backgroundColor: simulationColor(simulationIds, p.simulation_id),
                        }}
                      />
                    </span>
                    <span className="w-9 text-right font-mono text-[13px] font-semibold">
                      {value === null ? "—" : displayNumber(value, 0)}
                    </span>
                    <span
                      className={cn(
                        "w-10 font-mono text-xs",
                        diff === null || diff === 0
                          ? "text-transparent"
                          : diff > 0
                            ? "text-success"
                            : "text-destructive",
                      )}
                    >
                      {diff !== null && diff !== 0 ? `${diff > 0 ? "+" : "−"}${displayNumber(Math.abs(diff), 0)}` : "·"}
                    </span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** Topo: a sua colocação, quanto falta pro líder e o eixo mais fraco; ao lado, a sala em números. */
function Headline({ report, currentPlayerName }: { report: OverviewReport; currentPlayerName: string }) {
  const { players, average_return, min_score_days, goal_net_worth } = report;
  const measure = rankingMeasure(report);
  const you = players.find((p) => p.player_nickname === currentPlayerName);
  const leader = players[0];
  const byReturn = [...players].sort((a, b) => Number(b.return_percent) - Number(a.return_percent));
  const best = byReturn[0];
  const worst = byReturn.at(-1)!;

  const kpis = [
    { label: "Média da sala", value: average_return ? displaySignedPercent(average_return) : "—", detail: null },
    { label: "Melhor retorno", value: displaySignedPercent(best.return_percent), detail: best.player_nickname },
    { label: "Pior retorno", value: displaySignedPercent(worst.return_percent), detail: worst.player_nickname },
  ];

  return (
    <Card>
      <CardContent>
        <div className="grid items-center gap-5 lg:grid-cols-[1fr_repeat(3,170px)]">
          <div className="flex items-center gap-4">
            <span className="grid size-19 shrink-0 place-content-center rounded-xl bg-foreground text-center text-primary-foreground">
              <span className="text-2xl leading-none font-bold">{you ? `${you.position}º` : "—"}</span>
              <span className="text-[11px] text-sidebar-foreground">de {players.length}</span>
            </span>
            <div className="grid gap-1">
              <span className="text-xs text-muted-foreground">
                Sua colocação · vitória por <b className="text-foreground">{criterionLabel(report)}</b>
              </span>
              {you && measure === "GOAL" && (
                <span className="flex items-center gap-1.5 text-lg font-semibold">
                  {displayCriterionValue(measure, you.criterion_value)} da meta
                  <MetricHint metric={GOAL_PERCENT} />
                </span>
              )}
              {you?.score && measure !== "GOAL" && (
                <span className="text-lg font-semibold">
                  Nota {displayNumber(you.score.total, 0)} · retorno {displaySignedPercent(you.return_percent)}
                </span>
              )}
              {you && !you.score && measure !== "GOAL" && (
                <>
                  <span className="text-xl font-semibold">
                    Nota sai em {Math.max(min_score_days - you.days, 0)} pregões
                  </span>
                  <span className="flex items-center gap-2.5">
                    <span className="h-2 w-55 overflow-hidden rounded-full bg-muted">
                      <span
                        className="block h-full rounded-full bg-primary"
                        style={{ width: `${Math.min(you.days / min_score_days, 1) * 100}%` }}
                      />
                    </span>
                    <span className="font-mono text-xs text-muted-foreground">
                      {you.days} de {min_score_days} pregões
                    </span>
                  </span>
                  <span className="text-[13px] text-muted-foreground">
                    Antes de ~3 meses, anualizar o retorno engana. Retorno até aqui:{" "}
                    <b className="font-mono text-foreground">{displaySignedPercent(you.return_percent)}</b>.
                  </span>
                </>
              )}
              {you && measure === "GOAL" && goal_net_worth && (
                <span className="text-[13px] text-muted-foreground">
                  Faltam{" "}
                  <b className="font-mono text-foreground">{displayRemainingToGoal(you.criterion_value, goal_net_worth)}</b>{" "}
                  para a meta
                  {you.position > 1 && (
                    <>
                      {" "}
                      e <b className="font-mono text-foreground">{displayCriterionGap(measure, you.leader_gap, goal_net_worth)}</b>{" "}
                      para passar {leader.player_nickname} (1º)
                    </>
                  )}
                  . A meta é a mesma para todos, então quem tem mais patrimônio está mais perto.
                </span>
              )}
              {you && measure !== "GOAL" && you.position > 1 && (
                <span className="text-[13px] text-muted-foreground">
                  Faltam <b className="text-foreground">{displayCriterionGap(measure, you.leader_gap)}</b> pra passar{" "}
                  {leader.player_nickname} (1º).
                  {you.weakest_axis && (
                    <>
                      {" "}
                      Seu eixo mais fraco é <b className="text-foreground">{SCORE_AXES[you.weakest_axis].label}</b>.
                    </>
                  )}
                </span>
              )}
            </div>
          </div>
          {kpis.map((k) => (
            <div key={k.label} className="grid gap-0.5 border-l border-border pl-4">
              <span className="text-xs text-muted-foreground">{k.label}</span>
              <span className="font-mono text-lg font-semibold">{k.value}</span>
              {k.detail && <span className="text-xs text-muted-foreground">{k.detail}</span>}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function Ranking({
  report,
  currentPlayerName,
  simulationIds,
  title,
  description,
  action,
}: {
  report: OverviewReport;
  currentPlayerName: string;
  simulationIds: number[];
  /** Título, descrição e ação próprios, quando o ranking é uma das visões de outro cartão */
  title?: string;
  description?: string;
  action?: React.ReactNode;
}) {
  const measure = rankingMeasure(report);
  const goalRace = measure === "GOAL";
  const topScore = Math.max(...report.players.map((p) => Number(p.score?.total ?? 0)), 1);
  const largestReturn = Math.max(...report.players.map((p) => Math.abs(Number(p.return_percent))), 0.0001);
  const comparing = simulationIds.length > 1;
  const inTeams = report.teams.length > 0;
  // A meta só é uma entre as partidas comparadas quando todas têm a mesma
  const showRemaining = goalRace && !comparing && !!report.goal_net_worth;
  const sorting = useTableSort(report.players, {
    position: (p) => p.position,
    player: (p) => playerLabel(p, simulationIds, currentPlayerName),
    score: (p) => sortNumber(goalRace ? p.criterion_value : p.score?.total),
    wealth: (p) => sortNumber(p.total_networth),
    remaining: (p) => p.criterion_value == null ? null : Math.max(0, (1 - Number(p.criterion_value)) * Number(report.goal_net_worth)),
    return: (p) => sortNumber(p.return_percent),
    days: (p) => p.days,
    gap: (p) => sortNumber(p.leader_gap),
    contribution: (p) => sortNumber(p.team_contribution),
  });
  const players = sorting.rows;
  const shortcuts = { SCORE: "score", RETURN: "return", NETWORTH: "wealth" } as const;
  const sortBy = Object.entries(shortcuts).find(([, column]) => column === sorting.sort?.column)?.[0];

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>{title ?? (comparing ? `Ranking das ${simulationIds.length} partidas` : "Ranking")}</CardTitle>
        <CardDescription>
          {description ??
            (comparing
              ? "A Nota compara partidas de períodos diferentes de forma justa; o retorno depende de quanto o mercado andou em cada período. Sem nota (menos de 63 pregões) fica no fim."
              : `Classificação pelo critério da partida: ${criterionLabel(report)}`)}
        </CardDescription>
        {action && <CardAction>{action}</CardAction>}
        {comparing && (
          <CardAction>
            <ToggleGroup
              variant="segmented"
              aria-label="Ordenar por"
              value={sortBy ? [sortBy] : []}
              onValueChange={(values) => {
                const column = shortcuts[values[0] as keyof typeof shortcuts];
                if (column) sorting.setSort({ column, direction: "desc" });
              }}
            >
              <ToggleGroupItem value="SCORE">{goalRace ? "% da meta" : "Nota"}</ToggleGroupItem>
              <ToggleGroupItem value="RETURN">Retorno</ToggleGroupItem>
              <ToggleGroupItem value="NETWORTH">Patrimônio</ToggleGroupItem>
            </ToggleGroup>
          </CardAction>
        )}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead label={"#"} {...sorting.header("position")} />
            <SortableTableHead label={"Jogador"} {...sorting.header("player")} />
            <SortableTableHead label={(goalRace ? GOAL_PERCENT : SCORE).label} {...sorting.header("score")} numeric hint={<MetricHint metric={goalRace ? GOAL_PERCENT : SCORE} />} />
            <SortableTableHead label={"Patrimônio"} {...sorting.header("wealth")} numeric />
            {showRemaining && (
              <SortableTableHead label={GOAL_REMAINING.label} {...sorting.header("remaining")} numeric hint={<MetricHint metric={GOAL_REMAINING} />} />
            )}
            <SortableTableHead label={goalRace ? "Rentabilidade" : "Retorno"} {...sorting.header("return")} numeric />
            {!goalRace && <SortableTableHead label={"Pregões"} {...sorting.header("days")} numeric />}
            {!comparing && !goalRace && <SortableTableHead label={"Distância do líder"} {...sorting.header("gap")} numeric />}
            {inTeams && <SortableTableHead label={"Na média da equipe"} {...sorting.header("contribution")} numeric />}
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.players.length === 0 && (
            <TableEmptyRow
              colSpan={5 + (goalRace ? 0 : 1) + (goalRace || comparing ? 0 : 1) + (showRemaining ? 1 : 0) + (inTeams ? 1 : 0)}
            >
              <p className="text-[13px] text-muted-foreground">
                Ninguém tem patrimônio registrado ainda. O ranking aparece depois do primeiro pregão.
              </p>
            </TableEmptyRow>
          )}
          {players.map((p: Player) => {
            const position = p.position;
            const label = playerLabel(p, simulationIds, currentPlayerName);
            const isYou = p.player_nickname === currentPlayerName;
            const change = Number(p.return_percent);
            const returnTone = change > 0 ? "text-success" : change < 0 ? "text-destructive" : undefined;
            return (
              <TableRow key={playerKey(p)} variant={isYou ? "current" : "default"}>
                <TableCell>
                  <span
                    className={cn(
                      "grid size-7 place-content-center rounded-md font-mono text-xs font-semibold",
                      position === 1 ? "bg-foreground text-primary-foreground" : "bg-muted",
                    )}
                  >
                    {position}
                  </span>
                </TableCell>
                <TableCell>
                  <PlayerCell
                    player={p}
                    label={label}
                    simulationIds={simulationIds}
                    isYou={isYou}
                    teamNaming={report.team_naming}
                    delinquent={p.delinquent}
                  />
                </TableCell>
                {comparing ? (
                  <TableCell numeric>
                    {goalRace ? displayCriterionValue(measure, p.criterion_value) : displayMetric(SCORE, p.score?.total)}
                  </TableCell>
                ) : (
                  <TableCell>
                    <span className="flex items-center gap-2">
                      <span className="w-10 font-mono font-semibold">
                        {goalRace ? displayCriterionValue(measure, p.criterion_value) : displayMetric(SCORE, p.score?.total)}
                      </span>
                      {goalRace ? (
                        <Progress value={Math.min(Number(p.criterion_value ?? 0), 1) * 100} size="sm" className="w-28" />
                      ) : (
                        <span className="h-1.5 w-28 overflow-hidden rounded-full bg-muted">
                          <span
                            className="block h-full rounded-full bg-primary"
                            style={{ width: `${(Number(p.score?.total ?? 0) / topScore) * 100}%` }}
                          />
                        </span>
                      )}
                    </span>
                  </TableCell>
                )}
                <TableCell numeric>
                  <span className={cn(Number(p.total_networth) < 0 && "text-destructive")}>
                    {displaySignedMoney(p.total_networth)}
                  </span>
                </TableCell>
                {showRemaining && (
                  <TableCell numeric>{displayRemainingToGoal(p.criterion_value, report.goal_net_worth)}</TableCell>
                )}
                {comparing ? (
                  <TableCell>
                    {/* Barra divergente: o zero fica no meio, ganho para a direita e perda para a esquerda */}
                    <span className="flex items-center gap-3">
                      <span className="relative h-2.5 w-70 shrink-0">
                        <span className="absolute inset-y-0 left-1/2 w-px bg-input" />
                        <span
                          className={cn(
                            "absolute inset-y-0",
                            change >= 0 ? "left-1/2 rounded-r bg-success" : "right-1/2 rounded-l bg-destructive",
                          )}
                          style={{ width: `${(Math.abs(change) / largestReturn) * 50}%` }}
                        />
                      </span>
                      <span className={cn("w-20 text-right font-mono", returnTone)}>
                        {displaySignedPercent(p.return_percent)}
                      </span>
                    </span>
                  </TableCell>
                ) : (
                  <TableCell numeric>
                    <span className={returnTone}>{displaySignedPercent(p.return_percent)}</span>
                  </TableCell>
                )}
                {!goalRace && <TableCell numeric>{p.days}</TableCell>}
                {!comparing && !goalRace && (
                  <TableCell numeric>{displayCriterionGap(measure, p.leader_gap)}</TableCell>
                )}
                {inTeams && (
                  <TableCell numeric>
                    <span
                      className={cn(
                        "text-xs",
                        Number(p.team_contribution ?? 0) > 0
                          ? "text-success"
                          : Number(p.team_contribution ?? 0) < 0
                            ? "text-destructive"
                            : "text-muted-foreground",
                      )}
                    >
                      {displayCriterionContribution(measure, p.team_contribution)}
                    </span>
                  </TableCell>
                )}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      {report.players.some((p) => p.delinquent || Number(p.total_networth) < 0) && (
        <p className="px-(--card-spacing) text-xs text-muted-foreground">
          <Badge variant="destructive" size="tag">
            Negativado
          </Badge>{" "}
          tem parcela em atraso. Patrimônio em vermelho: deve mais do que tem.
        </p>
      )}
    </Card>
  );
}

/** A nota em 4 eixos, cada um numa régua de 0 a 200 com a marca do 100 e a do líder. */
function ScoreAxes({
  report,
  currentPlayerName,
  simulationIds,
  colorOf,
}: {
  report: OverviewReport;
  currentPlayerName: string;
  simulationIds: number[];
  colorOf: (label: string) => string;
}) {
  const scored = report.players.filter((p) => p.score);
  const labels = scored.map((p) => playerLabel(p, simulationIds, currentPlayerName));
  const yours = scored.find((p) => p.player_nickname === currentPlayerName);
  const [selected, setSelected] = useState<string | undefined>(
    yours ? playerLabel(yours, simulationIds, currentPlayerName) : labels[0],
  );
  const player =
    scored.find((p) => playerLabel(p, simulationIds, currentPlayerName) === selected) ?? scored[0];

  if (!player?.score) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Nota</CardTitle>
          <CardDescription>
            A nota só existe a partir de {report.min_score_days} pregões. Quem ainda não tem nota fica atrás no ranking.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <PlayerScoreCard
      report={report}
      player={player}
      currentPlayerName={currentPlayerName}
      action={<PlayerToggle labels={labels} current={selected} onSelect={setSelected} colorOf={colorOf} />}
    />
  );
}
