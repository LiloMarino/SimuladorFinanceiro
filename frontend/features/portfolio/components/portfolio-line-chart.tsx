import { Card } from "@/shared/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { formatDate, formatMoney, formatMonthYear } from "@/shared/lib/utils/formatting";
import type { PatrimonialHistory } from "@/types";

interface PortfolioLineChartProps {
  data: PatrimonialHistory[];
}

export function PortfolioLineChart({ data }: PortfolioLineChartProps) {
  if (!data.length) {
    return (
      <Card className="p-6 flex flex-col">
        <h3 className="font-semibold">Evolução do Patrimônio</h3>
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Sem dados</div>
      </Card>
    );
  }

  const chartData = data.map((item) => ({
    ...item,
    timestamp: new Date(`${item.snapshot_date}T00:00:00`).getTime(),
  }));

  return (
    <Card className="p-6">
      <h3 className="font-semibold mb-4">Evolução do Patrimônio</h3>

      <div className="h-[420px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid />

            <XAxis
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(value) => formatMonthYear(new Date(value))}
              minTickGap={40}
            />

            <YAxis tickFormatter={formatMoney} width={110} />

            <Tooltip labelFormatter={(label) => formatDate(new Date(label))} formatter={formatMoney} />

            <Line
              type="monotone"
              dataKey="total_networth"
              name="Patrimônio Total"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
