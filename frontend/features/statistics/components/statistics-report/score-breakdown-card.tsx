import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { displayNumber } from "@/shared/lib/utils/display";
import type { OverviewReport, Score } from "@/types";
import { playerLabel } from "../../lib/player-label";
import { SCORE, SCORE_AXES, SCORE_METRICS, displayMetric } from "../../lib/metrics";
import { MetricHint, MetricLabel } from "./metric-hint";
import { PlayerPills } from "./shared";

// Cada eixo tem ~100 como desempenho bom; a barra vai até o dobro disso
const AXIS_SCALE = 200;

interface Props {
  report: OverviewReport;
  showSimulation: boolean;
  currentPlayerName: string;
}

/** De onde vem a nota de cada jogador: os eixos e, dentro deles, cada métrica com os seus pontos. */
export function ScoreBreakdownCard({ report, showSimulation, currentPlayerName }: Props) {
  const [selected, setSelected] = useState<string | null>(null);
  const players = report.players.map((p) => ({ player: p, label: playerLabel(p, showSimulation) }));
  // Começa no jogador logado; sem ele na lista, no primeiro do ranking
  const current =
    players.find((p) => p.label === selected) ??
    players.find((p) => p.player.player_nickname === currentPlayerName) ??
    players[0];

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <MetricLabel metric={SCORE} />
        </CardTitle>
        <CardDescription>
          A nota é a soma dos quatro eixos; cada eixo é a média dos pontos das suas métricas.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        <PlayerPills labels={players.map((p) => p.label)} current={current?.label} onSelect={setSelected} />

        {current?.player.score ? (
          <ScoreAxes score={current.player.score} />
        ) : (
          <p className="text-sm text-muted-foreground">
            A nota aparece a partir de {report.min_score_days} pregões (~3 meses): antes disso, anualizar o retorno
            engana.{" "}
            {current &&
              `Faltam ${Math.max(report.min_score_days - (current.player.days - 1), 0)} pregões para ${current.label}.`}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function ScoreAxes({ score }: { score: Score }) {
  return (
    <div className="space-y-6">
      <p className="text-4xl font-bold">{SCORE.format(score.total)}</p>

      <div className="grid gap-6 lg:grid-cols-2">
        {score.axes.map((axis) => {
          const info = SCORE_AXES[axis.axis];
          const width = axis.points === null ? 0 : Math.min(Number(axis.points) / AXIS_SCALE, 1) * 100;

          return (
            <div key={axis.axis} className="space-y-2">
              <div className="flex items-baseline justify-between gap-2">
                <div>
                  <p className="font-semibold">{info.label}</p>
                  <p className="text-xs text-muted-foreground">{info.description}</p>
                </div>
                <p className="text-xl font-semibold">{points(axis.points)}</p>
              </div>

              {/* Barra do eixo, com a marca dos 100 pontos */}
              <div className="relative h-2.5 rounded-full bg-muted">
                <div className="h-2.5 rounded-full bg-primary" style={{ width: `${width}%` }} />
                <div className="absolute inset-y-0 left-1/2 w-px bg-foreground/40" title="100 pontos" />
              </div>

              <ul className="space-y-1 text-sm">
                {axis.metrics.map((m) => {
                  const metric = SCORE_METRICS[m.metric];
                  return (
                    <li key={m.metric} className="flex items-center justify-between gap-2">
                      <span className="flex items-center gap-1 text-muted-foreground">
                        {metric.label}
                        <MetricHint metric={metric} />
                      </span>
                      <span>
                        {displayMetric(metric, m.value)} <span className="text-muted-foreground">→</span>{" "}
                        <span className="font-medium">{points(m.points)} pts</span>
                      </span>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function points(value: string | null) {
  return value === null ? "—" : displayNumber(value, 1);
}
