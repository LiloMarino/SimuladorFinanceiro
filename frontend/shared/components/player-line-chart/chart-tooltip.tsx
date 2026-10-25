import type { TooltipContentProps } from "recharts";
import { displayDate } from "@/shared/lib/utils/display";
import type { ChartAxis, LineChartRow } from "./utils";

interface Props extends TooltipContentProps {
  format: (value: string) => string;
  axis: ChartAxis;
}

export function LineChartTooltip({ active, payload, label, format, axis }: Props) {
  if (!active || !payload || !payload.length || label === undefined) return null;

  const entries = payload as unknown as Array<{ name?: string; color?: string; payload?: LineChartRow }>;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-4 min-w-[200px]">
      <p className="font-semibold mb-2 text-sm text-foreground">
        {axis === "index" ? `${label}º pregão` : displayDate(new Date(label))}
      </p>

      <div className="space-y-1.5">
        {entries.map((entry) => {
          const value = entry.name ? entry.payload?.values[entry.name] : undefined;

          return (
            <div key={entry.name} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-sm text-muted-foreground">{entry.name}</span>
              </div>

              <span className="text-sm font-semibold text-foreground">{value ? format(value) : "--"}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
