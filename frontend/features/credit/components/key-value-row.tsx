import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

type KeyValueRowProps = {
  label: ReactNode;
  value: ReactNode;
  /** Linha do total: divisória grossa e peso maior */
  total?: boolean;
  className?: string;
};

/** Linha "rótulo ........ valor" dos resumos dos diálogos. */
export function KeyValueRow({ label, value, total = false, className }: KeyValueRowProps) {
  return (
    <div
      className={cn(
        "flex justify-between gap-3 border-t border-muted py-1.75 text-[13px] first:border-t-0",
        total && "border-t-2 border-foreground font-semibold",
        className,
      )}
    >
      <span className={total ? undefined : "text-muted-foreground"}>{label}</span>
      <span className="text-right font-mono">{value}</span>
    </div>
  );
}
