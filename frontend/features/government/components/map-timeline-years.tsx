import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { cn } from "@/shared/lib/utils";
import { partyColor } from "@/shared/lib/party-colors";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { TimelineYear } from "@/types";
import { monthYear } from "../lib/election";
import { visibleYears } from "../lib/map-timeline";

/** A partir deste tanto de eleições a grade do "Anteriores" passa a rolar. */
const SCROLL_FROM = 20;

type MapTimelineYearsProps = {
  years: TimelineYear[];
  year: number;
  onChange: (year: number) => void;
};

// Antes da primeira campanha o ano abre com o dia; depois, só com o mês
function yearLabel(item: TimelineYear, beforeFirst: boolean) {
  if (item.status === "CURRENT") return `${item.year} · em curso`;
  if (item.status === "UPCOMING") {
    const opens = beforeFirst
      ? `${displayDayMonth(item.opens_on)} ${item.opens_on.slice(0, 4)}`
      : monthYear(item.opens_on);
    return `${item.year} · abre em ${opens}`;
  }
  return String(item.year);
}

/** O seletor de ano da linha do tempo; com 5 eleições ou mais, as antigas ficam numa grade atrás do "Anteriores". */
export function MapTimelineYears({ years, year, onChange }: MapTimelineYearsProps) {
  const [open, setOpen] = useState(false);
  const { row, older } = visibleYears(years);
  const beforeFirst = years.every((item) => item.status === "UPCOMING");
  const chosenOlder = older.some((item) => item.year === year);

  return (
    <ToggleGroup
      variant="segmented"
      aria-label="Ano da eleição"
      data-own-arrows
      value={[chosenOlder ? "older" : String(year)]}
      onValueChange={(value) => {
        const next = Number(value[0]);
        if (Number.isInteger(next)) onChange(next);
      }}
    >
      {older.length > 0 && (
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger render={<ToggleGroupItem value="older" />}>
            {chosenOlder ? year : `Anteriores · ${older.length}`}
            <ChevronDown className="size-3.5" />
          </PopoverTrigger>
          <PopoverContent align="start" className="w-114">
            <div className="flex items-baseline justify-between">
              <PopoverTitle>Eleições da partida · {years.length}</PopoverTitle>
              <span className="text-xs text-muted-foreground">Esc fecha</span>
            </div>
            <div className={cn("grid grid-cols-4 gap-2", years.length >= SCROLL_FROM && "max-h-64 overflow-y-auto")}>
              {years.map((item) => (
                <button
                  key={item.year}
                  type="button"
                  disabled={item.status === "UPCOMING"}
                  aria-pressed={item.year === year}
                  onClick={() => {
                    onChange(item.year);
                    setOpen(false);
                  }}
                  className="flex flex-col items-start gap-1 rounded-lg border bg-card px-2.5 py-2 text-left transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50 aria-pressed:border-primary aria-pressed:bg-info-soft"
                >
                  <span className="text-sm font-semibold">{item.year}</span>
                  {item.status === "CURRENT" ? (
                    <Badge variant="info" size="sm">
                      em curso
                    </Badge>
                  ) : item.winner ? (
                    <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <span
                        className="size-2.5 rounded-full"
                        style={{ backgroundColor: partyColor(item.winner) }}
                        aria-hidden
                      />
                      {item.winner.abbr}
                    </span>
                  ) : null}
                </button>
              ))}
            </div>
            <PopoverDescription>
              Cada eleição mostra quem venceu. A partir de {SCROLL_FROM} eleições a lista rola.
            </PopoverDescription>
          </PopoverContent>
        </Popover>
      )}
      {row.map((item) => (
        <ToggleGroupItem key={item.year} value={String(item.year)} disabled={item.status === "UPCOMING"}>
          {yearLabel(item, beforeFirst)}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
