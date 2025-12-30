"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useState } from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { formatDate, formatMoney, formatMonthYear } from "@/shared/lib/utils/formatting";
import type { PatrimonialHistory } from "@/types";

interface PortfolioLineChartProps {
  data: PatrimonialHistory[];
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4 min-w-[200px]">
      <p className="font-semibold mb-2 text-sm text-foreground">{formatDate(new Date(label))}</p>
      <div className="space-y-1.5">
        {payload.map((entry: any) => (
          <div key={entry.dataKey} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-sm text-muted-foreground">{entry.name}</span>
            </div>
            <span className="text-sm font-semibold text-foreground">{formatMoney(entry.value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function PortfolioLineChart({ data }: PortfolioLineChartProps) {
  const [visible, setVisible] = useState<Record<string, boolean>>({
    total_networth: true,
    total_equity: false,
    total_fixed: false,
    total_cash: false,
  });

  const toggle = (key: string) => {
    setVisible((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const chartData = data.map((item) => ({
    ...item,
    timestamp: new Date(`${item.snapshot_date}T00:00:00`).getTime(),
  }));

  if (!data.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evolução do Patrimônio</CardTitle>
        </CardHeader>
        <CardContent className="h-[380px] flex flex-col items-center justify-center">
          <div className="text-center space-y-2">
            <div className="text-4xl text-muted-foreground/50">📊</div>
            <p className="text-muted-foreground text-sm">Nenhum dado disponível ainda</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  function CustomLegend({ payload }: any) {
    if (!payload) return null;

    return (
      <div className="flex justify-center lg:justify-end gap-2 mb-3 flex-wrap">
        {payload.map((entry: any) => {
          const isActive = visible[entry.dataKey];
          return (
            <button
              key={entry.dataKey}
              onClick={() => toggle(entry.dataKey)}
              aria-pressed={isActive}
              aria-label={`${isActive ? "Ocultar" : "Mostrar"} ${entry.value}`}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full 
                border transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary
                ${
                  isActive
                    ? "bg-primary/10 border-primary/20 hover:bg-primary/15"
                    : "bg-muted/50 border-muted hover:bg-muted opacity-50 hover:opacity-70"
                }
              `}
            >
              <span
                className="w-3 h-3 rounded-full transition-transform duration-200"
                style={{
                  backgroundColor: isActive ? entry.color : "#9CA3AF",
                  transform: isActive ? "scale(1)" : "scale(0.85)",
                }}
              />
              <span className={`text-xs font-medium ${isActive ? "text-foreground" : "text-muted-foreground"}`}>
                {entry.value}
              </span>
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução do Patrimônio</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="h-[380px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorNetworth" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorFixed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6B7280" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#6B7280" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" strokeOpacity={0.5} />

              <XAxis
                dataKey="timestamp"
                type="number"
                scale="time"
                domain={["dataMin", "dataMax"]}
                tickFormatter={(value) => formatMonthYear(new Date(value))}
                minTickGap={40}
                stroke="#9CA3AF"
                style={{ fontSize: "12px" }}
                tickLine={{ stroke: "#e5e7eb" }}
              />

              <YAxis
                tickFormatter={formatMoney}
                width={110}
                stroke="#9CA3AF"
                style={{ fontSize: "12px" }}
                tickLine={{ stroke: "#e5e7eb" }}
              />

              <Tooltip content={<CustomTooltip />} />

              <Legend content={(props) => <CustomLegend {...props} />} />

              <Area
                type="monotone"
                dataKey="total_networth"
                name="Patrimônio Total"
                stroke="#2563eb"
                strokeWidth={2.5}
                fill="url(#colorNetworth)"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2 }}
                hide={!visible.total_networth}
                animationDuration={800}
              />

              <Area
                type="monotone"
                dataKey="total_equity"
                name="Renda Variável"
                stroke="#10B981"
                strokeWidth={2.5}
                fill="url(#colorEquity)"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2 }}
                hide={!visible.total_equity}
                animationDuration={800}
              />

              <Area
                type="monotone"
                dataKey="total_fixed"
                name="Renda Fixa"
                stroke="#F59E0B"
                strokeWidth={2.5}
                fill="url(#colorFixed)"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2 }}
                hide={!visible.total_fixed}
                animationDuration={800}
              />

              <Area
                type="monotone"
                dataKey="total_cash"
                name="Caixa"
                stroke="#6B7280"
                strokeWidth={2.5}
                fill="url(#colorCash)"
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2 }}
                hide={!visible.total_cash}
                animationDuration={800}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
