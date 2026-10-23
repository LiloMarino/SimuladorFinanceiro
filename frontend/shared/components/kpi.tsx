import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

type KpiProps = {
  label: ReactNode;
  value: ReactNode;
  /** Linha de apoio embaixo do valor */
  note?: ReactNode;
  tone?: "default" | "success" | "destructive";
  className?: string;
};

/** Número de destaque: rótulo em cima, valor mono grande e uma linha de apoio. */
export function Kpi({ label, value, note, tone = "default", className }: KpiProps) {
  return (
    <div className={cn("grid content-start gap-1", className)}>
      <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">{label}</span>
      <span
        className={cn(
          "font-mono text-[22px] leading-tight font-semibold whitespace-nowrap tabular-nums",
          tone === "success" && "text-success",
          tone === "destructive" && "text-destructive",
        )}
      >
        {value}
      </span>
      {note && <span className="text-xs leading-snug text-muted-foreground">{note}</span>}
    </div>
  );
}
