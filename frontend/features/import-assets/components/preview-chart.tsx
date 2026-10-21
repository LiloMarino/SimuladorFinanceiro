import { CartesianGrid, Line, LineChart, ReferenceArea, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate } from "@/shared/lib/utils/display";
import type { FuturePreview } from "@/types";
import { previewChartData, yearTicks, type PreviewRow } from "../lib/preview-chart";

type PreviewChartProps = {
  series: FuturePreview["ibov"];
  height: number;
  /** Rótulo do eixo Y */
  formatValue: (value: number) => string;
  /** Valor no tooltip, com mais precisão que o eixo */
  formatTooltip: (value: number) => string;
  /** Quantas marcas de ano cabem no eixo X */
  maxYearTicks: number;
};

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

/** Real e gerado na mesma curva: o real em azul, o gerado em âmbar sobre a faixa que marca o futuro. */
export function PreviewChart({ series, height, formatValue, formatTooltip, maxYearTicks }: PreviewChartProps) {
  const { rows, lastRealTime, lastTime } = previewChartData(series);
  const firstTime = rows[0]?.time ?? 0;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 14, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={[firstTime, lastTime]}
          ticks={yearTicks(firstTime, lastTime, maxYearTicks)}
          tickFormatter={(t: number) => String(new Date(t).getFullYear())}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={["auto", "auto"]}
          tickCount={5}
          tickFormatter={formatValue}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={48}
        />
        {lastRealTime !== null && (
          <>
            <ReferenceArea x1={lastRealTime} x2={lastTime} fill="var(--chart-3)" fillOpacity={0.1} />
            <ReferenceLine
              x={lastRealTime}
              stroke="var(--faint-foreground)"
              strokeDasharray="3 3"
              label={{ value: "hoje", position: "top", fontSize: 10, fill: "var(--faint-foreground)" }}
            />
          </>
        )}
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={({ active, payload }) => {
            const row = payload?.[0]?.payload as PreviewRow | undefined;
            if (!active || !row) return null;
            const generated = row.real === undefined;
            return (
              <div className="rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                <div className="text-muted-foreground">{displayDate(new Date(row.time))}</div>
                <div className="font-mono font-semibold">
                  {formatTooltip((generated ? row.generated : row.real) ?? 0)}
                  <span className="ml-1.5 font-sans font-normal text-muted-foreground">
                    {generated ? "gerado" : "real"}
                  </span>
                </div>
              </div>
            );
          }}
        />
        <Line type="linear" dataKey="real" stroke="var(--chart-1)" strokeWidth={1.75} dot={false} isAnimationActive={false} />
        <Line
          type="linear"
          dataKey="generated"
          stroke="var(--chart-3)"
          strokeWidth={1.75}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
