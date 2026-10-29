import { CartesianGrid, Line, LineChart, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { Budget } from "@/types";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

type PremiumCurveChartProps = { budget: Budget; height: number };

function PremiumTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: { debt: number; premium: number } }[];
}) {
  const point = payload?.[0]?.payload;
  if (!active || !point) return null;
  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <span className="flex items-center justify-between gap-6">
        <span>Dívida</span>
        <span className="font-mono font-semibold">{displayPercent(point.debt, 0)} do PIB</span>
      </span>
      <span className="flex items-center justify-between gap-6">
        <span>Prêmio</span>
        <span className="font-mono font-semibold">{displayPremiumPoints(point.premium)}</span>
      </span>
    </div>
  );
}

/** A curva do prêmio de risco pela dívida, com o ponto de hoje marcado. */
export function PremiumCurveChart({ budget, height }: PremiumCurveChartProps) {
  const curve = budget.premium_curve.map((point) => ({ debt: Number(point.debt), premium: Number(point.premium) }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={curve} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="debt"
          type="number"
          domain={[0, "dataMax"]}
          tickFormatter={(value: number) => displayPercent(value, 0)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tickFormatter={(value: number) => (value * 100).toLocaleString("pt-BR", { maximumFractionDigits: 0 })}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={28}
        />
        <Tooltip cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }} content={<PremiumTooltip />} />
        <Line dataKey="premium" stroke="var(--chart-3)" strokeWidth={2} dot={false} isAnimationActive={false} />
        <ReferenceDot
          x={Number(budget.month.debt)}
          y={Number(budget.month.premium)}
          r={4.5}
          fill="var(--chart-3)"
          stroke="var(--card)"
          strokeWidth={2}
          ifOverflow="visible"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
