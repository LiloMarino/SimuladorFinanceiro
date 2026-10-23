import type { ReactNode } from "react";
import { RangeSlider, type RangeBarDrag } from "@/shared/components/ui/slider";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";
import { displayIsoDate } from "@/shared/lib/utils/display";
import {
  AXIS_MONTHS,
  AXIS_TICK_YEARS,
  axisPercent,
  axisPosition,
  bubbleLayout,
  endAtBoundary,
  startAtBoundary,
  timelineZones,
  type DataEnds,
  type DataFloor,
  type TimelineZone,
} from "../lib/period";

const ZONE_STYLES: Record<TimelineZone["kind"], string> = {
  "no-data": "bg-[repeating-linear-gradient(135deg,var(--border)_0_4px,var(--background)_4px_8px)]",
  real: "bg-real-zone",
  future: "bg-future-zone",
  repeat: "bg-[repeating-linear-gradient(135deg,var(--future-hatch)_0_4px,var(--future-soft)_4px_8px)]",
};

const LEGEND: { kind: TimelineZone["kind"]; label: string }[] = [
  { kind: "no-data", label: "Sem dado" },
  { kind: "real", label: "Dado real" },
  { kind: "future", label: "Futuro gerado" },
  { kind: "repeat", label: "Repete o último valor" },
];

const BUBBLE = "pointer-events-none absolute -top-[30px] inline-flex h-5 items-center rounded-[5px] bg-foreground px-1.5 font-mono text-[11px] whitespace-nowrap text-primary-foreground";
const TIP = "pointer-events-none absolute top-[26px] z-20 rounded-md bg-foreground px-2.5 py-1.5 text-xs font-medium whitespace-nowrap text-primary-foreground";

/** Aviso sob a linha: onde a alça parou ou o que a barra mantém ao andar. */
export type TimelineTip = { text: string; at: "start" | "end" | "bar" };

type PeriodTimelineProps = {
  /** As datas do período, como estão nos campos; só valem com `range` */
  startDate: string;
  endDate: string;
  /** Posição das duas alças em meses; nulo enquanto as datas não estão completas */
  range: [number, number] | null;
  /** O fim vem depois do início; senão as alças aparecem cruzadas e sem barra */
  ordered: boolean;
  floor: DataFloor | undefined;
  ends: DataEnds;
  today: string;
  /** A cobertura da base ainda não chegou */
  loading: boolean;
  disabled: boolean;
  tip: TimelineTip | null;
  onRangeChange: (range: [number, number]) => void;
  onBarDrag: (drag: RangeBarDrag) => void;
};

