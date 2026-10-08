import type { TooltipProps } from "recharts";
import { displayDate, displayMoney } from "@/shared/lib/utils/display";
import type { PatrimonialHistory } from "@/types";
import type { PortfolioSeriesKey } from "./series";

export function PortfolioAreaTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || !payload.length) return null;

  const entries = payload as Array<{
    dataKey?: PortfolioSeriesKey;
    name?: string;
    color?: string;
    payload?: { snapshot: PatrimonialHistory };
  }>;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4 min-w-[200px]">
      <p className="font-semibold mb-2 text-sm text-foreground">{displayDate(new Date(label))}</p>

      <div className="space-y-1.5">
        {entries.map((entry) => (
          <div key={entry.dataKey} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-sm text-muted-foreground">{entry.name}</span>
            </div>

            <span className="text-sm font-semibold text-foreground">{entry.dataKey && entry.payload ? displayMoney(entry.payload.snapshot[entry.dataKey]) : "--"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
