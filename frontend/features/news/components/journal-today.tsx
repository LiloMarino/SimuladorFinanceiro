import { displayWeekdayDate } from "@/shared/lib/utils/display";
import type { News } from "@/types";
import { DayHeading, NewsKicker, TickerChip } from "./news-parts";

type JournalTodayProps = {
  /** O dia da partida */
  date: string;
  /** A edição do dia: a manchete principal e até três menores */
  items: News[];
  held: ReadonlySet<string>;
};

/** A edição de "Hoje": a manchete principal em corpo grande e as menores em colunas. */
export function JournalToday({ date, items, held }: JournalTodayProps) {
  const [lead, ...others] = items;
  if (!lead) return null;

  return (
    <section>
      <DayHeading className="pt-5">Hoje · {displayWeekdayDate(date)}</DayHeading>
      <article className="grid gap-2.5 border-b border-paper-border pt-4.5 pb-5">
        <div className="flex items-center gap-2.5">
          <NewsKicker type={lead.news_type} />
          {lead.tickers.map((ticker) => (
            <TickerChip key={ticker} ticker={ticker} held={held.has(ticker)} />
          ))}
        </div>
        <h4 className="font-serif lining-nums text-[34px] leading-10 font-bold tracking-[-0.01em]">{lead.headline}</h4>
        {lead.dek && <p className="max-w-170 text-base leading-6 text-secondary-foreground">{lead.dek}</p>}
      </article>

      {/* Manchetes menores */}
      {others.length > 0 && (
        <div className="grid grid-cols-3 border-b border-foreground">
          {others.map((item) => (
            <article
              key={item.id}
              className="grid min-w-0 content-start gap-1.5 py-3.5 pr-5 not-first:border-l not-first:border-paper-border not-first:pl-5"
            >
              <div className="flex min-h-5.5 items-center gap-2">
                <NewsKicker type={item.news_type} />
                <span className="ml-auto flex gap-1.5">
                  {item.tickers.map((ticker) => (
                    <TickerChip key={ticker} ticker={ticker} held={held.has(ticker)} />
                  ))}
                </span>
              </div>
              <h4 className="font-serif lining-nums text-lg leading-6 font-semibold">{item.headline}</h4>
              {item.dek && <p className="line-clamp-3 text-[13px] leading-[19px] text-muted-foreground">{item.dek}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
