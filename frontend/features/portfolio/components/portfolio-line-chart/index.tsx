import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { formatMoney, formatMonthYear } from "@/shared/lib/utils/formatting";
import type { PatrimonialHistory } from "@/types";
import { PortfolioLineTooltip } from "./chart-tooltip";
import { useStaticChartVisibility } from "../../../../shared/hooks/useStaticChartVisibility";
import { PORTFOLIO_LINE_SERIES } from "./series";
import { PortfolioLineLegend } from "./chart-legend";
import { ChartEmptyCard } from "@/features/portfolio/components/shared/chart-empty-card";

interface PortfolioLineChartProps {
  data: PatrimonialHistory[];
}

export function PortfolioLineChart({ data }: PortfolioLineChartProps) {
  const { visible, toggle } = useStaticChartVisibility(PORTFOLIO_LINE_SERIES);

  const chartData = data.map((item) => ({
    ...item,
    timestamp: new Date(`${item.snapshot_date}T00:00:00`).getTime(),
  }));

  if (!data.length) {
    return <ChartEmptyCard title="Evolução do Patrimônio" icon="📈" message="Nenhum dado disponível ainda" />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução do Patrimônio</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="h-[380px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={chartData}
              margin={{
                top: 12,
                right: 16,
              }}
            >
              <defs>
                {PORTFOLIO_LINE_SERIES.map((s) => (
                  <linearGradient key={s.gradientId} id={s.gradientId} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={s.color} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={s.color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

              <XAxis
                dataKey="timestamp"
                type="number"
                scale="time"
                domain={["dataMin", "dataMax"]}
                tickFormatter={(value) => formatMonthYear(new Date(value))}
                minTickGap={40}
                tick={{
                  fontSize: 13,
                  fill: "#374151",
                  fontWeight: 500,
                }}
                axisLine={{ stroke: "#374151" }}
              />

              <YAxis
                tickFormatter={formatMoney}
                width={80}
                tick={{
                  fontSize: 13,
                  fill: "#374151",
                  fontWeight: 500,
                }}
                axisLine={{ stroke: "#374151" }}
              />

              <Tooltip content={<PortfolioLineTooltip />} />

              <Legend content={<PortfolioLineLegend visible={visible} toggle={toggle} />} />

              {PORTFOLIO_LINE_SERIES.map((s) => (
                <Area
                  type="monotone"
                  dataKey={s.key}
                  key={s.key}
                  name={s.label}
                  stroke={s.color}
                  strokeWidth={2.5}
                  fill={`url(#${s.gradientId})`}
                  hide={!visible[s.key]}
                  dot={false}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
