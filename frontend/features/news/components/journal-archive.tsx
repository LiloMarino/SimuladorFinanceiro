import { Button } from "@/shared/components/ui/button";
import { displayMonthShort } from "@/shared/lib/utils/display";
import { archiveMonths, type Month } from "../lib/months";
import { DayHeading } from "./news-parts";

type JournalArchiveProps = {
  startMonth: Month;
  currentMonth: Month;
  /** O mês em que a lista abre */
  selected: Month;
  onSelect: (month: Month) => void;
  onReset: () => void;
};

/** O arquivo da partida: os meses vividos, por ano; cada um reinicia a lista a partir dele. */
export function JournalArchive({ startMonth, currentMonth, selected, onSelect, onReset }: JournalArchiveProps) {
  return (
    <aside className="min-h-0 overflow-y-auto border-l border-paper-border px-6 pt-5 pb-7">
      <DayHeading className="pt-0">Arquivo da partida</DayHeading>
      <p className="mt-2.5 text-[13px] leading-[19px] text-muted-foreground">
        Cada mês abre a edição daquele mês, do dia mais novo ao mais antigo.
      </p>
      {selected !== currentMonth && (
        <Button variant="link" size="sm" className="mt-2" onClick={onReset}>
          Voltar a hoje
        </Button>
      )}
      {archiveMonths(startMonth, currentMonth).map(({ year, months }) => (
        <div key={year}>
          <h4 className="mt-3.5 mb-1.5 font-mono text-xs font-semibold">{year}</h4>
          <div className="grid grid-cols-4 gap-1.5">
            {months.map((month) => (
              <Button
                key={month}
                size="sm"
                variant={month === selected ? "dark" : "outline"}
                aria-pressed={month === selected}
                onClick={() => onSelect(month)}
              >
                {displayMonthShort(`${month}-01`)}
              </Button>
            ))}
          </div>
        </div>
      ))}
    </aside>
  );
}
