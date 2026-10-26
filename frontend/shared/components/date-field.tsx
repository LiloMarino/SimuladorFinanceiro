import { useState } from "react";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Calendar } from "@/shared/components/ui/calendar";
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput } from "@/shared/components/ui/input-group";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { displayIsoDate, parseLocalDate } from "@/shared/lib/utils/display";
import {
  CALENDAR_END_YEAR,
  CALENDAR_START_YEAR,
  dateFieldDisplay,
  dateFieldValue,
  isIsoDate,
  maskDate,
  toIso,
  todayIso,
} from "@/shared/lib/utils/date-field";

type DateFieldProps = {
  id: string;
  /** ISO quando a data está completa; senão o texto em digitação */
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  invalid?: boolean;
  disabled?: boolean;
  /** Mostra o atalho "Hoje" dentro do campo */
  todayChip?: boolean;
  /** Até onde há dado real e futuro gerado: o calendário pinta o futuro e explica a cor */
  dataEnds?: { realEnd?: string | undefined; generatedEnd?: string | undefined };
  /** Período da partida, destacado no calendário */
  period?: { start: string; end: string } | null;
};

const CALENDAR_START = new Date(CALENDAR_START_YEAR, 0);
const CALENDAR_END = new Date(CALENDAR_END_YEAR, 11);

/** Data em dd/mm/aaaa com máscara; o calendário é um atalho para escolher o dia. */
export function DateField({
  id,
  value,
  onChange,
  onBlur,
  invalid,
  disabled,
  todayChip,
  dataEnds,
  period,
}: DateFieldProps) {
  const [calendarOpen, setCalendarOpen] = useState(false);
  const selected = isIsoDate(value) ? parseLocalDate(value) : undefined;
  const today = todayIso();
  const { realEnd, generatedEnd } = dataEnds ?? {};
  const lastDataDay = generatedEnd ?? realEnd;

  const isFuture = (day: Date) => {
    const iso = toIso(day);
    return !!realEnd && !!generatedEnd && iso > realEnd && iso <= generatedEnd;
  };
  const hasNoData = (day: Date) => !!lastDataDay && toIso(day) > lastDataDay;
  const inPeriod = (day: Date) => {
    const iso = toIso(day);
    return !!period && iso >= period.start && iso <= period.end;
  };

  const pick = (iso: string) => {
    onChange(iso);
    setCalendarOpen(false);
  };

  return (
    <InputGroup>
      <InputGroupInput
        id={id}
        inputMode="numeric"
        autoComplete="off"
        placeholder="dd/mm/aaaa"
        numeric
        value={dateFieldDisplay(value)}
        aria-invalid={invalid}
        disabled={disabled}
        onChange={(e) => onChange(dateFieldValue(maskDate(e.target.value)))}
        onBlur={onBlur}
      />
      <InputGroupAddon align="inline-end">
        {todayChip && !disabled && (
          <InputGroupButton variant="info" onClick={() => onChange(today)}>
            Hoje
          </InputGroupButton>
        )}
        <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
          <PopoverTrigger
            render={<InputGroupButton size="icon-xs" aria-label="Abrir calendário" disabled={disabled} />}
          >
            <CalendarIcon />
          </PopoverTrigger>
          <PopoverContent align="end" className="w-auto">
            <Calendar
              mode="single"
              captionLayout="dropdown"
              startMonth={CALENDAR_START}
              endMonth={CALENDAR_END}
              {...(selected ? { defaultMonth: selected, selected } : {})}
              onSelect={(day) => {
                if (day) pick(toIso(day));
              }}
              modifiers={{
                no_data: (day) => hasNoData(day) && !inPeriod(day),
                future: (day) => isFuture(day) && !inPeriod(day),
                period: (day) => inPeriod(day) && !isFuture(day),
                period_future: (day) => inPeriod(day) && isFuture(day),
                period_start: (day) => !!period && toIso(day) === period.start,
                period_end: (day) => !!period && toIso(day) === period.end,
              }}
            />
            <div className="mt-2 flex items-center justify-between border-t pt-2.5">
              <Button type="button" variant="outline" size="sm" onClick={() => pick(today)}>
                Hoje
              </Button>
              <span className="text-[11px] text-faint-foreground">{displayIsoDate(today)} · hoje</span>
            </div>
            {realEnd && (
              <div className="mt-2.5 flex flex-wrap gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1.5">
                  <span className="size-3 rounded-[3px] bg-real-range ring-1 ring-info-border ring-inset" />
                  Dado real até {displayIsoDate(realEnd)}
                </span>
                {generatedEnd && (
                  <span className="inline-flex items-center gap-1.5">
                    <span className="size-3 rounded-[3px] bg-future-soft ring-1 ring-future-border ring-inset" />
                    Futuro gerado até {displayIsoDate(generatedEnd)}
                  </span>
                )}
                <span className="inline-flex items-center gap-1.5">
                  <span className="size-3 rounded-[3px] bg-muted ring-1 ring-border ring-inset" />
                  Dias sem dado
                </span>
              </div>
            )}
          </PopoverContent>
        </Popover>
      </InputGroupAddon>
    </InputGroup>
  );
}
