import type { TooltipProps } from "recharts";
import { formatDate, formatMoney } from "@/shared/lib/utils/formatting";

export function PortfolioLineTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload || !payload.length) return null;

  const entries = payload as Array<{
    dataKey?: string;
    name?: string;
    color?: string;
    value?: number;
  }>;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4 min-w-[200px]">
      <p className="font-semibold mb-2 text-sm text-foreground">{formatDate(new Date(label))}</p>

      <div className="space-y-1.5">
        {entries.map((entry) => (
          <div key={entry.dataKey} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-sm text-muted-foreground">{entry.name}</span>
            </div>

            <span className="text-sm font-semibold text-foreground">{formatMoney(entry.value ?? 0)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