/** A linha de 1993 a 2040 pintada pelo dado que a base tem, com as duas alças e a barra do período. */
export function PeriodTimeline({
  startDate,
  endDate,
  range,
  ordered,
  floor,
  ends,
  today,
  loading,
  disabled,
  tip,
  onRangeChange,
  onBarDrag,
}: PeriodTimelineProps) {
  const zones = timelineZones(floor, ends);
  const todayPercent = axisPercent(axisPosition(today, "end"));
  const clamp = (position: number) => Math.min(Math.max(position, 0), AXIS_MONTHS);

  const marker = (
    <>
      {/* Marcador de hoje */}
      <div
        className="pointer-events-none absolute -top-1.5 -bottom-2.5 z-[1] -ml-px w-0.5 bg-foreground"
        style={{ left: `${todayPercent}%` }}
      />
      <span
        className="pointer-events-none absolute top-[30px] -translate-x-1/2 bg-subtle px-[3px] text-[11px] font-semibold"
        style={{ left: `${todayPercent}%` }}
      >
        hoje
      </span>
    </>
  );

  const zoneBands = (
    <div className="absolute inset-0 flex overflow-hidden rounded-full">
      {zones.map((zone) => (
        <div key={zone.kind} className={ZONE_STYLES[zone.kind]} style={{ width: `${zone.to - zone.from}%` }} />
      ))}
    </div>
  );

  let track: ReactNode;
  if (loading) {
    track = <Skeleton circle className="h-3.5" />;
  } else if (!range) {
    track = (
      <div className="relative h-3.5">
        {zoneBands}
        {marker}
      </div>
    );
  } else {
    const [start, end] = [clamp(range[0]), clamp(range[1])];
    const startPercent = axisPercent(start);
    const endPercent = axisPercent(end);
    const layout = bubbleLayout(startPercent, endPercent);
    const startLabel = displayIsoDate(startDate);
    const endLabel = displayIsoDate(endDate);
    track = (
      <RangeSlider
        value={[start, end]}
        onValueChange={onRangeChange}
        onBarDrag={onBarDrag}
        min={0}
        max={AXIS_MONTHS}
        step={1}
        largeStep={12}
        disabled={disabled}
        thumbLabels={["Início do período", "Fim do período"]}
        getThumbValueText={(value, index) =>
          displayIsoDate(index === 0 ? startAtBoundary(value, floor) : endAtBoundary(value))
        }
        track={zoneBands}
      >
        {marker}
        {ordered && (
          <>
            {/* Datas sobre as alças */}
            {layout === "split" || layout === "split-flipped" ? (
              <>
                <span className={cn(BUBBLE, "-translate-x-full")} style={{ left: `${startPercent}%`, marginLeft: 6 }}>
                  {startLabel}
                </span>
                <span
                  className={cn(BUBBLE, layout === "split-flipped" && "-translate-x-full")}
                  style={{ left: `${endPercent}%`, marginLeft: layout === "split-flipped" ? 6 : -6 }}
                >
                  {endLabel}
                </span>
              </>
            ) : (
              <span
                className={cn(BUBBLE, layout === "merged-end" && "-translate-x-full")}
                style={
                  layout === "merged-start"
                    ? { left: `${startPercent}%`, marginLeft: -8 }
                    : { left: `${endPercent}%`, marginLeft: 6 }
                }
              >
                {startLabel} → {endLabel}
              </span>
            )}
          </>
        )}
        {/* Aviso da parada */}
        {tip && (
          <span
            className={cn(TIP, tip.at === "bar" && "-translate-x-1/2", tip.at === "end" && "-translate-x-full")}
            style={
              tip.at === "start"
                ? { left: `${startPercent}%`, marginLeft: -8 }
                : tip.at === "end"
                  ? { left: `${endPercent}%`, marginLeft: 8 }
                  : { left: `${(startPercent + endPercent) / 2}%` }
            }
          >
            {tip.text}
          </span>
        )}
      </RangeSlider>
    );
  }

  return (
    <div className="grid gap-1 rounded-[10px] bg-subtle px-4 pt-[34px] pb-3">
      <div className="relative">{track}</div>
      {/* Anos */}
      <div className="relative mt-[22px] h-4">
        {AXIS_TICK_YEARS.map((year) => (
          <span
            key={year}
            className="absolute -translate-x-1/2 font-mono text-[10px] text-faint-foreground"
            style={{ left: `${axisPercent(axisPosition(`${year}-01-01`, "start"))}%` }}
          >
            {year}
          </span>
        ))}
      </div>
      {!range && !loading && (
        <div className="pt-0.5 text-center text-xs text-muted-foreground">Escolha um atalho ou arraste as alças na linha.</div>
      )}
      {/* Legenda */}
      <div className="mt-1.5 flex flex-wrap gap-3">
        {LEGEND.map(({ kind, label }) => (
          <span key={kind} className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={cn("size-3 shrink-0 rounded-[3px]", ZONE_STYLES[kind])} />
            {label}
          </span>
        ))}
      </div>
      <div className="mt-1 text-xs text-muted-foreground">
        Arraste as alças para mudar o início ou o fim. Arraste a barra para mover o período mantendo a duração.
      </div>
    </div>
  );
}
