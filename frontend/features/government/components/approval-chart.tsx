import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { GovernmentApproval } from "@/types";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

type ApprovalChartProps = {
  approval: GovernmentApproval;
  height?: number;
  /** Sem eixos nem grade: o gráfico pequeno do cartão do topo */
  compact?: boolean;
};

/** A aprovação mês a mês, com o piso do impeachment tracejado. */
export function ApprovalChart({ approval, height = 180, compact = false }: ApprovalChartProps) {
  const rows = approval.history.map((point) => ({ time: parseLocalDate(point.date).getTime(), value: point.value }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={compact ? { top: 4, right: 4, left: 4, bottom: 4 } : { top: 8, right: 8, left: 0, bottom: 0 }}>
        {!compact && <CartesianGrid vertical={false} stroke="var(--border)" />}
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          hide={compact}
          tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          ticks={[0, 25, 50, 75, 100]}
          hide={compact}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        <ReferenceLine y={approval.floor} stroke="var(--destructive)" strokeDasharray="4 3" />
        {!compact && (
          <Tooltip
            cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
            content={({ active, payload }) => {
              const row = payload?.[0]?.payload as (typeof rows)[number] | undefined;
              if (!active || !row) return null;
              return (
                <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                  <span className="text-muted-foreground">{displayDate(new Date(row.time))}</span>
                  <span className="font-mono font-semibold">{row.value}%</span>
                </div>
              );
            }}
          />
        )}
        <Line
          dataKey="value"
          type="linear"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={compact ? false : { r: 2.5, fill: "var(--primary)" }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
