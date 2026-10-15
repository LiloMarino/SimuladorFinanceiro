import { useState } from "react";
import {
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceArea,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayList, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { RiskReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerColors } from "../../lib/player-colors";
import { playerLabel } from "../../lib/player-label";
import {
  ANNUAL_VOLATILITY,
  DRAWDOWN,
  MAX_DRAWDOWN,
  ROLLING_VOLATILITY,
  SAMPLE_DAYS,
  SHARPE_RATIO,
  SORTINO_RATIO,
  TIME_UNDERWATER,
  WORST_MONTH,
} from "../../lib/metrics";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

type Player = RiskReport["players"][number];
type View = "DRAWDOWN" | "VOLATILITY";

// A dispersão precisa de alguns pregões para a oscilação existir
const MIN_SCATTER_DAYS = 3;

export function RiskTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("risk", simulationIds);
  const { data: returns } = useStatisticsReport("returns", simulationIds);
  const [view, setView] = useState<View>("DRAWDOWN");
  if (!data) return <TabStatus loading={isLoading} title="o Risco" error={error} onRetry={() => void refetch()} />;

  const labels = data.players.map((p) => playerLabel(p, showSimulation));
  const colorOf = playerColors(labels);
  const cdiReturn = returns?.benchmarks.find((b) => b.series === "CDI")?.annual_return ?? null;

  const lines: LineSeries[] = data.players.map((p) => {
    const label = playerLabel(p, showSimulation);
    return {
      key: label,
      label,
      color: colorOf(label),
      points: view === "DRAWDOWN" ? p.drawdown : p.rolling_volatility,
      emphasis: p.player_nickname === currentPlayerName,
    };
  });

  return (
    <div className="grid gap-5">
      <RiskReturn
        players={data.players}
        cdiReturn={cdiReturn}
        currentPlayerName={currentPlayerName}
        showSimulation={showSimulation}
        colorOf={colorOf}
      />

      <ChartCard
        metric={view === "DRAWDOWN" ? DRAWDOWN : ROLLING_VOLATILITY}
        action={
          <ToggleGroup
            variant="segmented"
            aria-label="Série do gráfico"
            value={[view]}
            onValueChange={(values) => values[0] && setView(values[0] as View)}
          >
            <ToggleGroupItem value="DRAWDOWN">Distância do pico</ToggleGroupItem>
            <ToggleGroupItem value="VOLATILITY">Volatilidade · {data.rolling_window} pregões</ToggleGroupItem>
          </ToggleGroup>
        }
      >
        <PlayerLineChart
          key={`${view}|${labels.join("|")}`}
          series={lines}
          format={(v) => displayPercent(v)}
          axisFormat={(v) => displayPercent(v, 0)}
        />
      </ChartCard>

      <MetricsTable
        title="Risco por jogador"
        description="Verde = melhor da sala em cada métrica. Com menos de ~63 pregões, leia com cautela."
        rows={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        colorOf={colorOf}
        columns={[
          { metric: MAX_DRAWDOWN, value: (r) => r.max_drawdown, best: "min" },
          { metric: ANNUAL_VOLATILITY, value: (r) => r.annual_volatility, best: "min" },
          { metric: SHARPE_RATIO, value: (r) => r.sharpe_ratio, best: "max" },
          { metric: SORTINO_RATIO, value: (r) => r.sortino_ratio, best: "max" },
          { metric: TIME_UNDERWATER, value: (r) => r.time_underwater, best: "min" },
          { metric: WORST_MONTH, value: (r) => r.worst_month, best: "max" },
          { metric: SAMPLE_DAYS, value: (r) => r.days },
        ]}
      />
    </div>
  );
}

/** Um ponto por jogador: quanto oscilou × quanto rendeu, com o CDI como referência sem oscilar. */
function RiskReturn({
  players,
  cdiReturn,
  currentPlayerName,
  showSimulation,
  colorOf,
}: {
  players: Player[];
  cdiReturn: string | null;
  currentPlayerName?: string;
  showSimulation: boolean;
  colorOf: (label: string) => string;
}) {
  const measured = players.filter(
    (p) => p.annual_volatility !== null && p.annual_return !== null && p.days >= MIN_SCATTER_DAYS,
  );
  // Jogadores no mesmo ponto (ex.: todos parados em caixa) viram um ponto só com os nomes juntos
  const byPosition = new Map<string, { labels: string[]; x: number; y: number }>();
  for (const p of measured) {
    const x = Number(p.annual_volatility);
    const y = Number(p.annual_return);
    const key = `${x.toFixed(4)}|${y.toFixed(4)}`;
    const point = byPosition.get(key) ?? { labels: [], x, y };
    point.labels.push(playerLabel(p, showSimulation));
    byPosition.set(key, point);
  }
  const points = [...byPosition.values()].map((p) => ({ ...p, label: displayList(p.labels), colorKey: p.labels[0] }));
  const cdi = cdiReturn !== null ? Number(cdiReturn) : null;
  const maxX = Math.max(...points.map((p) => p.x), 0.01) * 1.15;
  const ys = [...points.map((p) => p.y), cdi ?? 0];
  const minY = Math.min(...ys, 0) * 1.15;
  const maxY = Math.max(...ys, 0.01) * 1.15;
  const medianX = points.length ? [...points].sort((a, b) => a.x - b.x)[Math.floor(points.length / 2)].x : maxX / 2;

  // "Melhor da sala" só faz sentido com pelo menos dois Sharpes medidos
  const withSharpe = measured.filter((p) => p.sharpe_ratio !== null);
  const bestSharpe =
    withSharpe.length >= 2
      ? [...withSharpe].sort((a, b) => Number(b.sharpe_ratio) - Number(a.sharpe_ratio))[0]
      : undefined;
  const belowCdi = cdi !== null ? measured.filter((p) => Number(p.annual_return) < cdi) : [];
  const you = measured.find((p) => p.player_nickname === currentPlayerName);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risco × retorno</CardTitle>
        <CardDescription>
          Um ponto por jogador no período inteiro. Quanto mais pra cima e pra esquerda, melhor.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {points.length === 0 ? (
          <div className="flex h-72 flex-col items-center justify-center gap-1 rounded-[10px] border border-dashed border-input text-center">
            <span className="font-semibold">Aparece no {MIN_SCATTER_DAYS}º pregão</span>
            <span className="text-[13px] text-muted-foreground">Com menos de 3 dias não dá pra medir oscilação.</span>
          </div>
        ) : (
          <div className="grid gap-5 lg:grid-cols-[1.7fr_1fr]">
            <div className="h-90">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 16, right: 24, left: 8, bottom: 16 }}>
                  <CartesianGrid stroke="var(--border)" />
                  {cdi !== null && (
                    <ReferenceArea
                      x1={0}
                      x2={medianX}
                      y1={cdi}
                      y2={maxY}
                      fill="var(--success)"
                      fillOpacity={0.07}
                      ifOverflow="hidden"
                    />
                  )}
                  <XAxis
                    type="number"
                    dataKey="x"
                    domain={[0, maxX]}
                    tickFormatter={(v: number) => displayPercent(v, 0)}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    name="Volatilidade anual"
                    label={{
                      value: "Volatilidade anual (risco) →",
                      position: "insideBottom",
                      offset: -8,
                      fontSize: 11,
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    domain={[minY, maxY]}
                    tickFormatter={(v: number) => displayPercent(v, 0)}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    width={56}
                    name="Retorno anual"
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                    formatter={(v, name) => [displayPercent(Number(v)), name]}
                  />
                  <Scatter data={points} isAnimationActive={false}>
                    {points.map((p) => (
                      <Cell key={p.label} fill={colorOf(p.colorKey)} />
                    ))}
                    <LabelList
                      dataKey="label"
                      content={({ x, y, width, height, value, index }) => {
                        // Na metade direita o nome vai à esquerda do ponto, para caber no gráfico
                        const toLeft = index !== undefined && points[index].x > maxX / 2;
                        const cx = Number(x) + Number(width) / 2;
                        return (
                          <text
                            x={toLeft ? cx - 10 : cx + 10}
                            y={Number(y) + Number(height) / 2 + 4}
                            textAnchor={toLeft ? "end" : "start"}
                            fontSize={11}
                            fill="var(--foreground)"
                          >
                            {value}
                          </text>
                        );
                      }}
                    />
                  </Scatter>
                  {cdi !== null && (
                    <Scatter
                      data={[{ x: 0, y: cdi, label: `CDI · ${displayPercent(cdi)} sem oscilar` }]}
                      fill="var(--faint-foreground)"
                      shape="diamond"
                    >
                      <LabelList dataKey="label" position="right" fontSize={11} fill="var(--muted-foreground)" />
                    </Scatter>
                  )}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="grid content-start gap-3">
              <div className="grid gap-1 rounded-[10px] bg-subtle p-3.5 text-[13px]">
                <span className="font-semibold">Leitura rápida</span>
                {bestSharpe && (
                  <span className="text-muted-foreground">
                    <b className="text-foreground">{bestSharpe.player_nickname}</b> rendeu mais por unidade de
                    oscilação: Sharpe{" "}
                    <b className="font-mono text-foreground">{displayNumber(bestSharpe.sharpe_ratio ?? 0)}</b>, o melhor
                    da sala.
                  </span>
                )}
                {belowCdi.length > 0 && (
                  <span className="text-muted-foreground">
                    {belowCdi.length === measured.length && belowCdi.length > 1
                      ? "Todos ficaram"
                      : `${displayList(belowCdi.map((p) => p.player_nickname))} ${belowCdi.length > 1 ? "ficaram" : "ficou"}`}{" "}
                    abaixo do CDI.
                  </span>
                )}
              </div>
              {you && (
                <div className="grid gap-1 rounded-[10px] bg-warning-soft/60 p-3.5 text-[13px]">
                  <span className="font-semibold">Você</span>
                  <span className="text-muted-foreground">
                    Oscilou <b className="font-mono text-foreground">{displayPercent(you.annual_volatility ?? 0)}</b> ao
                    ano pra render <b className="font-mono text-foreground">{displayPercent(you.annual_return ?? 0)}</b>
                    {cdi !== null && <> (CDI: {displayPercent(cdi)})</>}. Sharpe{" "}
                    <b className="font-mono text-foreground">
                      {you.sharpe_ratio ? displayNumber(you.sharpe_ratio) : "—"}
                    </b>
                    .
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
