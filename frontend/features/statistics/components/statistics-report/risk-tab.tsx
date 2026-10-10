import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { displayPercent } from "@/shared/lib/utils/display";
import type { RiskReport } from "@/types";
import { stringToColor } from "@/shared/lib/utils";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerLabel } from "../../lib/player-label";
import {
  ANNUAL_VOLATILITY,
  DRAWDOWN,
  MAX_DRAWDOWN,
  RISK_RETURN,
  ROLLING_VOLATILITY,
  SAMPLE_DAYS,
  SHARPE_RATIO,
  SORTINO_RATIO,
  TIME_UNDERWATER,
  WORST_MONTH,
} from "../../lib/metrics";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

export function RiskTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading } = useStatisticsReport("risk", simulationIds);
  if (!data) return <TabStatus loading={isLoading} />;

  const players = data.players.map((p) => {
    const label = playerLabel(p, showSimulation);
    return { player: p, label, color: stringToColor(label) };
  });
  const lines = (pick: (p: RiskReport["players"][number]) => LineSeries["points"]): LineSeries[] =>
    players.map(({ player, label, color }) => ({ key: label, label, color, points: pick(player) }));
  const seriesSetKey = players.map((p) => p.label).join("|");
  const percent = (v: string) => displayPercent(v);
  const axisPercent = (v: number) => displayPercent(v, 0);

  // Um ponto por jogador que já tem volatilidade e retorno anual
  const points = players.filter(({ player }) => player.annual_volatility !== null && player.annual_return !== null);

  return (
    <div className="space-y-6">
      <ChartCard metric={DRAWDOWN}>
        <PlayerLineChart
          key={seriesSetKey}
          series={lines((p) => p.drawdown)}
          format={percent}
          axisFormat={axisPercent}
        />
      </ChartCard>

      <ChartCard
        metric={ROLLING_VOLATILITY}
        description={`A volatilidade anual dos últimos ${data.rolling_window} pregões (~3 meses), dia a dia`}
      >
        <PlayerLineChart
          key={seriesSetKey}
          series={lines((p) => p.rolling_volatility)}
          format={percent}
          axisFormat={axisPercent}
        />
      </ChartCard>

      <ChartCard metric={RISK_RETURN}>
        {points.length === 0 ? (
          <div className="h-72 flex items-center justify-center border border-dashed rounded-md text-sm text-muted-foreground">
            Aparece a partir do 3º dia de simulação.
          </div>
        ) : (
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 12, right: 24, left: 24, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  type="number"
                  dataKey="volatility"
                  name="Volatilidade anual"
                  tickFormatter={axisPercent}
                  label={{ value: "Volatilidade anual (risco)", position: "insideBottom", offset: -12 }}
                />
                <YAxis
                  type="number"
                  dataKey="return"
                  name="Retorno anual"
                  tickFormatter={axisPercent}
                  width={72}
                  label={{ value: "Retorno anual", angle: -90, position: "insideLeft" }}
                />
                <ZAxis range={[120, 120]} />
                <Tooltip formatter={(value: number) => displayPercent(value)} cursor={{ strokeDasharray: "3 3" }} />
                <Legend verticalAlign="top" />
                {points.map(({ player, label, color }) => (
                  <Scatter
                    key={label}
                    name={label}
                    fill={color}
                    data={[{ volatility: Number(player.annual_volatility), return: Number(player.annual_return) }]}
                  />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartCard>

      <MetricsTable
        title="Risco por jogador"
        rows={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        columns={[
          { metric: MAX_DRAWDOWN, value: (p) => p.max_drawdown },
          { metric: ANNUAL_VOLATILITY, value: (p) => p.annual_volatility },
          { metric: SHARPE_RATIO, value: (p) => p.sharpe_ratio },
          { metric: SORTINO_RATIO, value: (p) => p.sortino_ratio },
          { metric: TIME_UNDERWATER, value: (p) => p.time_underwater },
          { metric: WORST_MONTH, value: (p) => p.worst_month },
          { metric: SAMPLE_DAYS, value: (p) => p.days },
        ]}
      />
    </div>
  );
}
