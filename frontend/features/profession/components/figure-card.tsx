import type { ReactNode } from "react";
import { Check, TriangleAlert } from "lucide-react";
import { cn } from "@/shared/lib/utils";

type FigureCardProps = {
  label: ReactNode;
  value: string;
  note: string;
  /** Uma segunda nota, mais apertada, sob a primeira */
  extraNote?: string;
  /** O botão do cartão, no pé */
  action?: ReactNode;
  tone?: "default" | "success" | "destructive";
  /** Uma linha de estado sob a nota: confirma (success) ou avisa (warning) */
  flag?: { text: string; tone: "success" | "warning" };
};

/** O cartão de um número do bloco da mecânica: rótulo, valor em destaque e a nota que o explica. */
export function FigureCard({ label, value, note, extraNote, action, tone = "default", flag }: FigureCardProps) {
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
      {extraNote && <span className="mt-1 text-xs text-muted-foreground">{extraNote}</span>}
      {flag && (
        <span
          className={cn(
            "mt-1.5 flex items-start gap-1 text-xs",
            flag.tone === "success" ? "text-success" : "text-warning",
          )}
        >
          {flag.tone === "success" ? (
            <Check className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
          ) : (
            <TriangleAlert className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
          )}
          {flag.text}
        </span>
      )}
      {action && <div className="mt-2.5">{action}</div>}
    </div>
  );
}
