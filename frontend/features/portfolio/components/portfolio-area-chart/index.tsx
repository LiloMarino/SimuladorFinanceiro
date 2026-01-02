import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { displayMoney, displayMonthYear } from "@/shared/lib/utils/display";
import type { PatrimonialHistory } from "@/types";
import { PortfolioAreaTooltip } from "./chart-tooltip";
import { useStaticChartVisibility } from "../../../../shared/hooks/useStaticChartVisibility";
import { PORTFOLIO_AREA_SERIES } from "./series";
import { PortfolioAreaLegend } from "./chart-legend";
import { ChartEmptyCard } from "@/features/portfolio/components/shared/chart-empty-card";

interface PortfolioAreaChartProps {
  data: PatrimonialHistory[];
}

export function PortfolioAreaChart({ data }: PortfolioAreaChartProps) {
  const { visible, toggle } = useStaticChartVisibility(PORTFOLIO_AREA_SERIES);

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
                {PORTFOLIO_AREA_SERIES.map((s) => (
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
                tickFormatter={(value) => displayMonthYear(new Date(value))}
                minTickGap={40}
                tick={{
                  fontSize: 13,
                  fill: "#374151",
                  fontWeight: 500,
                }}
                axisLine={{ stroke: "#374151" }}
              />

              <YAxis
                tickFormatter={displayMoney}
                width={80}
                tick={{
                  fontSize: 13,
                  fill: "#374151",
                  fontWeight: 500,
                }}
                axisLine={{ stroke: "#374151" }}
              />

              <Tooltip content={<PortfolioAreaTooltip />} />

              <Legend content={<PortfolioAreaLegend visible={visible} toggle={toggle} />} />

              {PORTFOLIO_AREA_SERIES.map((s) => (
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
