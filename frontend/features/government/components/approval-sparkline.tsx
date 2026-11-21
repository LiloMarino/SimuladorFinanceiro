import { Line, LineChart, ReferenceLine, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { parseLocalDate } from "@/shared/lib/utils/display";
import type { GovernmentApproval } from "@/types";

type ApprovalSparklineProps = {
  approval: Pick<GovernmentApproval, "history" | "floor">;
  height?: number;
};

/** A aprovação mês a mês sem eixos nem grade, com o piso do impeachment tracejado: o gráfico pequeno do cartão do topo. */
export function ApprovalSparkline({ approval, height = 64 }: ApprovalSparklineProps) {
  const rows = approval.history.map((point) => ({ time: parseLocalDate(point.date).getTime(), value: point.value }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
        <XAxis dataKey="time" type="number" scale="time" domain={["dataMin", "dataMax"]} hide />
        <YAxis domain={[0, 100]} hide />
        <ReferenceLine y={approval.floor} stroke="var(--destructive)" strokeDasharray="4 3" />
        <Line
          dataKey="value"
          type="linear"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
