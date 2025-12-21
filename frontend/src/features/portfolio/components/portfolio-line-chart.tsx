import { Card } from "@/shared/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { formatDate, formatMoney } from "@/shared/lib/utils/formatting";
import type { PatrimonialHistory } from "@/types";

interface PortfolioLineChartProps {
  data: PatrimonialHistory[];
}

export function PortfolioLineChart({ data }: PortfolioLineChartProps) {
  return (
    <Card className="p-6">
      <h3 className="font-semibold mb-4">Evolução do Patrimônio</h3>

      <div className="h-[420px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="date" tickFormatter={(date) => formatDate(date)} />

            <YAxis tickFormatter={(value) => formatMoney(value)} width={80} />

            <Tooltip formatter={(value: number) => formatMoney(value)} labelFormatter={(label) => formatDate(label)} />

            <Line type="monotone" dataKey="total_networth" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
