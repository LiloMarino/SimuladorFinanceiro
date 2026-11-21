import { addMonths, endOfMonth } from "date-fns";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { displayShortDate, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { GovernmentApproval } from "@/types";
import {
  ALL_GROUPS,
  PROJECTED_MONTHS,
  projection,
  selectedSeries,
  verdictCounts,
  verdictCountsSentence,
} from "../lib/approval";
import type { Selection } from "../lib/approval";
import { CHART_FONT_SIZE, CHART_TICK } from "@/shared/lib/chart-text";

type Row = {
  time: number;
  date: string;
  value?: number | undefined;
  projected?: number | undefined;
};

type ApprovalChartProps = {
  approval: GovernmentApproval;
  /** O total do eleitorado ou um grupo */
  selection?: Selection;
  height?: number;
};

/** A aprovação mês a mês, com o piso do impeachment tracejado, a carência, a posse e a projeção até o alvo. */
export function ApprovalChart({ approval, selection = ALL_GROUPS, height = 180 }: ApprovalChartProps) {
  const series = selectedSeries(approval, selection);
  const rows: Row[] = series.history.map((point) => ({
    time: parseLocalDate(point.date).getTime(),
    date: point.date,
    value: point.value,
  }));
  const last = rows.at(-1);

  // A projeção sai do último ponto e anda um terço do caminho até o alvo a cada fechamento
  if (last) {
    last.projected = last.value;
    const closing = endOfMonth(parseLocalDate(approval.closes_on));
    projection(series.value, series.target, PROJECTED_MONTHS).forEach((value, index) => {
      const time = endOfMonth(addMonths(closing, index)).getTime();
      rows.push({ time, date: "", projected: Math.round(value * 10) / 10 });
    });
  }

  const first = rows[0];
  const graceEnd = Math.min(parseLocalDate(approval.grace_until).getTime(), last?.time ?? Infinity);
  const lastProjected = rows.at(-1);
  const nearTarget = rows.at(-2);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 14, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          ticks={[0, 25, 50, 75, 100]}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        {first && graceEnd > first.time && (
          <ReferenceArea
            x1={first.time}
            x2={graceEnd}
            fill="var(--muted)"
            fillOpacity={0.7}
            label={{
              value: "carência: sem impeachment",
              position: "insideBottomLeft",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--faint-foreground)",
            }}
          />
        )}
        <ReferenceLine
          y={approval.floor}
          stroke="var(--destructive)"
          strokeDasharray="4 3"
          label={{
            value: `piso ${approval.floor}%`,
            position: "insideTopLeft",
            fontSize: CHART_FONT_SIZE,
            fill: "var(--destructive)",
          }}
        />
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={({ active, payload }) => {
            const row = payload[0]?.payload as Row | undefined;
            if (!active || !row) return null;
            const shown = row.value ?? row.projected;
            const closed = row.date !== "";
            return (
              <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                <span className="text-muted-foreground">
                  {closed ? displayShortDate(row.date) : `${displayShortDate(new Date(row.time))} · projeção`}
                </span>
                <span className="font-mono font-semibold">{shown !== undefined ? Math.round(shown) : "?"}%</span>
                {closed && selection === ALL_GROUPS && (
                  <span className="text-muted-foreground">
                    {verdictCountsSentence(verdictCounts(approval, row.date))}
                  </span>
                )}
              </div>
            );
          }}
        />
        <Line
          dataKey="value"
          type="linear"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={{ r: 2.5, fill: "var(--primary)" }}
          isAnimationActive={false}
          connectNulls={false}
        />
        <Line
          dataKey="projected"
          type="linear"
          stroke="var(--primary)"
          strokeOpacity={0.45}
          strokeWidth={2}
          strokeDasharray="3 4"
          dot={false}
          activeDot={false}
          isAnimationActive={false}
        />
        {lastProjected && nearTarget && (
          <ReferenceLine
            segment={[
              { x: nearTarget.time, y: series.target },
              { x: lastProjected.time, y: series.target },
            ]}
            stroke="var(--foreground)"
            strokeWidth={2}
            label={{
              value: `rumo ao alvo ${series.target}%`,
              position: "top",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--muted-foreground)",
            }}
          />
        )}
        {first && first.value !== undefined && (
          <ReferenceDot
            x={first.time}
            y={first.value}
            r={3.5}
            fill="var(--card)"
            stroke="var(--primary)"
            strokeWidth={2}
            label={{
              value: `posse: ${first.value}%`,
              position: "top",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--foreground)",
            }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
