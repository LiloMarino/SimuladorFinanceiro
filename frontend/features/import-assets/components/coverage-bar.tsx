import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

export type TimelineRange = { start: number; end: number };

type CoverageBarProps = {
  series: SeriesCoverage;
  range: TimelineRange;
};

// Posição de uma data na linha do tempo comum a todas as séries, em %
function offset(isoDate: string, range: TimelineRange): number {
  const span = range.end - range.start || 1;
  return ((parseLocalDate(isoDate).getTime() - range.start) / span) * 100;
}

export function CoverageBar({ series, range }: CoverageBarProps) {
  if (!series.start || !series.real_end) {
    return <div className="h-2 rounded-full bg-muted" />;
  }

  const realStart = offset(series.start, range);
  const realEnd = offset(series.real_end, range);
  const generatedEnd = series.generated_end ? offset(series.generated_end, range) : realEnd;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="relative h-2 min-w-40 rounded-full bg-muted">
          {/* Trecho real */}
          <div
            className="absolute inset-y-0 rounded-full bg-chart-1"
            style={{ left: `${realStart}%`, width: `${Math.max(realEnd - realStart, 0.5)}%` }}
          />
          {/* Trecho gerado */}
          {series.generated_end && (
            <div
              className="absolute inset-y-0 rounded-full bg-chart-3"
              style={{ left: `${realEnd}%`, width: `${generatedEnd - realEnd}%` }}
            />
          )}
        </div>
      </TooltipTrigger>
      <TooltipContent side="top">
        Dado real de {displayDate(parseLocalDate(series.start))} a {displayDate(parseLocalDate(series.real_end))}
        {series.generated_end && `; gerado até ${displayDate(parseLocalDate(series.generated_end))}`}
      </TooltipContent>
    </Tooltip>
  );
}
