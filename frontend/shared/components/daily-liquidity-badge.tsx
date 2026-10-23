import type { ReactNode } from "react";
import { Zap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";

type DailyLiquidityBadgeProps = {
  /** O texto da etiqueta: "liquidez diária", "Qualquer dia", "Sempre disponível" */
  children: ReactNode;
  size?: "default" | "sm";
};

/** A etiqueta verde dos títulos que voltam ao caixa em qualquer pregão. */
export function DailyLiquidityBadge({ children, size = "default" }: DailyLiquidityBadgeProps) {
  return (
    <Badge variant="success" size={size}>
      <Zap />
      {children}
    </Badge>
  );
}
