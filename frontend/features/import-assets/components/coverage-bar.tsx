import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";
import { afterEnd } from "../lib/after-end";
import { timelineOffset, timelineTodayOffset, type TimelineRange } from "../lib/timeline";

type CoverageBarProps = {
  series: SeriesCoverage;
  range: TimelineRange;
};

const HATCH = "bg-[repeating-linear-gradient(135deg,var(--chart-3)_0_3px,transparent_3px_6px)] opacity-70";

const AFTER_END_TOOLTIP = {
  generated: "",
  repeat: " · depois repete o último valor",
  computed: " · depois, calculado na partida",
  none: " · sem futuro gerado",
} as const;

/** O período com dado real da série, em texto: início → último dado. */
export function CoverageDates({ series }: { series: SeriesCoverage }) {
  if (!series.start || !series.real_end) return <span className="text-xs text-faint-foreground">Sem dado</span>;
  return (
    <span className="font-mono text-xs whitespace-nowrap text-foreground">
      {displayIsoDate(series.start)} → {displayIsoDate(series.real_end)}
    </span>
  );
}

/** Até onde vai o dado de uma série no eixo comum: o real, o futuro gerado e o que a partida faz depois do fim. */
export function CoverageBar({ series, range }: CoverageBarProps) {
  if (!series.start || !series.real_end) {
    return <div className="h-2.5 rounded-full bg-muted" />;
  }

  const realStart = timelineOffset(series.start, range);
  const realEnd = timelineOffset(series.real_end, range);
  const generatedEnd = series.generated_end ? timelineOffset(series.generated_end, range) : realEnd;
  const dataEnd = Math.max(realEnd, generatedEnd);
  const after = afterEnd(series);
  const today = timelineTodayOffset(range);

  return (
    <Tooltip>
      <TooltipTrigger render={<div />}>
        <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-muted">
          {/* Dado real */}
          <span
            className="absolute inset-y-0 rounded-full bg-primary"
            style={{ left: `${realStart}%`, width: `${Math.max(realEnd - realStart, 0.5)}%` }}
          />
          {/* Futuro gerado */}
          {generatedEnd > realEnd && (
            <span
              className="absolute inset-y-0 bg-chart-3"
              style={{ left: `${realEnd}%`, width: `${generatedEnd - realEnd}%` }}
            />
          )}
          {/* Depois do fim: repete o último valor (listrado) ou é calculado na partida (verde-azulado) */}
          {(after === "repeat" || after === "computed") && dataEnd < 100 && (
            <span
              className={cn("absolute inset-y-0", after === "repeat" ? HATCH : "bg-chart-2")}
              style={{ left: `${dataEnd}%`, width: `${100 - dataEnd}%` }}
            />
          )}
          {/* Hoje */}
          <span className="absolute inset-y-0 w-0.5 bg-foreground" style={{ left: `${today}%` }} />
        </div>
      </TooltipTrigger>
      <TooltipContent side="top">
        Real: {displayIsoDate(series.start)} → {displayIsoDate(series.real_end)}
        {series.generated_end && ` · gerado até ${displayIsoDate(series.generated_end)}`}
        {AFTER_END_TOOLTIP[after]}
      </TooltipContent>
    </Tooltip>
  );
}
