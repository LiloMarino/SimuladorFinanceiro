import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

type FigureCardProps = {
  label: ReactNode;
  value: string;
  note: string;
  tone?: "default" | "success" | "destructive";
};

/** O cartão de um número do bloco da mecânica: rótulo, valor em destaque e a nota que o explica. */
export function FigureCard({ label, value, note, tone = "default" }: FigureCardProps) {
  return (
    <div className="grid content-start gap-1 rounded-[10px] border p-4">
      <span className="text-[13px] font-semibold">{label}</span>
      <b
        className={cn(
          "font-mono text-[17px] font-semibold",
          tone === "success" && "text-success",
          tone === "destructive" && "text-destructive",
        )}
      >
        {value}
      </b>
      <span className="text-xs text-muted-foreground">{note}</span>
    </div>
  );
}
