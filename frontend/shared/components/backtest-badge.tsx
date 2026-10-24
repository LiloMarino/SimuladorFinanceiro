import { FlaskConical } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";

/** O selo que marca uma simulação como backtest. */
export function BacktestBadge() {
  return (
    <Badge variant="inverse" size="tag">
      <FlaskConical />
      Backtest
    </Badge>
  );
}
