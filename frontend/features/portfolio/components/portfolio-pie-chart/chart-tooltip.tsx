import type { TooltipProps } from "recharts";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

interface PortfolioPieTooltipProps extends TooltipProps<number, string> {
  total: number;
}

export function PortfolioPieTooltip({ active, payload, total }: PortfolioPieTooltipProps) {
  if (!active || !payload || !payload.length || total === 0) return null;

  const data = payload[0] as { name?: string; value?: number };
  const value = data.value ?? 0;

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-3 backdrop-blur-sm">
      <p className="font-semibold text-sm mb-1">{data.name}</p>
      <p className="text-lg font-bold text-primary">{displayMoney(value)}</p>
      <p className="text-xs text-muted-foreground mt-1">{displayPercent(value / total)} do total</p>
    </div>
  );
}
