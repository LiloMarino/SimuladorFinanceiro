import { Activity, Layers } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import type { StrategyGroup } from "@/types";

/** O ícone do grupo da estratégia, no quadrado que abre cada item das listas de estratégias. */
export function StrategyGroupIcon({ group }: { group: StrategyGroup }) {
  const Icon = group === "reference" ? Layers : Activity;
  return (
    <span
      className={cn(
        "row-span-2 flex size-9 items-center justify-center rounded-[9px]",
        group === "reference" ? "bg-muted text-secondary-foreground" : "bg-info-soft text-primary",
      )}
    >
      <Icon className="size-[18px]" />
    </span>
  );
}
