import { useState } from "react";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { Calendar } from "@/shared/components/ui/calendar";
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput } from "@/shared/components/ui/input-group";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { parseLocalDate } from "@/shared/lib/utils/display";
import { dateFieldDisplay, dateFieldValue, isIsoDate, maskDate } from "@/shared/lib/utils/date-field";

type DateFieldProps = {
  id: string;
  /** ISO quando a data está completa; senão o texto em digitação */
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  invalid?: boolean;
  disabled?: boolean;
};

// O calendário cobre da série mais antiga (IBOV, 1993) até uma partida longa
const CALENDAR_START = new Date(1993, 0);
const CALENDAR_END = new Date(2040, 11);

/** Data em dd/mm/aaaa com máscara; o calendário é um atalho para escolher o dia. */
export function DateField({ id, value, onChange, onBlur, invalid, disabled }: DateFieldProps) {
  const [calendarOpen, setCalendarOpen] = useState(false);
  const selected = isIsoDate(value) ? parseLocalDate(value) : undefined;

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
              defaultMonth={selected}
              selected={selected}
              onSelect={(day) => {
                if (!day) return;
                onChange(format(day, "yyyy-MM-dd"));
                setCalendarOpen(false);
              }}
            />
          </PopoverContent>
        </Popover>
      </InputGroupAddon>
    </InputGroup>
  );
}
