import { cn } from "@/shared/lib/utils";
import type { Pending } from "@/types";

type PendingDotProps = {
  severity: Pending["severity"];
  label: string;
};

/** O ponto do item do menu: vermelho para pendência grave, âmbar para aviso. */
export function PendingDot({ severity, label }: PendingDotProps) {
  return (
    <span
      aria-label={label}
      className={cn(
        "size-2 rounded-full ring-2 ring-sidebar",
        severity === "SEVERE" ? "bg-destructive" : "bg-toast-warning",
      )}
    />
  );
}
