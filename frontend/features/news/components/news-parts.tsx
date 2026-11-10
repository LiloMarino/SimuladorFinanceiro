import { PartyMark } from "@/shared/components/party-mark";
import { Badge } from "@/shared/components/ui/badge";
import { useElection } from "@/shared/hooks/queries/useElection";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { cn } from "@/shared/lib/utils";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { News, NewsType } from "@/types";
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
    <span className={cn("text-xs font-bold tracking-widest uppercase", SECTION_TONE[section], className)}>
      {sectionLabel(catalog, section)}
      {suffix}
    </span>
  );
}

type NewsPartiesProps = {
  abbrs: News["party_abbrs"];
};

/** Os partidos citados na manchete, cada sigla na cor do partido; sem partido citado, não busca nada. */
export function NewsParties({ abbrs }: NewsPartiesProps) {
  const { data: election } = useElection({ enabled: abbrs.length > 0 });
  if (abbrs.length === 0) return null;

  return (
    <span className="flex items-center gap-1">
      {abbrs.map((abbr) => (
        <PartyMark
          key={abbr}
          abbr={abbr}
          color={election?.parties.find((party) => party.abbr === abbr)?.color ?? null}
          size="sm"
        />
      ))}
    </span>
  );
}

type TickerChipProps = {
  ticker: string;
  held: boolean;
};

/** O ativo de uma manchete; em azul, com o aviso, quando está na carteira. */
export function TickerChip({ ticker, held }: TickerChipProps) {
  return (
    <Badge variant={held ? "info" : "secondary"}>
      {ticker}
      {held && <i className="font-normal not-italic opacity-85">· na carteira</i>}
    </Badge>
  );
}

type DayHeadingProps = {
  children: React.ReactNode;
  className?: string;
};

/** O título de um dia ou bloco do jornal, em mono maiúsculo sobre um fio escuro. */
export function DayHeading({ children, className }: DayHeadingProps) {
  return (
    <h3
      className={cn(
        "border-b border-foreground pt-4.5 pb-2 font-mono text-xs font-semibold tracking-wide text-muted-foreground uppercase",
        className,
      )}
    >
      {children}
    </h3>
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
      <b className="font-serif lining-nums text-[15px] font-bold tracking-tight">Diário do Pregão</b>
      {children ?? <span className="font-mono text-xs text-muted-foreground">{displayShortDate(date)}</span>}
    </div>
  );
}
