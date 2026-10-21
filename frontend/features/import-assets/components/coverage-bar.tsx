import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";
import { timelineOffset, type TimelineRange } from "../lib/timeline";

type CoverageBarProps = {
  series: SeriesCoverage;
  range: TimelineRange;
};

/** Até onde vai o dado de uma série no eixo comum: real, gerado e o trecho que repete o último valor. */
export function CoverageBar({ series, range }: CoverageBarProps) {
  if (!series.start || !series.real_end) {
    return <div className="h-2.5 rounded-full bg-muted" />;
  }

  const realStart = timelineOffset(series.start, range);
  const realEnd = timelineOffset(series.real_end, range);
  const generatedEnd = series.generated_end ? timelineOffset(series.generated_end, range) : realEnd;
  const dataEnd = Math.max(realEnd, generatedEnd);

  return (
    <Tooltip>
      <TooltipTrigger render={<div />}>
        <div className="relative h-2.5 min-w-40 rounded-full bg-muted">
          {/* Dado real */}
          <span
            className="absolute inset-y-0 rounded-full bg-primary"
            style={{ left: `${realStart}%`, width: `${Math.max(realEnd - realStart, 0.5)}%` }}
          />
          {/* Dado gerado */}
          {generatedEnd > realEnd && (
            <span
              className="absolute inset-y-0 rounded-full bg-chart-3"
              style={{ left: `${realEnd}%`, width: `${generatedEnd - realEnd}%` }}
            />
          )}
          {/* Depois do fim: repete o último valor */}
          {dataEnd < 100 && (
            <span
              className="absolute inset-y-0 rounded-r-full bg-[repeating-linear-gradient(135deg,var(--chart-3)_0_3px,transparent_3px_6px)] opacity-70"
              style={{ left: `${dataEnd}%`, width: `${100 - dataEnd}%` }}
            />
          )}
        </div>
      </TooltipTrigger>
      <TooltipContent side="top">
        Real: {displayIsoDate(series.start)} → {displayIsoDate(series.real_end)}
        {series.generated_end && ` · gerado até ${displayIsoDate(series.generated_end)}`}
        {dataEnd < 100 && " · depois repete o último valor"}
      </TooltipContent>
    </Tooltip>
  );
}
