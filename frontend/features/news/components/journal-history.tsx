import { Button } from "@/shared/components/ui/button";
import { useLoadMoreOnVisible } from "@/shared/hooks/useLoadMoreOnVisible";
import type { News } from "@/types";
import { monthLabel, previousMonth, type Month } from "../lib/months";
import { JournalDayRows } from "./journal-day-rows";
import { JournalSkeleton } from "./journal-skeleton";

type JournalHistoryProps = {
  /** As manchetes dos dias anteriores que passaram pelo filtro */
  items: News[];
  held: ReadonlySet<string>;
  /** O mês mais antigo já carregado */
  lastMonth: Month;
  /** Quantos meses já vieram: o sentinela volta a olhar a cada mês novo */
  loadedMonths: number;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => unknown;
};

/** Os dias anteriores, com o mês seguinte carregando sozinho quando a rolagem chega ao fim da lista. */
export function JournalHistory({
  items,
  held,
  lastMonth,
  loadedMonths,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
}: JournalHistoryProps) {
  // O sentinela fica à vista enquanto o filtro esconde tudo: os meses seguintes vêm até aparecer resultado
  const sentinelRef = useLoadMoreOnVisible({
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
    pageCount: loadedMonths,
  });

  return (
    <div>
      <JournalDayRows items={items} held={held} />
      {items.length === 0 && hasNextPage && <JournalSkeleton />}
      <div ref={sentinelRef} />
      <div className="flex items-center justify-between gap-4 pt-5 pb-7">
        <span className="text-[13px] text-muted-foreground first-letter:uppercase">{monthLabel(lastMonth)}</span>
        {hasNextPage && (
          <Button variant="outline" size="sm" disabled={isFetchingNextPage} onClick={() => void fetchNextPage()}>
            <span className="first-letter:uppercase">{monthLabel(previousMonth(lastMonth))}</span> ›
          </Button>
        )}
      </div>
    </div>
  );
}
