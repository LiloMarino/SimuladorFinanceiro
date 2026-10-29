import { Newspaper, SearchX } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { displayWeekdayDate } from "@/shared/lib/utils/display";
import type { News } from "@/types";
import { groupByDay, type JournalFilter } from "../lib/filter";
import { NewsKicker } from "./news-parts";

type JournalEntriesProps = {
  /** As manchetes que passaram pelo filtro */
  items: News[];
  /** Quantas manchetes a partida tem, sem filtro */
  total: number;
  filter: JournalFilter;
  onClear: () => void;
  held: ReadonlySet<string>;
};

/** As manchetes agrupadas por dia, ou o motivo de a página estar vazia. */
export function JournalEntries({ items, total, filter, onClear, held }: JournalEntriesProps) {
  if (items.length === 0) {
    const filtered = filter.query.trim() !== "" || filter.section !== null || filter.onlyMine;
    return filtered ? <NoResults onClear={onClear} /> : <NoNews empty={total === 0} />;
  }

  return (
    <div className="grid">
      {groupByDay(items).map((group) => (
        <section key={group.day} className="grid gap-4 border-b border-paper-border py-5 last:border-b-0">
          <h3 className="font-mono text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            {displayWeekdayDate(group.day)}
          </h3>
          {group.items.map((item) => (
            <article key={item.id} className="grid gap-1">
              <NewsKicker type={item.news_type} />
              <h4 className="font-serif text-xl leading-snug font-semibold">{item.headline}</h4>
              {item.dek && <p className="text-sm text-muted-foreground">{item.dek}</p>}
              {item.tickers.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {item.tickers.map((ticker) => (
                    <Badge key={ticker} variant={held.has(ticker) ? "info" : "secondary"} size="sm">
                      {ticker}
                    </Badge>
                  ))}
                </div>
              )}
            </article>
          ))}
        </section>
      ))}
    </div>
  );
}

function NoNews({ empty }: { empty: boolean }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Newspaper />
        </EmptyMedia>
        <EmptyTitle>{empty ? "Nenhuma manchete ainda" : "Nenhuma manchete para mostrar"}</EmptyTitle>
        <EmptyDescription>
          {empty
            ? "As notícias da partida aparecem aqui conforme os pregões passam."
            : "Os tipos de notícia estão desligados. Dá para religá-los em Configurações."}
        </EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}

function NoResults({ onClear }: { onClear: () => void }) {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <SearchX />
        </EmptyMedia>
        <EmptyTitle>Nenhuma manchete com esse filtro</EmptyTitle>
        <EmptyDescription>Ajuste a busca, a seção ou o filtro da carteira.</EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline" onClick={onClear}>
          Limpar filtros
        </Button>
      </EmptyContent>
    </Empty>
  );
}
