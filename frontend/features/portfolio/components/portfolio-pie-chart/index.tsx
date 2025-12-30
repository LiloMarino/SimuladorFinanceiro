import { Card } from "@/shared/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { formatMoney } from "@/shared/lib/utils/formatting";
import { stringToColor } from "@/shared/lib/utils";
import { useState } from "react";
import { PortfolioPieTooltip } from "./chart-tooltip";
import { PortfolioPieLegend } from "./chart-legend";
import type { PieDataItem } from "./chart-legend";
import { useDynamicChartVisibility } from "../../hooks/useDynamicChartVisibility";
import { ChartEmptyCard } from "@/features/portfolio/components/shared/chart-empty-card";

interface PortfolioPieChartProps {
  title: string;
  data: PieDataItem[];
}

export function PortfolioPieChart({ title, data }: PortfolioPieChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const { hidden, visibleData, toggle } = useDynamicChartVisibility(data);

  if (!data.length) {
    return <ChartEmptyCard title={title} />;
  }

  const total = visibleData.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card className="p-6 flex flex-col">
      <h3 className="font-semibold mb-4">{title}</h3>

      <div className="flex-1 flex flex-col lg:flex-row gap-6 items-center">
        <div className="h-64 w-full lg:w-1/2 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={visibleData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={95}
                paddingAngle={2}
                animationBegin={0}
                animationDuration={800}
                onMouseEnter={(_, index) => setActiveIndex(index)}
                onMouseLeave={() => setActiveIndex(null)}
              >
                {visibleData.map((entry, index) => (
                  <Cell
                    key={entry.name}
                    fill={stringToColor(entry.name)}
                    opacity={activeIndex === null || activeIndex === index ? 1 : 0.3}
                    className="transition-opacity duration-200 cursor-pointer"
                  />
                ))}
              </Pie>
              <Tooltip content={<PortfolioPieTooltip total={total} />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <PortfolioPieLegend
          data={data}
          hiddenItems={hidden}
          toggleItem={toggle}
          setActiveIndex={setActiveIndex}
          total={total}
        />
      </div>

      <div className="mt-4 pt-4 border-t border-border flex justify-between items-center">
        <span className="text-sm text-muted-foreground">Total</span>
        <span className="text-lg font-bold">{formatMoney(total)}</span>
      </div>
    </Card>
  );
}
