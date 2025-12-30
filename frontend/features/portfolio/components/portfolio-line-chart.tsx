import { Card } from "@/shared/components/ui/card";
import { useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
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

  // Controle de visibilidade das séries: por padrão só mostramos o patrimônio total
  const [visible, setVisible] = useState<Record<string, boolean>>({
    total_networth: true,
    total_equity: false,
    total_fixed: false,
    total_cash: false,
  });

  const toggle = (key: string) => {
    setVisible((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Legenda customizável para permitir toggle das séries
  function CustomLegend({ payload }: any) {
    if (!payload) return null;

    return (
      <div className="flex justify-end gap-3 mb-2 flex-wrap">
        {payload.map((entry: any) => {
          const isActive = visible[entry.dataKey];
          return (
            <button
              key={entry.dataKey}
              onClick={() => toggle(entry.dataKey)}
              aria-pressed={isActive}
              className={`flex items-center space-x-2 px-2 py-1 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-1 ${
                isActive ? "" : "opacity-40"
              }`}
            >
              <span
                className="w-3 h-3 rounded-sm"
                style={{ background: entry.color || entry.payload?.stroke || "#000" }}
              />

              <span className="text-sm">{entry.value}</span>
            </button>
          );
        })}
      </div>
    );
  }

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

            <Legend content={(props) => <CustomLegend {...props} />} />

            <Line
              type="monotone"
              dataKey="total_networth"
              name="Patrimônio Total"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              hide={!visible.total_networth}
            />

            <Line
              type="monotone"
              dataKey="total_equity"
              name="Renda Variável"
              stroke="#10B981"
              strokeWidth={2}
              dot={false}
              hide={!visible.total_equity}
            />

            <Line
              type="monotone"
              dataKey="total_fixed"
              name="Renda Fixa"
              stroke="#F59E0B"
              strokeWidth={2}
              dot={false}
              hide={!visible.total_fixed}
            />

            <Line
              type="monotone"
              dataKey="total_cash"
              name="Caixa"
              stroke="#6B7280"
              strokeWidth={2}
              dot={false}
              hide={!visible.total_cash}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
