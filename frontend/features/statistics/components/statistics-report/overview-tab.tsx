import { useState } from "react";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { MetricLabel } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { displayCriterionGap } from "../../lib/criterion";
import { SCORE, SCORE_AXES, SCORE_METRICS, displayMetric } from "../../lib/metrics";
import { playerColors } from "../../lib/player-colors";
import { playerLabel } from "../../lib/player-label";
import { PlayerCell, PlayerToggle, TabStatus, type ReportProps } from "./shared";

type Player = OverviewReport["players"][number];

// Régua dos eixos da nota: ~100 é um bom desempenho, a escala vai a 200
const AXIS_SCALE = 200;

export function OverviewTab({ simulationIds, showSimulation, currentPlayerName = "" }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("overview", simulationIds);
  if (!data) return <TabStatus loading={isLoading} title="o Geral" error={error} onRetry={() => void refetch()} />;

  const labels = data.players.map((p) => playerLabel(p, showSimulation));
  const colorOf = playerColors(labels);

  return (
    <div className="grid gap-5">
      {data.players.length > 0 && <Headline report={data} currentPlayerName={currentPlayerName} />}
      <Ranking report={data} currentPlayerName={currentPlayerName} showSimulation={showSimulation} colorOf={colorOf} />
      {data.players.length > 0 && (
        <ScoreAxes
          report={data}
          currentPlayerName={currentPlayerName}
          showSimulation={showSimulation}
          colorOf={colorOf}
        />
      )}
    </div>
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
              {you && (
                <span className="text-lg font-semibold">
                  {you.score ? `Nota ${displayNumber(you.score.total, 0)}` : "Sem nota ainda"} · retorno{" "}
                  {displaySignedPercent(you.return_percent)}
                </span>
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
              {you && !you.score && (
                <span className="text-[13px] text-muted-foreground">
                  A nota sai em <b className="text-foreground">{Math.max(min_score_days - you.days, 0)} pregões</b>:
                  antes de ~3 meses, anualizar o retorno engana.
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
  showSimulation,
  colorOf,
}: {
  report: OverviewReport;
  currentPlayerName: string;
  showSimulation: boolean;
  colorOf: (label: string) => string;
}) {
  const topScore = Math.max(...report.players.map((p) => Number(p.score?.total ?? 0)), 1);

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Ranking</CardTitle>
        <CardDescription>Ordenado pelo critério da partida: {VICTORY_CRITERIA[report.criterion].label}</CardDescription>
      </CardHeader>
      {report.players.length === 0 ? (
        <CardContent>
          <p className="py-6 text-center text-[13px] text-muted-foreground">
            Ninguém tem patrimônio registrado ainda. O ranking aparece depois do primeiro pregão.
          </p>
        </CardContent>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>#</TableHead>
              <TableHead>Jogador</TableHead>
              <TableHead>
                <MetricLabel metric={SCORE} />
              </TableHead>
              <TableHead numeric>Patrimônio</TableHead>
              <TableHead numeric>Retorno</TableHead>
              <TableHead numeric>Pregões</TableHead>
              <TableHead numeric>Distância do líder</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.players.map((p: Player) => {
              const label = playerLabel(p, showSimulation);
              const isYou = p.player_nickname === currentPlayerName;
              const change = Number(p.return_percent);
              return (
                <TableRow key={playerLabel(p, true)} variant={isYou ? "current" : "default"}>
                  <TableCell>
                    <span
                      className={cn(
                        "grid size-7 place-content-center rounded-md font-mono text-xs font-semibold",
                        p.position === 1 ? "bg-foreground text-primary-foreground" : "bg-muted",
                      )}
                    >
                      {p.position}
                    </span>
                  </TableCell>
                  <TableCell>
                    <PlayerCell label={label} color={colorOf(label)} isYou={isYou} />
                  </TableCell>
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
                  <TableCell numeric>{displayMoney(p.total_networth)}</TableCell>
                  <TableCell numeric>
                    <span className={change > 0 ? "text-success" : change < 0 ? "text-destructive" : undefined}>
                      {displaySignedPercent(p.return_percent)}
                    </span>
                  </TableCell>
                  <TableCell numeric>{p.days}</TableCell>
                  <TableCell numeric>{displayCriterionGap(report.criterion, p.leader_gap)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}

/** A nota em 4 eixos, cada um numa régua de 0 a 200 com a marca do 100 e a do líder. */
function ScoreAxes({
  report,
  currentPlayerName,
  showSimulation,
  colorOf,
}: {
  report: OverviewReport;
  currentPlayerName: string;
  showSimulation: boolean;
  colorOf: (label: string) => string;
}) {
  const scored = report.players.filter((p) => p.score);
  const labels = scored.map((p) => playerLabel(p, showSimulation));
  const yours = scored.find((p) => p.player_nickname === currentPlayerName);
  const [selected, setSelected] = useState<string | undefined>(yours ? playerLabel(yours, showSimulation) : labels[0]);
  const player = scored.find((p) => playerLabel(p, showSimulation) === selected) ?? scored[0];
  const leader = report.players[0]?.score ? report.players[0] : undefined;

  if (!player?.score) {
    const sample = report.players.find((p) => p.player_nickname === currentPlayerName) ?? report.players[0];
    return (
      <Card>
        <CardHeader>
          <CardTitle>Nota</CardTitle>
          <CardDescription>A nota só existe a partir de {report.min_score_days} pregões.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            <span className="text-[13px]">
              <b className="font-mono">{sample.days}</b> de {report.min_score_days} pregões
            </span>
            <span className="h-2 w-56 overflow-hidden rounded-full bg-muted">
              <span
                className="block h-full rounded-full bg-primary"
                style={{ width: `${Math.min(sample.days / report.min_score_days, 1) * 100}%` }}
              />
            </span>
            <span className="text-[13px] text-muted-foreground">
              Antes de ~3 meses, anualizar o retorno engana. Quem ainda não tem nota fica atrás no ranking.
            </span>
          </div>
        </CardContent>
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
                <dl className="grid gap-1 text-xs">
                  {axis.metrics.map((m) => (
                    <div key={m.metric} className="flex justify-between gap-2">
                      <dt className="text-muted-foreground">{SCORE_METRICS[m.metric].label}</dt>
                      <dd className="font-mono">
                        {displayMetric(SCORE_METRICS[m.metric], m.value)} ·{" "}
                        {m.points === null ? "—" : `${displayNumber(m.points, 0)} pts`}
                      </dd>
                    </div>
                  ))}
                </dl>
              </div>
            );
          })}
        </div>
        {leader && (
          <p className="mt-4 text-xs text-muted-foreground">
            Marca preta = líder ({leader.player_nickname}); traço cinza = 100, um bom desempenho. Barra âmbar: abaixo do
            líder nesse eixo.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
