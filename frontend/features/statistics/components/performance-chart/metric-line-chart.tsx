import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { formatMoney, formatMonthYear } from "@/shared/lib/utils/formatting";
import { useStaticChartVisibility } from "@/shared/hooks/useStaticChartVisibility";
import { PerformanceChartLegend } from "./chart-legend";
import { PerformanceChartTooltip } from "./chart-tooltip";
import { buildChartData } from "./utils";
import { buildPlayerSeries } from "./series";
import type { PlayerHistory, PerformanceMetric } from "@/types";

interface MetricLineChartProps {
  metric: PerformanceMetric;
  players: PlayerHistory[];
}

export function MetricLineChart({ metric, players }: MetricLineChartProps) {
  const series = buildPlayerSeries(players);
  const { visible, toggle } = useStaticChartVisibility(series);
  const data = buildChartData(players, metric);

  if (!data.length) {
    return (
      <div className="h-72 flex items-center justify-center border border-dashed rounded-md text-sm text-muted-foreground">
        Nenhum dado disponível
      </div>
    );
  }

  return (
    <div className="h-[380px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 12,
            right: 16,
            left: 24,
            bottom: 8,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => formatMonthYear(new Date(v))}
            minTickGap={40}
          />

          <YAxis tickFormatter={formatMoney} width={96} />

          <Tooltip content={<PerformanceChartTooltip />} />

          <Legend content={<PerformanceChartLegend series={series} visible={visible} toggle={toggle} />} />

          {series.map((s) => (
            <Line
              key={s.key}
              dataKey={s.key}
              name={s.label}
              stroke={s.color}
              strokeWidth={2.5}
              dot={false}
              hide={!visible[s.key]}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
