import { Link } from "react-router-dom";
import { Newspaper } from "lucide-react";
import { displayDayMonth } from "@/shared/lib/utils/display";

type NewsSealProps = {
  /** A data da última manchete */
  date: string;
};

/** O cartão recolhido: um selo no canto que leva ao jornal. */
export function NewsSeal({ date }: NewsSealProps) {
  return (
    <Link
      to="/journal"
      aria-label="Abrir o jornal"
      className="flex items-center gap-2 rounded-full border border-paper-border bg-paper px-3 py-2 shadow-[0_12px_32px_rgba(15,23,41,.18)] focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <Newspaper className="size-4" />
      <b className="font-serif text-[13px]">Diário</b>
      <span className="font-mono text-[11px] text-muted-foreground">{displayDayMonth(date)}</span>
    </Link>
  );
}
