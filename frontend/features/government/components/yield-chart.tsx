import { CartesianGrid, Line, LineChart, ReferenceDot, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { curveCeiling, monthlyYield, yieldCurve } from "../lib/election";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

type YieldChartProps = {
  /** Verba mensal atual do partido, em reais */
  budget: number;
  color: string | null;
};

/** A curva "quanto a verba rende": sobe rápido e achata, com um ponto na verba de hoje. */
export function YieldChart({ budget, color }: YieldChartProps) {
  const stroke = color ?? "var(--primary)";
  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={yieldCurve(curveCeiling(budget))} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="spend"
          type="number"
          domain={[0, curveCeiling(budget)]}
          tickCount={4}
          tickFormatter={(value: number) => displayMoneyCompact(value)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          width={28}
          tickCount={3}
          tickFormatter={(value: number) => value.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <Line dataKey="points" type="monotone" stroke={stroke} strokeWidth={2} dot={false} isAnimationActive={false} />
        <ReferenceDot x={budget} y={monthlyYield(budget)} r={4} fill={stroke} stroke="var(--card)" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
