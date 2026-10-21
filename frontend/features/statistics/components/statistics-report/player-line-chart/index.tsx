import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { niceTicks } from "@/shared/lib/chart-scale";
import { displayShortMonthYear } from "@/shared/lib/utils/display";
import { useStaticChartVisibility } from "@/shared/hooks/useStaticChartVisibility";
import { LineChartLegend } from "./chart-legend";
import { LineChartTooltip } from "./chart-tooltip";
import { buildChartData, monthStartTicks, type ChartAxis, type LineChartRow } from "./utils";
import type { LineSeries } from "./series";

export type { LineSeries } from "./series";

interface PlayerLineChartProps {
  series: LineSeries[];
  format: (value: string) => string;
  axisFormat: (value: number) => string;
  axis?: ChartAxis;
  /** Rótulo do eixo X; o padrão é "abr/22" para datas e "12º" para o número do pregão */
  xTickFormat?: (x: number) => string;
  /** Posições fixas das marcas do eixo X, no lugar das automáticas */
  xTicks?: number[];
}

// A altura do gráfico e a do eixo X são fixas: com elas, o rótulo do fim de cada linha cai na posição exata
const CHART_HEIGHT = 340;
const MARGIN = { top: 12, right: 132, left: 8, bottom: 0 };
const X_AXIS_HEIGHT = 28;
const PLOT_HEIGHT = CHART_HEIGHT - MARGIN.top - X_AXIS_HEIGHT;
const LABEL_SPACING = 15;

/** Uma linha por série ao longo das datas, com o nome no fim de cada uma e a legenda clicável embaixo. */
export function PlayerLineChart({ series, format, axisFormat, axis = "date", xTickFormat, xTicks }: PlayerLineChartProps) {
  const { visible, toggle } = useStaticChartVisibility(series);
  const data = buildChartData(series, axis);

  if (!data.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-[10px] border border-dashed border-input text-sm text-muted-foreground">
        Nenhum dado disponível
      </div>
    );
  }

  const shown = series.filter((s) => visible[s.key]);
  const values = data.flatMap((row) => shown.map((s) => row.numbers[s.key]).filter((v) => v !== undefined));
  const ticks = niceTicks(Math.min(...values, 0), Math.max(...values, 0));
  const [floor, ceiling] = [ticks[0], ticks[ticks.length - 1]];
  // No eixo de datas, uma marca por mês: sem isso o mesmo mês se repete em dias diferentes
  const dateTicks =
    xTicks ?? (axis === "date" ? monthStartTicks(data[0].x, data[data.length - 1].x) : undefined);
  const yOf = (value: number) => MARGIN.top + (1 - (value - floor) / (ceiling - floor || 1)) * PLOT_HEIGHT;

  // Último valor de cada linha visível, do topo para baixo; o rótulo que colide desce
  const ends = shown
    .map((s) => {
      const last = [...data].reverse().find((row) => row.numbers[s.key] !== undefined);
      return last ? { series: s, y: yOf(last.numbers[s.key]) } : null;
    })
    .filter((end): end is { series: LineSeries; y: number } => end !== null)
    .sort((a, b) => a.y - b.y)
    .reduce<{ series: LineSeries; y: number }[]>((placed, end) => {
      const previous = placed.at(-1);
      return [...placed, { ...end, y: previous ? Math.max(end.y, previous.y + LABEL_SPACING) : end.y }];
    }, []);

  return (
    <div className="grid gap-3">
      <div className="relative">
        <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
          <ComposedChart data={data} margin={MARGIN}>
            <CartesianGrid vertical={false} stroke="var(--border)" />

            <XAxis
              dataKey="x"
              type="number"
              scale={axis === "date" ? "time" : "linear"}
              domain={["dataMin", "dataMax"]}
              tickFormatter={(v: number) =>
                xTickFormat ? xTickFormat(v) : axis === "date" ? displayShortMonthYear(new Date(v)) : `${v}º`
              }
              ticks={dateTicks}
              minTickGap={56}
              tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
              axisLine={false}
              tickLine={false}
              height={X_AXIS_HEIGHT}
            />

            <YAxis
              ticks={ticks}
              domain={[floor, ceiling]}
              tickFormatter={axisFormat}
              width={72}
              tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
              axisLine={false}
              tickLine={false}
            />

            <Tooltip content={(props) => <LineChartTooltip {...props} format={format} axis={axis} />} />

            {series
              .filter((s) => s.area)
              .map((s) => (
                <Area
                  key={`${s.key}-area`}
                  dataKey={(row: LineChartRow) => row.numbers[s.key]}
                  stroke="none"
                  fill={s.color}
                  fillOpacity={0.08}
                  connectNulls
                  hide={!visible[s.key]}
                  isAnimationActive={false}
                  legendType="none"
                  tooltipType="none"
                />
              ))}

            {series.map((s) => (
              <Line
                key={s.key}
                dataKey={(row: LineChartRow) => row.numbers[s.key]}
                name={s.key}
                stroke={s.color}
                strokeOpacity={s.muted ? 0.35 : 1}
                strokeWidth={s.emphasis ? 2.5 : 1.5}
                strokeDasharray={s.dashed ? "6 4" : undefined}
                dot={false}
                connectNulls
                hide={!visible[s.key]}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>

        {/* Nome de cada linha no fim, na cor dela */}
        <div
          className="pointer-events-none absolute inset-y-0 right-0 text-[11px]"
          style={{ width: MARGIN.right }}
          aria-hidden="true"
        >
          {ends.map(({ series: s, y }) => (
            <span
              key={s.key}
              className={`absolute left-2 max-w-[calc(100%-0.5rem)] -translate-y-1/2 truncate leading-none ${s.emphasis ? "font-bold" : "font-medium"}`}
              style={{ top: y, color: s.color }}
            >
              {s.label}
            </span>
          ))}
        </div>
      </div>

      <LineChartLegend series={series} visible={visible} toggle={toggle} />
    </div>
  );
}
