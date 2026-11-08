import { displayWeekdayDate } from "@/shared/lib/utils/display";
import type { News } from "@/types";
import { groupByDay } from "../lib/filter";
import { DayHeading, NewsKicker, TickerChip } from "./news-parts";

type JournalDayRowsProps = {
  items: News[];
  held: ReadonlySet<string>;
};

/** Os dias anteriores em linhas compactas: seção, título, resumo e ativos. */
export function JournalDayRows({ items, held }: JournalDayRowsProps) {
  return (
    <>
      {groupByDay(items).map((group) => (
        <section key={group.day} data-day={group.day} className="scroll-mt-(--topbar-height)">
          <DayHeading>{displayWeekdayDate(group.day)}</DayHeading>
          {group.items.map((item) => (
            <article
              key={item.id}
              className="grid grid-cols-[96px_minmax(0,1fr)_auto] items-baseline gap-x-4 border-b border-paper-border py-2.5"
            >
              <NewsKicker type={item.news_type} />
              <h4 className="font-serif lining-nums text-base leading-5.5 font-semibold">{item.headline}</h4>
              <span className="flex gap-1.5">
                {item.tickers.map((ticker) => (
                  <TickerChip key={ticker} ticker={ticker} held={held.has(ticker)} />
                ))}
              </span>
              {item.dek && (
                <p className="col-start-2 mt-0.5 text-[13px] leading-[19px] text-muted-foreground">{item.dek}</p>
              )}
            </article>
          ))}
        </section>
      ))}
    </>
  );
}
