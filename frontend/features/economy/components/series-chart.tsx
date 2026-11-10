import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import { monthTicks, type EconomyRow } from "../lib/economy";
import { CHART_FONT_SIZE, CHART_TICK } from "@/shared/lib/chart-text";

type SeriesKey = "growth" | "unemployment" | "debt" | "dollar";

type SeriesChartProps = {
  rows: EconomyRow[];
  dataKey: SeriesKey;
  /** Nome da linha no tooltip */
  label: string;
  color: string;
  /** Linha de referência tracejada, como o limite em que a dívida passa a cobrar prêmio */
  reference?: { value: number; label: string };
  /** Em pixels ou em % da altura do pai, que precisa ter altura definida */
  height?: number | `${number}%`;
  /** Como o valor aparece no eixo e no tooltip; o padrão é percentual */
  format?: (value: number, digits: number) => string;
};

function SeriesTooltip({
  active,
  payload,
  seriesName,
  format,
}: {
  active?: boolean;
  payload?: { payload: EconomyRow; value: number | null }[];
  seriesName: string;
  format: (value: number, digits: number) => string;
}) {
  const entry = payload?.[0];
  if (!active || !entry || entry.value === null) return null;
  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <span className="text-muted-foreground">{displayDate(new Date(entry.payload.time))}</span>
      <span className="flex items-center justify-between gap-6">
        <span>{seriesName}</span>
        <span className="font-mono font-semibold">{format(entry.value, 1)}</span>
      </span>
    </div>
  );
}

/** Uma série da economia ao longo da partida, em % no eixo vertical. */
export function SeriesChart({
  rows,
  dataKey,
  label,
  color,
  reference,
  height = 190,
  format = displayPercent,
}: SeriesChartProps) {
  if (rows.length < 2) {
    return (
      <div
        className="flex items-center justify-center rounded-[10px] border border-dashed border-input text-sm text-muted-foreground"
        style={{ height }}
      >
        O gráfico aparece quando a partida andar um pouco.
      </div>
    );
  }

  const ticks = monthTicks(rows.map((row) => row.time));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          {...(ticks.length > 0 && { ticks })}
          tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={dataKey === "dollar" ? ["auto", "auto"] : [(min: number) => Math.min(0, min), "auto"]}
          tickFormatter={(value: number) => format(value, dataKey === "dollar" ? 2 : 0)}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
          width={dataKey === "dollar" ? 56 : 40}
        />
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={<SeriesTooltip seriesName={label} format={format} />}
        />
        {reference && (
          <ReferenceLine
            y={reference.value}
            stroke="var(--muted-foreground)"
            strokeDasharray="5 4"
            label={{
              value: reference.label,
              position: "insideTopRight",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--muted-foreground)",
            }}
          />
        )}
        <Line dataKey={dataKey} type="stepAfter" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
