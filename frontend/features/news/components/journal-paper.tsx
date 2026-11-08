import { useRef, useState } from "react";
import { ErrorState } from "@/shared/components/error-state";
import { Card } from "@/shared/components/ui/card";
import { useNotificationCatalog } from "@/shared/hooks/queries/useNotificationCatalog";
import { useNotificationSettings } from "@/shared/hooks/queries/useNotificationSettings";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { displayWeekdayDate } from "@/shared/lib/utils/display";
import type { News } from "@/types";
import { useNewsHistory } from "../hooks/queries/useNewsHistory";
import { useNewsMonth } from "../hooks/queries/useNewsMonth";
import { useReadingDay } from "../hooks/useReadingDay";
import { sectionOf } from "../lib/catalog";
import { filterNews, levelFor, type JournalFilter } from "../lib/filter";
import { monthOf, type Month } from "../lib/months";
import { pickToday } from "../lib/today";
import { JournalArchive } from "./journal-archive";
import { JournalEmpty } from "./journal-empty";
import { JournalFilters } from "./journal-filters";
import { JournalHistory } from "./journal-history";
import { JournalSkeleton } from "./journal-skeleton";
import { JournalToday } from "./journal-today";

const NO_FILTER: JournalFilter = { query: "", section: null, onlyMine: false };

type JournalPaperProps = {
  simulationId: number;
  startDate: string;
  currentDate: string;
};

/**
 * O jornal da partida em página de jornal: "Hoje" e a lista dos dias anteriores rolam com a página,
 * um mês por vez, e o arquivo fica fixo na lateral como navegação.
 */
export function JournalPaper({ simulationId, startDate, currentDate }: JournalPaperProps) {
  const startMonth = monthOf(startDate);
  const currentMonth = monthOf(currentDate);
  // O mês em que a lista foi reaberta pelo arquivo; sem escolha, ela abre no mês atual
  const [picked, setPicked] = useState<Month | null>(null);
  const fromMonth = picked ?? currentMonth;
  const [filter, setFilter] = useState<JournalFilter>(NO_FILTER);

  const monthNews = useNewsMonth(simulationId, currentMonth);
  const history = useNewsHistory(simulationId, startMonth, fromMonth);
  const { data: catalog, error: catalogError, refetch: refetchCatalog } = useNotificationCatalog();
  const { data: preferences, error: preferencesError, refetch: refetchPreferences } = useNotificationSettings();
  const { data: portfolio } = usePortfolio();

  const failed = monthNews.error ?? history.error ?? catalogError ?? preferencesError;
  const held = new Set((portfolio?.variable_income ?? []).map((position) => position.ticker));
  const visible = (items: News[]) =>
    catalog && preferences
      ? filterNews(items, filter, {
          sectionOf: (type) => sectionOf(catalog, type),
          levelOf: (item) =>
            levelFor(
              preferences.news[item.news_type],
              preferences.news_held_only[item.news_type] ?? false,
              item.tickers,
              held,
            ),
          held,
        })
      : [];

  const today = pickToday(visible(monthNews.data ?? []).filter((item) => item.news_date === currentDate));
  const earlier = visible(history.data?.items ?? []).filter((item) => item.news_date !== currentDate);
  const ready = Boolean(catalog && preferences && monthNews.data && history.data);
  const nothing = ready && today.length === 0 && earlier.length === 0 && !history.hasNextPage;

  // O arquivo segue o dia em leitura; no topo, destaca o mês em que a lista abre
  const paperRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);
  const reading = useReadingDay(listRef);
  const highlighted = reading ? monthOf(reading) : fromMonth;

  // Um mês já carregado na lista é alcançado rolando; um mês fora dela reabre a lista a partir dele
  const selectMonth = (month: Month) => {
    const firstDay = listRef.current?.querySelector(`[data-day^="${month}-"]`);
    if (firstDay) {
      firstDay.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    setPicked(month);
    if (reading) historyRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const backToToday = () => {
    setPicked(null);
    paperRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <Card ref={paperRef} variant="paper" size="flush" className="min-h-136 scroll-mt-(--topbar-height)">
      {/* Cabeçalho do jornal */}
      <div className="grid gap-3 border-b-[3px] border-double border-foreground px-7 pt-4 pb-3">
        <div className="grid grid-cols-[1fr_auto_1fr] items-end">
          <span className="font-mono text-xs text-muted-foreground first-letter:uppercase">
            {displayWeekdayDate(currentDate)}
          </span>
          <h2 className="font-serif lining-nums text-4xl font-bold tracking-tight">Diário do Pregão</h2>
          <span className="text-right font-mono text-xs text-muted-foreground">A partida inteira</span>
        </div>
        <JournalFilters filter={filter} onChange={setFilter} catalog={catalog} />
      </div>

      <div className="grid flex-1 grid-cols-[minmax(0,1fr)_300px]">
        {/* Hoje e lista dos dias anteriores */}
        <div ref={listRef} className="flex flex-col">
          {failed ? (
            <div className="px-7">
              <ErrorState
                title="Não deu para carregar as notícias"
                description="A partida segue normal. Tente de novo em instantes."
                error={failed}
                onRetry={() =>
                  void Promise.all([monthNews.refetch(), history.refetch(), refetchCatalog(), refetchPreferences()])
                }
              />
            </div>
          ) : (
            <>
              <div className="px-7">
                <JournalToday date={currentDate} items={today} held={held} />
              </div>
              {/* A lista nasce de novo a cada mês escolhido no arquivo */}
              <div key={fromMonth} ref={historyRef} className="scroll-mt-(--topbar-height) px-7">
                {!ready || !history.data ? (
                  <JournalSkeleton />
                ) : nothing ? (
                  <JournalEmpty
                    total={history.data.items.length}
                    filter={filter}
                    onClear={() => setFilter(NO_FILTER)}
                  />
                ) : (
                  <JournalHistory
                    items={earlier}
                    held={held}
                    lastMonth={history.data.months.at(-1) ?? fromMonth}
                    loadedMonths={history.data.months.length}
                    hasNextPage={history.hasNextPage}
                    isFetchingNextPage={history.isFetchingNextPage}
                    fetchNextPage={history.fetchNextPage}
                  />
                )}
              </div>
            </>
          )}
        </div>

        {/* Arquivo da partida */}
        <JournalArchive
          startMonth={startMonth}
          currentMonth={currentMonth}
          highlighted={highlighted}
          readingDay={reading}
          showBackToToday={reading !== null || fromMonth !== currentMonth}
          onSelect={selectMonth}
          onBackToToday={backToToday}
        />
      </div>
    </Card>
  );
}
