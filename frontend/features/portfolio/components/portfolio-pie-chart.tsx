import { Card } from "@/shared/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { formatMoney } from "@/shared/lib/utils/formatting";
import { stringToColor } from "@/shared/lib/utils";

export type PieDataItem = {
  name: string;
  value: number;
};

interface PortfolioPieChartProps {
  title: string;
  data: PieDataItem[];
}

export function PortfolioPieChart({ title, data }: PortfolioPieChartProps) {
  if (!data.length) {
    return (
      <Card className="p-6 flex flex-col">
        <h3 className="font-semibold">{title}</h3>
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Sem dados</div>
      </Card>
    );
  }

  return (
    <Card className="p-6 flex flex-col">
      <h3 className="font-semibold mb-4">{title}</h3>

      {/* flex-1 faz ocupar a altura restante do card */}
      <div className="flex-1 flex items-center justify-center">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
              >
                {data.map((entry) => (
                  <Cell key={entry.name} fill={stringToColor(entry.name)} />
                ))}
              </Pie>

              <Tooltip formatter={(value: number) => formatMoney(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </Card>
  );
}
