import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { EconomyRow } from "../lib/economy";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

type SeriesKey = "growth" | "unemployment" | "debt";

type SeriesChartProps = {
  rows: EconomyRow[];
  dataKey: SeriesKey;
  /** Nome da linha no tooltip */
  label: string;
  color: string;
  /** Linha de referência tracejada, como a tendência de crescimento */
  reference?: { value: number; label: string };
  height?: number;
};

function SeriesTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { payload: EconomyRow; value: number | null }[];
  label: string;
}) {
  const entry = payload?.[0];
  if (!active || !entry || entry.value === null) return null;
  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <span className="text-muted-foreground">{displayDate(new Date(entry.payload.time))}</span>
      <span className="flex items-center justify-between gap-6">
        <span>{label}</span>
        <span className="font-mono font-semibold">{displayPercent(entry.value, 1)}</span>
      </span>
    </div>
  );
}

/** Uma série da economia ao longo da partida, em % no eixo vertical. */
export function SeriesChart({ rows, dataKey, label, color, reference, height = 190 }: SeriesChartProps) {
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

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[(min: number) => Math.min(0, min), "auto"]}
          tickFormatter={(value: number) => displayPercent(value, 0)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={40}
        />
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={<SeriesTooltip label={label} />}
        />
        {reference && (
          <ReferenceLine
            y={reference.value}
            stroke="var(--muted-foreground)"
            strokeDasharray="5 4"
            label={{
              value: reference.label,
              position: "insideTopRight",
              fontSize: 10.5,
              fill: "var(--muted-foreground)",
            }}
          />
        )}
        <Line dataKey={dataKey} type="stepAfter" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
