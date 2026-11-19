import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

type KeyValueRowProps = {
  label: ReactNode;
  value: ReactNode;
  /** Explicação curta sob o rótulo; com ela o rótulo ganha a cor do texto */
  note?: ReactNode;
  /** Linha do total: divisória grossa e peso maior */
  total?: boolean;
  className?: string;
  /** Ajusta o valor; o padrão é mono, para números */
  valueClassName?: string;
};

/** Linha "rótulo ........ valor" dos resumos dos diálogos. */
export function KeyValueRow({ label, value, note, total = false, className, valueClassName }: KeyValueRowProps) {
  return (
    <div
      className={cn(
        "flex justify-between gap-3 border-t border-muted py-1.75 text-[13px] first:border-t-0",
        total && "border-t-2 border-foreground font-semibold",
        className,
      )}
    >
      {note === undefined ? (
        <span className={total ? undefined : "text-muted-foreground"}>{label}</span>
      ) : (
        <span className="grid gap-0.5">
          <span>{label}</span>
          <span className="text-xs text-muted-foreground">{note}</span>
        </span>
      )}
      <span className={cn("text-right font-mono", valueClassName)}>{value}</span>
    </div>
  );
}
