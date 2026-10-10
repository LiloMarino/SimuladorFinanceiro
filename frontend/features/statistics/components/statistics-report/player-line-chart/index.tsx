import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { displayMonthYear } from "@/shared/lib/utils/display";
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
      <div className="h-72 flex items-center justify-center border border-dashed rounded-md text-sm text-muted-foreground">
        Nenhum dado disponível
      </div>
    );
  }

  return (
    <div className="h-[380px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 16, left: 24, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />

          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => displayMonthYear(new Date(v))}
            minTickGap={40}
          />

          <YAxis tickFormatter={axisFormat} width={96} />

          <Tooltip content={<LineChartTooltip format={format} />} />

          <Legend content={<LineChartLegend series={series} visible={visible} toggle={toggle} />} />

          {series.map((s) => (
            <Line
              key={s.key}
              dataKey={(row: LineChartRow) => row.numbers[s.key]}
              name={s.key}
              stroke={s.color}
              strokeWidth={s.dashed ? 1.5 : 2.5}
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
