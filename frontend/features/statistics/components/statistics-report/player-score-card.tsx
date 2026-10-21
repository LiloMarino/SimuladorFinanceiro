import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayNumber } from "@/shared/lib/utils/display";
import type { OverviewReport, ScoreMetric } from "@/types";
import { AXIS_SCALE, SCORE_AXES, SCORE_METRICS, displayMetric } from "../../lib/metrics";

type Player = OverviewReport["players"][number];

// Métricas da nota que o relatório lê como contagem de meses ("7 de 12"), não como percentual
const MONTH_COUNT_METRICS: ScoreMetric[] = ["months_above_cdi", "positive_months"];

/** Valor da métrica na nota; os meses entram como contagem ("7 de 12"), como a Rentabilidade mostra. */
function displayScoreMetric(metric: ScoreMetric, value: string | null, months: number) {
  if (value !== null && MONTH_COUNT_METRICS.includes(metric) && months > 0) {
    return `${Math.round(Number(value) * months)} de ${months}`;
  }
  return displayMetric(SCORE_METRICS[metric], value);
}

/** Cartão da nota de um jogador: o total e os quatro eixos, cada um com as métricas que o formam. */
export function PlayerScoreCard({
  report,
  player,
  currentPlayerName,
  action,
}: {
  report: OverviewReport;
  player: Player;
  currentPlayerName: string;
  action: React.ReactNode;
}) {
  const leader = report.players[0]?.score ? report.players[0] : undefined;
  if (!player.score) return null;

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
        <CardAction>{action}</CardAction>
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
