import { useState } from "react";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricLabel } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, ScoreMetric } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { displayCriterionGap } from "../../lib/criterion";
import { SCORE, SCORE_AXES, SCORE_METRICS, displayMetric } from "../../lib/metrics";
import { SimulationLetter } from "../compare/simulation-letter";
import { simulationColor, simulationLetter, labelColors } from "../../lib/player-label";
import { playerKey, playerLabel } from "../../lib/player-label";
import { PlayerCell, PlayerToggle, TabStatus, type ReportProps } from "./shared";

type Player = OverviewReport["players"][number];

type RankingSort = "SCORE" | "RETURN" | "NETWORTH";

// Régua dos eixos da nota: ~100 é um bom desempenho, a escala vai a 200
const AXIS_SCALE = 200;

// Métricas da nota que o relatório lê como contagem de meses ("7 de 12"), não como percentual
const MONTH_COUNT_METRICS: ScoreMetric[] = ["months_above_cdi", "positive_months"];

export function OverviewTab({ simulationIds, currentPlayerName = "", onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("overview", simulationIds, onlyPlayer);
  if (!data) return <TabStatus loading={isLoading} title="o Geral" error={error} onRetry={() => void refetch()} />;

  const colorOf = labelColors(data.players, simulationIds, currentPlayerName);

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
  const { players, criterion, average_return, min_score_days } = report;
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
                Sua colocação · vitória por <b className="text-foreground">{VICTORY_CRITERIA[criterion].label}</b>
              </span>
              {you?.score && (
                <span className="text-lg font-semibold">
                  Nota {displayNumber(you.score.total, 0)} · retorno {displaySignedPercent(you.return_percent)}
                </span>
              )}
              {you && !you.score && (
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
              {you && you.position > 1 && (
                <span className="text-[13px] text-muted-foreground">
                  Faltam <b className="text-foreground">{displayCriterionGap(criterion, you.leader_gap)}</b> pra passar{" "}
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
}: {
  report: OverviewReport;
  currentPlayerName: string;
  simulationIds: number[];
}) {
  const [sortBy, setSortBy] = useState<RankingSort>("SCORE");
  const topScore = Math.max(...report.players.map((p) => Number(p.score?.total ?? 0)), 1);
  const largestReturn = Math.max(...report.players.map((p) => Math.abs(Number(p.return_percent))), 0.0001);
  const comparing = simulationIds.length > 1;
  // A ordem do servidor é a do critério; entre partidas dá para reordenar por retorno ou patrimônio
  const players =
    comparing && sortBy !== "SCORE"
      ? [...report.players].sort((a, b) =>
          sortBy === "RETURN"
            ? Number(b.return_percent) - Number(a.return_percent)
            : Number(b.total_networth) - Number(a.total_networth),
        )
      : report.players;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>{comparing ? `Ranking das ${simulationIds.length} partidas` : "Ranking"}</CardTitle>
        <CardDescription>
          {comparing
            ? "A Nota compara partidas de períodos diferentes de forma justa; o retorno depende de quanto o mercado andou em cada período. Sem nota (menos de 63 pregões) fica no fim."
            : `Ordenado pelo critério da partida: ${VICTORY_CRITERIA[report.criterion].label}`}
        </CardDescription>
        {comparing && (
          <CardAction>
            <ToggleGroup
              variant="segmented"
              aria-label="Ordenar por"
              value={[sortBy]}
              onValueChange={(values) => values[0] && setSortBy(values[0] as RankingSort)}
            >
              <ToggleGroupItem value="SCORE">Nota</ToggleGroupItem>
              <ToggleGroupItem value="RETURN">Retorno</ToggleGroupItem>
              <ToggleGroupItem value="NETWORTH">Patrimônio</ToggleGroupItem>
            </ToggleGroup>
          </CardAction>
        )}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>#</TableHead>
            <TableHead>Jogador</TableHead>
            <TableHead numeric={comparing}>
              <MetricLabel metric={SCORE} />
            </TableHead>
            <TableHead numeric>Patrimônio</TableHead>
            <TableHead numeric={!comparing}>Retorno</TableHead>
            <TableHead numeric>Pregões</TableHead>
            {!comparing && <TableHead numeric>Distância do líder</TableHead>}
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.players.length === 0 && (
            <TableEmptyRow colSpan={comparing ? 6 : 7}>
              <p className="text-[13px] text-muted-foreground">
                Ninguém tem patrimônio registrado ainda. O ranking aparece depois do primeiro pregão.
              </p>
            </TableEmptyRow>
          )}
          {players.map((p: Player, i) => {
            const position = sortBy === "SCORE" ? p.position : i + 1;
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
                  <PlayerCell player={p} label={label} simulationIds={simulationIds} isYou={isYou} />
                </TableCell>
                {comparing ? (
                  <TableCell numeric>{displayMetric(SCORE, p.score?.total)}</TableCell>
                ) : (
                  <TableCell>
                    <span className="flex items-center gap-2">
                      <span className="w-10 font-mono font-semibold">{displayMetric(SCORE, p.score?.total)}</span>
                      <span className="h-1.5 w-28 overflow-hidden rounded-full bg-muted">
                        <span
                          className="block h-full rounded-full bg-primary"
                          style={{ width: `${(Number(p.score?.total ?? 0) / topScore) * 100}%` }}
                        />
                      </span>
                    </span>
                  </TableCell>
                )}
                <TableCell numeric>{displayMoney(p.total_networth)}</TableCell>
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
                <TableCell numeric>{p.days}</TableCell>
                {!comparing && <TableCell numeric>{displayCriterionGap(report.criterion, p.leader_gap)}</TableCell>}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}

/** Valor da métrica na nota; os meses entram como contagem ("7 de 12"), como a Rentabilidade mostra. */
function displayScoreMetric(metric: ScoreMetric, value: string | null, months: number) {
  if (value !== null && MONTH_COUNT_METRICS.includes(metric) && months > 0) {
    return `${Math.round(Number(value) * months)} de ${months}`;
  }
  return displayMetric(SCORE_METRICS[metric], value);
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
  const leader = report.players[0]?.score ? report.players[0] : undefined;

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
    <Card>
      <CardHeader>
        <CardTitle>
          {player.player_nickname === currentPlayerName ? "Sua nota" : `Nota de ${player.player_nickname}`}:{" "}
          {displayNumber(player.score.total, 0)} pontos
        </CardTitle>
        <CardDescription>
          Soma de quatro eixos; cada eixo é a média dos pontos das suas métricas. ~100 por eixo é um bom desempenho.
        </CardDescription>
        <CardAction>
          <PlayerToggle labels={labels} current={selected} onSelect={setSelected} colorOf={colorOf} />
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {player.score.axes.map((axis) => {
            const points = Number(axis.points ?? 0);
            const leaderPoints = leader?.score?.axes.find((a) => a.axis === axis.axis)?.points;
            const belowLeader = leaderPoints !== null && leaderPoints !== undefined && points < Number(leaderPoints);
            return (
              <div key={axis.axis} className="grid content-start gap-3 rounded-[10px] border border-border p-4">
                <div className="grid gap-0.5">
                  <span className="flex items-baseline justify-between">
                    <span className="font-semibold">{SCORE_AXES[axis.axis].label}</span>
                    <span className="font-mono text-xl font-semibold">{displayNumber(points, 0)}</span>
                  </span>
                  <span className="text-xs text-muted-foreground">{SCORE_AXES[axis.axis].description}</span>
                </div>
                <div className="grid gap-1">
                  <div className="relative h-2 rounded-full bg-muted">
                    <span
                      className={cn("absolute inset-y-0 left-0 rounded-full", belowLeader ? "bg-chart-3" : "bg-primary")}
                      style={{ width: `${Math.min(points / AXIS_SCALE, 1) * 100}%` }}
                    />
                    <span
                      className="absolute -top-1 h-4 w-px bg-faint-foreground"
                      style={{ left: "50%" }}
                      title="100 = bom"
                    />
                    {leaderPoints !== null && leaderPoints !== undefined && (
                      <span
                        className="absolute -top-1 h-4 w-0.5 bg-foreground"
                        style={{ left: `${Math.min(Number(leaderPoints) / AXIS_SCALE, 1) * 100}%` }}
                        title={`Líder: ${displayNumber(leaderPoints, 0)}`}
                      />
                    )}
                  </div>
                  <span className="font-mono text-[11px] text-faint-foreground">0 · 100 = bom · {AXIS_SCALE}</span>
                </div>
                {/* Métrica, valor e pontos: tabela compacta dentro do cartão do eixo */}
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-[11px] text-faint-foreground">
                      <th scope="col" className="pb-1 text-left font-medium">
                        Métrica
                      </th>
                      <th scope="col" className="pb-1 text-right font-medium">
                        Valor
                      </th>
                      <th scope="col" className="pb-1 pl-2 text-right font-medium">
                        Pts
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {axis.metrics.map((m) => (
                      <tr key={m.metric} className="border-t border-muted">
                        <td className="py-1.5 pr-2 text-muted-foreground">{SCORE_METRICS[m.metric].label}</td>
                        <td className="py-1.5 text-right font-mono whitespace-nowrap">
                          {displayScoreMetric(m.metric, m.value, player.months)}
                        </td>
                        <td className="py-1.5 pl-2 text-right font-mono text-muted-foreground">
                          {m.points === null ? "—" : displayNumber(m.points, 0)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>

        {/* Legenda com as amostras das marcas */}
        <ul className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-muted-foreground">
          {leader && (
            <li className="flex items-center gap-1.5">
              <span className="h-3.5 w-0.5 bg-foreground" aria-hidden="true" />
              líder ({leader.player_nickname})
            </li>
          )}
          <li className="flex items-center gap-1.5">
            <span className="size-2.5 rounded-sm bg-chart-3" aria-hidden="true" />
            abaixo do líder nesse eixo
          </li>
          <li className="flex items-center gap-1.5">
            <span className="h-2 w-5 rounded-full bg-primary" aria-hidden="true" />
            igual ou acima
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}
