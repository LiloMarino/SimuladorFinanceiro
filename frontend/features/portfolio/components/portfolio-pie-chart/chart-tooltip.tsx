import type { TooltipProps } from "recharts";
import { displayMoney } from "@/shared/lib/utils/display";

interface PortfolioPieTooltipProps extends TooltipProps<number, string> {
  total: number;
}

export function PortfolioPieTooltip({ active, payload, total }: PortfolioPieTooltipProps) {
  if (!active || !payload || !payload.length || total === 0) return null;

  const data = payload[0] as { name?: string; value?: number };
  const percentage = ((data.value! / total) * 100).toFixed(1);

  return (
    <div className="bg-background border border-border rounded-lg shadow-lg p-3 backdrop-blur-sm">
      <p className="font-semibold text-sm mb-1">{data.name}</p>
      <p className="text-lg font-bold text-primary">{displayMoney(data.value ?? 0)}</p>
      <p className="text-xs text-muted-foreground mt-1">{percentage}% do total</p>
    </div>
  );
}
