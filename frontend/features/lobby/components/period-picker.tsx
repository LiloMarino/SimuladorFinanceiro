import { useEffect, useRef, useState } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Field, FieldCaption, FieldError, FieldLabel, FieldTitle } from "@/shared/components/ui/field";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import type { RangeBarDrag } from "@/shared/components/ui/slider";
import { DateField } from "@/shared/components/date-field";
import { useSeriesCoverage } from "@/shared/hooks/queries/useSeriesCoverage";
import { isIsoDate, todayIso } from "@/shared/lib/utils/date-field";
import type { CoverageCheck } from "../lib/coverage";
import {
  activeShortcut,
  buildShortcuts,
  dataEnds,
  dataFloor,
  displayDuration,
  endAtBoundary,
  parsePeriod,
  periodMonths,
  periodRange,
  periodStop,
  shiftPeriod,
  startAtBoundary,
  stopMessage,
  type Period,
  type PeriodShortcut,
} from "../lib/period";
import type { SimulationFormValues } from "./lobby-match";
import { PeriodTimeline, type TimelineTip } from "./period-timeline";

type PeriodPickerProps = {
  form: UseFormReturn<SimulationFormValues>;
  /** Sem edição: convidado ou regras de uma partida salva */
  readOnly: boolean;
  /** O mesmo conferido pelo aviso de cobertura: início sem dado pinta o campo de erro */
  coverageCheck: CoverageCheck;
};

