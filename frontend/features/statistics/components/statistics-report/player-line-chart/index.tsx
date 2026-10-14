import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { displayShortDate } from "@/shared/lib/utils/display";
import { useStaticChartVisibility } from "@/shared/hooks/useStaticChartVisibility";
import { LineChartLegend } from "./chart-legend";
import { LineChartTooltip } from "./chart-tooltip";
import { buildChartData, type LineChartRow } from "./utils";
import type { LineSeries } from "./series";

export type { LineSeries } from "./series";

interface PlayerLineChartProps {
  series: LineSeries[];
  format: (value: string) => string;
  axisFormat: (value: number) => string;
}

/** Uma linha por série ao longo das datas; a visibilidade de cada uma se alterna pela legenda. */
export function PlayerLineChart({ series, format, axisFormat }: PlayerLineChartProps) {
  const { visible, toggle } = useStaticChartVisibility(series);
  const data = buildChartData(series);

  if (!data.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-[10px] border border-dashed border-input text-sm text-muted-foreground">
        Nenhum dado disponível
      </div>
    );
  }

  return (
    <div className="h-[380px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 16, left: 24, bottom: 8 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />

          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => displayShortDate(new Date(v))}
            minTickGap={56}
            tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            tickFormatter={axisFormat}
            width={84}
            tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip content={(props) => <LineChartTooltip {...props} format={format} />} />

          <Legend content={<LineChartLegend series={series} visible={visible} toggle={toggle} />} />

          {series.map((s) => (
            <Line
              key={s.key}
              dataKey={(row: LineChartRow) => row.numbers[s.key]}
              name={s.key}
              stroke={s.color}
              strokeOpacity={s.muted ? 0.45 : 1}
              strokeWidth={s.emphasis ? 2.5 : 1.5}
              strokeDasharray={s.dashed ? "6 4" : undefined}
              dot={false}
              connectNulls
              hide={!visible[s.key]}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
