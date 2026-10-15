import { useState } from "react";
import {
  CartesianGrid,
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
import { displayList, displayNumber, displayPercent, displayPercentagePoints } from "@/shared/lib/utils/display";
import type { RiskReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerColors } from "../../lib/player-colors";
import { playerLabel, youLabel } from "../../lib/player-label";
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

export function RiskTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("risk", simulationIds, onlyPlayer);
  const { data: returns } = useStatisticsReport("returns", simulationIds);
  const [view, setView] = useState<View>("DRAWDOWN");
  if (!data) return <TabStatus loading={isLoading} title="o Risco" error={error} onRetry={() => void refetch()} />;

  const labels = data.players.map((p) => playerLabel(p, simulationIds, currentPlayerName));
  const someoneIsYou = data.players.some((p) => p.player_nickname === currentPlayerName);
  const colorOf = playerColors(labels);
  const cdiReturn = returns?.benchmarks.find((b) => b.series === "CDI")?.annual_return ?? null;

  // Distância do pico: a sua linha ganha área e as dos outros ficam de fundo
  const lines: LineSeries[] = data.players.map((p) => {
    const label = playerLabel(p, simulationIds, currentPlayerName);
    const you = p.player_nickname === currentPlayerName;
    return {
      key: label,
      label: youLabel(label, you),
      color: colorOf(label),
      points: view === "DRAWDOWN" ? p.drawdown : p.rolling_volatility,
      emphasis: you,
      area: view === "DRAWDOWN" && you,
      muted: view === "DRAWDOWN" && someoneIsYou && !you,
    };
  });

  return (
    <div className="grid gap-5">
      <RiskReturn
        players={data.players}
        cdiReturn={cdiReturn}
        currentPlayerName={currentPlayerName}
        simulationIds={simulationIds}
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
        simulationIds={simulationIds}
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

/** O Sharpe em palavras: quanto retorno veio para cada unidade de oscilação. */
function sharpeVerdict(sharpe: number) {
  if (sharpe < 0) return "o risco não compensou";
  if (sharpe < 0.5) return "o risco foi pago, mas pouco";
  if (sharpe < 1) return "o risco foi bem pago";
  return "o risco foi muito bem pago";
}

/** Um ponto por jogador: quanto oscilou × quanto rendeu, com o CDI como referência sem oscilar. */
function RiskReturn({
  players,
  cdiReturn,
  currentPlayerName,
  simulationIds,
  colorOf,
}: {
  players: Player[];
  cdiReturn: string | null;
  currentPlayerName?: string;
  simulationIds: number[];
  colorOf: (label: string) => string;
}) {
  const measured = players.filter(
    (p) => p.annual_volatility !== null && p.annual_return !== null && p.days >= MIN_SCATTER_DAYS,
  );
  // Jogadores no mesmo ponto (ex.: todos parados em caixa) viram um ponto só com os nomes juntos
  const byPosition = new Map<string, { keys: string[]; names: string[]; x: number; y: number; you: boolean }>();
  for (const p of measured) {
    const x = Number(p.annual_volatility);
    const y = Number(p.annual_return);
    const key = `${x.toFixed(4)}|${y.toFixed(4)}`;
    const point = byPosition.get(key) ?? { keys: [], names: [], x, y, you: false };
    const isYou = p.player_nickname === currentPlayerName;
    const label = playerLabel(p, simulationIds, currentPlayerName);
    point.keys.push(label);
    point.names.push(youLabel(label, isYou));
    point.you = point.you || isYou;
    byPosition.set(key, point);
  }
  const points = [...byPosition.values()].map((p) => ({
    ...p,
    label: displayList(p.names),
    colorKey: p.keys[0],
  }));
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
            <div className="relative h-90">
              {/* Quadrantes: o melhor é em cima e à esquerda, o pior embaixo e à direita */}
              <span className="pointer-events-none absolute top-5 left-18 text-[11px] font-medium text-success">
                Mais retorno, menos risco
              </span>
              <span className="pointer-events-none absolute right-8 bottom-14 text-[11px] font-medium text-destructive">
                Menos retorno, mais risco
              </span>
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
                    width={64}
                    name="Retorno anual"
                    label={{
                      value: "Retorno anual →",
                      angle: -90,
                      position: "insideLeft",
                      offset: 8,
                      fontSize: 11,
                      fill: "var(--muted-foreground)",
                      style: { textAnchor: "middle" },
                    }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                    formatter={(v, name) => [displayPercent(Number(v)), name]}
                  />
                  <Scatter
                    data={points}
                    isAnimationActive={false}
                    shape={(props: { cx?: number; cy?: number; payload?: (typeof points)[number] }) => (
                      // Você em destaque: ponto maior com borda branca
                      <circle
                        cx={props.cx}
                        cy={props.cy}
                        r={props.payload?.you ? 8 : 6}
                        fill={colorOf(props.payload?.colorKey ?? "")}
                        stroke="var(--card)"
                        strokeWidth={props.payload?.you ? 2 : 0}
                      />
                    )}
                  >
                    <LabelList
                      dataKey="label"
                      content={({ x, y, width, height, value, index }) => {
                        // Na metade direita o nome vai à esquerda do ponto, para caber no gráfico
                        const point = index !== undefined ? points[index] : undefined;
                        const toLeft = point !== undefined && point.x > maxX / 2;
                        const cx = Number(x) + Number(width) / 2;
                        return (
                          <text
                            x={toLeft ? cx - 12 : cx + 12}
                            y={Number(y) + Number(height) / 2 + 4}
                            textAnchor={toLeft ? "end" : "start"}
                            fontSize={11}
                            fontWeight={point?.you ? 700 : 500}
                            fill={point ? colorOf(point.colorKey) : "var(--foreground)"}
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
                    {cdi !== null && (
                      <>
                        :{" "}
                        <b className="font-mono text-foreground">
                          {displayPercentagePoints(Math.abs(Number(you.annual_return ?? 0) - cdi))}{" "}
                          {Number(you.annual_return ?? 0) >= cdi ? "acima" : "abaixo"} do CDI
                        </b>
                      </>
                    )}
                    . Sharpe{" "}
                    <b className="font-mono text-foreground">
                      {you.sharpe_ratio ? displayNumber(you.sharpe_ratio) : "—"}
                    </b>
                    {you.sharpe_ratio !== null && (
                      <>
                        : <b className="text-foreground">{sharpeVerdict(Number(you.sharpe_ratio))}</b>
                      </>
                    )}
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
