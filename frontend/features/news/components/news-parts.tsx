import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { cn } from "@/shared/lib/utils";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { NewsType } from "@/types";
import { SECTION_TONE, sectionLabel, sectionOf } from "../lib/catalog";

type NewsKickerProps = {
  type: NewsType;
  /** Texto depois do nome da seção, como a data */
  suffix?: string;
  className?: string;
};

/** O rótulo da seção de uma manchete, na cor dela. */
export function NewsKicker({ type, suffix, className }: NewsKickerProps) {
  const { data: catalog } = useNotificationCatalog();
  const section = catalog ? sectionOf(catalog, type) : undefined;
  if (!catalog || !section) return null;

  return (
    <span className={cn("text-[10.5px] font-bold tracking-widest uppercase", SECTION_TONE[section], className)}>
      {sectionLabel(catalog, section)}
      {suffix}
    </span>
  );
}

type NewsMastheadProps = {
  date: string;
  children?: React.ReactNode;
};

/** O título do jornal com a data da manchete, no alto do cartão e da janela. */
export function NewsMasthead({ date, children }: NewsMastheadProps) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b-[3px] border-double border-foreground px-3.5 pt-2 pb-1.5">
      <b className="font-serif text-[15px] font-bold tracking-tight">Diário do Pregão</b>
      {children ?? <span className="font-mono text-[11px] text-muted-foreground">{displayShortDate(date)}</span>}
    </div>
  );
}
