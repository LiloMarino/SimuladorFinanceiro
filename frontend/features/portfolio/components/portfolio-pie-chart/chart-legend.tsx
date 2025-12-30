import { formatMoney } from "@/shared/lib/utils/formatting";
import { stringToColor } from "@/shared/lib/utils";

export type PieDataItem = {
  name: string;
  value: number;
};

interface PortfolioPieLegendProps {
  data: PieDataItem[];
  hiddenItems: Set<string>;
  toggleItem: (name: string) => void;
  setActiveIndex: (index: number | null) => void;
  total: number;
}

export function PortfolioPieLegend({ data, hiddenItems, toggleItem, setActiveIndex, total }: PortfolioPieLegendProps) {
  return (
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
  );
}