/** Início e fim da partida: atalhos, linha do tempo com alças e barra, e os campos para o dia exato. */
export function PeriodPicker({ form, readOnly, coverageCheck }: PeriodPickerProps) {
  const [startDate, endDate] = useWatch({ control: form.control, name: ["startDate", "endDate"] });
  const { data: coverage, isPending: loading } = useSeriesCoverage();
  const floor = coverage ? dataFloor(coverage) : undefined;
  const ends = coverage ? dataEnds(coverage) : { realEnd: undefined, generatedEnd: undefined };
  const today = todayIso();
  const shortcuts = buildShortcuts(today, floor);

  const bothDates = isIsoDate(startDate) && isIsoDate(endDate);
  const period = parsePeriod(startDate, endDate);
  const range = bothDates ? periodRange({ start: startDate, end: endDate }) : null;
  const active = activeShortcut(period, shortcuts);
  const startUncovered = coverageCheck.missingAtStart.length > 0;

  // A dica sob a linha vale enquanto a pessoa segura uma alça ou a barra, ou com o foco numa alça
  const [engaged, setEngaged] = useState(false);
  const [barDragging, setBarDragging] = useState(false);
  const barOrigin = useRef<Period | null>(null);

  useEffect(() => {
    const release = () => setEngaged(false);
    window.addEventListener("pointerup", release);
    window.addEventListener("pointercancel", release);
    return () => {
      window.removeEventListener("pointerup", release);
      window.removeEventListener("pointercancel", release);
    };
  }, []);

  const applyPeriod = (next: Partial<Period>) => {
    if (next.start !== undefined) {
      form.setValue("startDate", next.start, { shouldDirty: true, shouldTouch: true });
    }
    if (next.end !== undefined) {
      form.setValue("endDate", next.end, { shouldDirty: true, shouldTouch: true });
    }
    // Início e fim se validam juntos: o fim precisa vir depois do início
    void form.trigger(["startDate", "endDate"]);
  };

  // Cada alça muda só a própria ponta; a que não mexeu continua no dia que estava
  const changeRange = (next: [number, number]) => {
    if (!range) return;
    if (next[0] !== range[0]) applyPeriod({ start: startAtBoundary(next[0], floor) });
    else if (next[1] !== range[1]) applyPeriod({ end: endAtBoundary(next[1]) });
  };

  // A barra soma o mesmo deslocamento às duas pontas a partir do período em que foi pressionada
  const dragBar = ({ steps, phase }: RangeBarDrag) => {
    if (phase === "start") {
      barOrigin.current = period;
      setBarDragging(period !== null);
      return;
    }
    const origin = barOrigin.current;
    if (!origin) return;
    const moved = shiftPeriod(origin, steps, floor);
    if (moved.start !== startDate || moved.end !== endDate) applyPeriod(moved);
    if (phase === "end") {
      barOrigin.current = null;
      setBarDragging(false);
    }
  };

  const stop = period ? periodStop(period, floor) : null;
  let tip: TimelineTip | null = null;
  if (period && (engaged || barDragging)) {
    if (stop) tip = { text: stopMessage(stop, floor), at: stop === "floor" ? "start" : "end" };
    else if (barDragging) tip = { text: `Mantém ${displayDuration(periodMonths(period))}`, at: "bar" };
  }

  const shortcutGroup = (group: PeriodShortcut["group"], legend: string) => {
    const items = shortcuts.filter((s) => s.group === group);
    return (
      <div role="group" aria-label={legend} className="grid gap-1">
        <FieldCaption tone={group === "future" ? "future" : "default"}>{legend}</FieldCaption>
        <ToggleGroup
          variant="segmented"
          aria-label={legend}
          value={active?.group === group ? [active.id] : []}
          onValueChange={(values) => {
            const picked = items.find((s) => s.id === values[0]);
            if (picked) applyPeriod(picked.period);
          }}
          disabled={readOnly}
          className="w-full"
        >
          {items.map((shortcut) => {
            // "Tudo" depende da cobertura: enquanto ela não chega, o lugar fica reservado
            if (loading && shortcut.id === "past-all") {
              return <Skeleton key={shortcut.id} className="h-8 flex-1" />;
            }
            const item = (
              <ToggleGroupItem
                key={shortcut.id}
                value={shortcut.id}
                tone={group === "future" ? "future" : "neutral"}
                disabled={shortcut.blocked !== null}
                className="flex-1"
              >
                {shortcut.label}
              </ToggleGroupItem>
            );
            if (!shortcut.blocked) return item;
            return (
              <Tooltip key={shortcut.id}>
                <TooltipTrigger render={<span className="flex flex-1" />}>{item}</TooltipTrigger>
                <TooltipContent side="top">{shortcut.blocked}</TooltipContent>
              </Tooltip>
            );
          })}
        </ToggleGroup>
      </div>
    );
  };

  return (
    <div className="grid gap-3">
      {/* Cabeçalho */}
      <div className="flex items-baseline justify-between">
        <FieldTitle>Período</FieldTitle>
        {period && (
          <span className="font-mono text-xs text-muted-foreground">{displayDuration(periodMonths(period))}</span>
        )}
      </div>

      {/* Atalhos */}
      <div className="grid grid-cols-[4fr_2fr] gap-2.5">
        {shortcutGroup("past", "Até hoje")}
        {shortcutGroup("future", "Pra frente")}
      </div>

      {/* Linha do tempo */}
      <div
        onPointerDownCapture={() => setEngaged(true)}
        onFocusCapture={() => setEngaged(true)}
        onBlurCapture={() => setEngaged(false)}
      >
        <PeriodTimeline
          startDate={startDate}
          endDate={endDate}
          range={range}
          ordered={period !== null}
          floor={floor}
          ends={ends}
          today={today}
          loading={loading}
          disabled={readOnly}
          tip={tip}
          onRangeChange={changeRange}
          onBarDrag={dragBar}
        />
      </div>

      {/* Campos */}
      <div className="grid grid-cols-2 gap-3">
        {(["startDate", "endDate"] as const).map((name) => (
          <Controller
            key={name}
            control={form.control}
            name={name}
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor={`rules-${name}`}>{name === "startDate" ? "Início" : "Fim"}</FieldLabel>
                <DateField
                  id={`rules-${name}`}
                  value={field.value}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  invalid={fieldState.invalid || (name === "startDate" && startUncovered)}
                  disabled={readOnly}
                  todayChip={name === "endDate"}
                  dataEnds={ends}
                  period={period}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
        ))}
      </div>
    </div>
  );
}
