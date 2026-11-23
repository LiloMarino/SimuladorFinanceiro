import { Badge } from "@/shared/components/ui/badge";
import { RecentPicker, type RecentPickerItem } from "@/shared/components/recent-picker";
import { partyColor } from "@/shared/lib/party-colors";
import { displayDayMonth, displayMonthYear } from "@/shared/lib/utils/display";
import type { TimelineYear } from "@/types";

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
      : displayMonthYear(item.opens_on);
    return `${item.year} · abre em ${opens}`;
  }
  return String(item.year);
}

/** O seletor de ano da linha do tempo; com 5 eleições ou mais, as antigas ficam numa grade atrás do "Anteriores". */
export function MapTimelineYears({ years, year, onChange }: MapTimelineYearsProps) {
  const beforeFirst = years.every((item) => item.status === "UPCOMING");
  const items: RecentPickerItem[] = years.map((item) => ({
    value: String(item.year),
    label: yearLabel(item, beforeFirst),
    shortLabel: String(item.year),
    disabled: item.status === "UPCOMING",
    cell: (
      <>
        <span className="text-sm font-semibold">{item.year}</span>
        {item.status === "CURRENT" ? (
          <Badge variant="info" size="sm">
            em curso
          </Badge>
        ) : item.winner ? (
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="size-2.5 rounded-full" style={{ backgroundColor: partyColor(item.winner) }} aria-hidden />
            {item.winner.abbr}
          </span>
        ) : null}
      </>
    ),
  }));

  return (
    <RecentPicker
      aria-label="Ano da eleição"
      items={items}
      value={String(year)}
      onChange={(value) => onChange(Number(value))}
      title={`Eleições da partida · ${years.length}`}
      noun="eleições"
      description="Cada eleição mostra quem venceu."
    />
  );
}
