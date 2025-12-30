import { Card } from "@/shared/components/ui/card";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { formatMoney } from "@/shared/lib/utils/formatting";
import { stringToColor } from "@/shared/lib/utils";
import { useState } from "react";

export type PieDataItem = {
  name: string;
  value: number;
};

interface PortfolioPieChartProps {
  title: string;
  data: PieDataItem[];
}

export function PortfolioPieChart({ title, data }: PortfolioPieChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [hiddenItems, setHiddenItems] = useState<Set<string>>(new Set());

  if (!data.length) {
    return (
      <Card className="p-6 flex flex-col">
        <h3 className="font-semibold">{title}</h3>
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Sem dados</div>
      </Card>
    );
  }

  const visibleData = data.filter((item) => !hiddenItems.has(item.name));
  const total = visibleData.reduce((sum, item) => sum + item.value, 0);

  const toggleItem = (name: string) => {
    setHiddenItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(name)) {
        newSet.delete(name);
      } else {
        if (newSet.size < data.length - 1) {
          newSet.add(name);
        }
      }
      return newSet;
    });
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0];
    const percentage = ((data.value / total) * 100).toFixed(1);

    return (
      <div className="bg-background border border-border rounded-lg shadow-lg p-3 backdrop-blur-sm">
        <p className="font-semibold text-sm mb-1">{data.name}</p>
        <p className="text-lg font-bold text-primary">{formatMoney(data.value)}</p>
        <p className="text-xs text-muted-foreground mt-1">{percentage}% do total</p>
      </div>
    );
  };

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
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="w-full lg:w-1/2 space-y-2">
          {data.map((item, index) => {
            const isHidden = hiddenItems.has(item.name);
            const percentage = ((item.value / total) * 100).toFixed(1);

            return (
              <button
                key={item.name}
                onClick={() => toggleItem(item.name)}
                onMouseEnter={() => setActiveIndex(index)}
                onMouseLeave={() => setActiveIndex(null)}
                className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all duration-200 ${
                  isHidden
                    ? "bg-muted/50 border-border opacity-50"
                    : "bg-card border-border hover:border-primary hover:shadow-sm"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: stringToColor(item.name) }}
                  />
                  <span className={`text-sm font-medium text-left ${isHidden ? "line-through" : ""}`}>{item.name}</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-sm font-semibold">{formatMoney(item.value)}</span>
                  <span className="text-xs text-muted-foreground">{percentage}%</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border flex justify-between items-center">
        <span className="text-sm text-muted-foreground">Total</span>
        <span className="text-lg font-bold">{formatMoney(total)}</span>
      </div>
    </Card>
  );
}
