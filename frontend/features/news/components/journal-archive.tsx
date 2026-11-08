import { ArrowUp } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { displayMonthShort, displayWeekdayDate } from "@/shared/lib/utils/display";
import { archiveMonths, type Month } from "../lib/months";
import { DayHeading } from "./news-parts";

type JournalArchiveProps = {
  startMonth: Month;
  currentMonth: Month;
  /** O mês em leitura, ou o mês em que a lista abre enquanto a página está no topo */
  highlighted: Month;
  /** O dia que está na tela; nulo enquanto "Hoje" está à vista */
  readingDay: string | null;
  showBackToToday: boolean;
  onSelect: (month: Month) => void;
  onBackToToday: () => void;
};

/** O arquivo da partida: os meses vividos, por ano, com o mês em leitura destacado. Fica sob o topo da página enquanto ela rola. */
export function JournalArchive({
  startMonth,
  currentMonth,
  highlighted,
  readingDay,
  showBackToToday,
  onSelect,
  onBackToToday,
}: JournalArchiveProps) {
  return (
    <aside className="border-l border-paper-border">
      <div className="sticky top-(--topbar-height) max-h-[calc(100svh-var(--topbar-height))] overflow-y-auto px-6 pt-5 pb-7">
        <DayHeading className="pt-0">Arquivo da partida</DayHeading>
        <p className="mt-2.5 text-[13px] leading-[19px] text-muted-foreground">
          Cada mês leva à edição daquele mês, do dia mais novo ao mais antigo; o mês em leitura fica destacado.
        </p>
        {showBackToToday && (
          <Button variant="outline" size="sm" className="mt-3 w-full" onClick={onBackToToday}>
            <ArrowUp />
            Voltar para hoje
          </Button>
        )}
        {/* Dia em leitura */}
        {readingDay && (
          <p className="mt-2 font-mono text-xs text-muted-foreground">Lendo: {displayWeekdayDate(readingDay)}</p>
        )}
        {archiveMonths(startMonth, currentMonth).map(({ year, months }) => (
          <div key={year}>
            <h4 className="mt-3.5 mb-1.5 font-mono text-xs font-semibold">{year}</h4>
            <div className="grid grid-cols-4 gap-1.5">
              {months.map((month) => (
                <Button
                  key={month}
                  size="sm"
                  variant={month === highlighted ? "dark" : "outline"}
                  aria-current={month === highlighted ? "true" : undefined}
                  onClick={() => onSelect(month)}
                >
                  {displayMonthShort(`${month}-01`)}
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
